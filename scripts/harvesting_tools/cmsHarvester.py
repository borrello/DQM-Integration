#!/usr/bin/env python

###########################################################################
## File       : cmsHarvest.py
## Author     : Jeroen Hegeman
##              jeroen.hegeman@cern.ch
## Last change: 20090921
##
## Purpose    : Main program to run all kinds of harvesting.
##              For more information please refer to the CMS Twiki url
##              mentioned just below here.
###########################################################################

"""Main program to run all kinds of harvesting.

These are the basic kinds of harvesting implemented (contact me if
your favourite is missing):

- DQMOffline : Run for real data (could also be run for MC). Maps to
               the `dqmHarvesting' sequence.

- RelVal : Run for release validation samples. Makes heavy use of MC
           truth information. Maps to the `validationHarvesting' sequence.

- Preproduction : Run for MC preproduction samples. Maps to the
                  `validationprodHarvesting' sequence.

"""

###########################################################################

__version__ = "1.5.0"
__author__ = "Jeroen Hegeman (jeroen.hegeman@cern.ch)"

twiki_url = "https://twiki.cern.ch/twiki/bin/view/CMS/CmsHarvester"

###########################################################################

###########################################################################
## TODO list
##
## - SPECIAL (future):
##   After discussing all these harvesting issues yet again with Luca,
##   it looks like we'll need something special to handle harvesting
##   for (collisions) data in reprocessing. Stuff with a special DBS
##   instance in which `rolling' reports of reprocessed datasets is
##   publised. In this case we will have to check (w.r.t. the parent
##   dataset) how much of a given run is ready, and submit once we're
##   satisfied (let's say 90%).
##
## - We could get rid of most of the `and dataset.status = VALID'
##   pieces in the DBS queries.
## - Change to a more efficient grid scheduler.
## - Implement incremental harvesting. Requires some changes to the
##   book keeping to store the harvested number of events for each
##   run. Also requires some changes to the dataset checking to see if
##   additional statistics have become available.
## - Emphasize the warnings in case we're running in force
##   mode. Otherwise they may get lost a bit in the output.
## - Fix the creation of the CASTOR dirs. The current approach works
##   but is a) too complicated and b) too inefficient.
## - Fully implement all harvesting types.
##   --> Discuss with Andreas what exactly should be in there. And be
##       careful with the run numbers!
## - Add the (second-step) harvesting config file to the (first-step)
##   ME extraction job to make sure it does not get lost.
## - Improve sanity checks on harvesting type vs. data type.
## - Implement reference histograms.
##   1) User-specified reference dataset.
##   2) Educated guess based on dataset name.
##   3) References from GlobalTag.
##   4) No reference at all.
## - Is this options.evt_type used anywhere?
## - Combine all these dbs_resolve_xxx into a single call to DBS(?).
## - Implement CRAB server use?
## - Add implementation of email address of user. (Only necessary for
##   CRAB server.)
###########################################################################

import os
import sys
import commands
import re
import logging
import optparse
import datetime
import copy
from inspect import getargspec
from random import choice

# These we need to communicate with DBS global DBSAPI
from DBSAPI.dbsApi import DbsApi
import DBSAPI.dbsException
import DBSAPI.dbsApiException
# and these we need to parse the DBS output.
global xml
global SAXParseException
import xml.sax
from xml.sax import SAXParseException

import Configuration.PyReleaseValidation
from Configuration.PyReleaseValidation.ConfigBuilder import \
     ConfigBuilder, defaultOptions
# from Configuration.PyReleaseValidation.cmsDriverOptions import options, python_config_filename

#import FWCore.ParameterSet.Config as cms

# Debugging stuff.
import pdb

###########################################################################
## Helper class: Usage exception.
###########################################################################
class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return repr(self.msg)

    # End of Usage.

###########################################################################
## Helper class: Error exception.
###########################################################################
class Error(Exception):
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return repr(self.msg)

###########################################################################
## CMSHarvesterHelpFormatter class.
###########################################################################

class CMSHarvesterHelpFormatter(optparse.IndentedHelpFormatter):
    """Helper class to add some customised help output to cmsHarvester.

    We want to add some instructions, as well as a pointer to the CMS
    Twiki.

    """

    def format_usage(self, usage):

        usage_lines = []

        sep_line = "-" * 60
        usage_lines.append(sep_line)
        usage_lines.append("Welcome to the CMS harvester, a (hopefully useful)")
        usage_lines.append("tool to create harvesting configurations.")
        usage_lines.append("For more information please have a look at the CMS Twiki:")
        usage_lines.append("  %s" % twiki_url)
        usage_lines.append(sep_line)
        usage_lines.append("")

        # Since we only add to the output, we now just append the
        # original output from IndentedHelpFormatter.
        usage_lines.append(optparse.IndentedHelpFormatter. \
                           format_usage(self, usage))

        formatted_usage = "\n".join(usage_lines)
        return formatted_usage

    # End of CMSHarvesterHelpFormatter.

###########################################################################
## CMSHarvester class.
###########################################################################

class CMSHarvester(object):
    """Class to perform CMS harvesting.

    More documentation `obviously' to follow.

    """

    ##########

    def __init__(self, cmd_line_opts=None):
        "Initialize class and process command line options."

        self.version = __version__

        # These are the harvesting types allowed. See the head of this
        # file for more information.
        self.harvesting_types = [
            "DQMOffline",
            "RelVal",
            "preproduction"
            ]

        # These are the possible harvesting modes:
        #   - Single-step: harvesting takes place on-site in a single
        #   step. For each samples only a single ROOT file containing
        #   the harvesting results is returned.
        #   - Single-step-allow-partial: special hack to allow
        #   harvesting of partial statistics using single-step
        #   harvesting on spread-out samples.
        #   - Two-step: harvesting takes place in two steps. The first
        #   step returns a series of monitoring elenent summaries for
        #   each sample. The second step then merges these summaries
        #   locally and does the real harvesting. This second step
        #   produces the ROOT file containing the harvesting results.
        self.harvesting_modes = [
            "single-step",
            "single-step-allow-partial",
            "two-step"
            ]

        # It is possible to specify a GlobalTag that will override any
        # choices (regarding GlobalTags) made by the cmsHarvester.
        # BUG BUG BUG
        # For the moment, until I figure out a way to obtain the
        # GlobalTag with which a given data (!) dataset was created,
        # it is necessary to specify a GlobalTag for harvesting of
        # data.
        # BUG BUG BUG end
        self.globaltag = None

        # This contains information specific to each of the harvesting
        # types. Used to create the harvesting configuration.
        harvesting_info = {}

        harvesting_info["DQMOffline"] = {}
        harvesting_info["DQMOffline"]["step_string"] = "dqmHarvesting"
        harvesting_info["DQMOffline"]["beamspot"] = None
        harvesting_info["DQMOffline"]["eventcontent"] = None
        harvesting_info["DQMOffline"]["harvesting"] = "AtRunEnd"

        harvesting_info["RelVal"] = {}
        harvesting_info["RelVal"]["step_string"] = "validationHarvesting"
        harvesting_info["RelVal"]["beamspot"] = None
        harvesting_info["RelVal"]["eventcontent"] = None
        harvesting_info["RelVal"]["harvesting"] = "AtRunEnd"

        harvesting_info["preproduction"] = {}
        harvesting_info["preproduction"]["step_string"] = "validationprodHarvesting"
        harvesting_info["preproduction"]["beamspot"] = None
        harvesting_info["preproduction"]["eventcontent"] = None
        harvesting_info["preproduction"]["harvesting"] = "AtRunEnd"

        self.harvesting_info = harvesting_info

        ###

        # These are default `unused' values that will be filled in
        # depending on the command line options.

        # The type of harvesting we're doing. See
        # self.harvesting_types for allowed types.
        self.harvesting_type = None

        # The harvesting mode, popularly known as single-step
        # vs. two-step. The thing to remember at this point is that
        # single-step is only possible for samples located completely
        # at a single site (i.e. SE).
        self.harvesting_mode = None
        # BUG BUG BUG
        # Default temporarily set to two-step until we can get staged
        # jobs working with CRAB.
        self.harvesting_mode_default = "single-step"
        # BUG BUG BUG end

        # The input method: are we reading a dataset name (or regexp)
        # directly from the command line or are we reading a file
        # containing a list of dataset specifications.
        self.input_method = {}
        self.input_method["use"] = None
        self.input_method["ignore"] = None

        # The name of whatever input we're using.
        self.input_name = {}
        self.input_name["use"] = None
        self.input_name["ignore"] = None

        # If this is true, we're running in `force mode'. In this case
        # the sanity checks are performed but failure will not halt
        # everything.
        self.force_running = None

        # The base path of the output dir in CASTOR.
        self.castor_base_dir = None
        self.castor_base_dir_default = "/castor/cern.ch/" \
                                       "cms/store/temp/" \
                                       "dqm/offline/harvesting_output/"

        # The name of the file to be used for book keeping: which
        # datasets, runs, etc. we have already processed.
        self.book_keeping_file_name = None
        self.book_keeping_file_name_default = "harvesting_accounting.txt"

        # Hmmm, hard-coded prefix of the CERN CASTOR area. This is the
        # only supported CASTOR area.
        # NOTE: Make sure this one starts with a `/'.
        self.castor_prefix = "/castor/cern.ch"

        # This will become the list of datasets and runs to consider
        self.datasets_to_use = {}
        # and this will become the list of datasets and runs to skip.
        self.datasets_to_ignore = {}
        # This, in turn, will hold all book keeping information.
        self.book_keeping_information = {}

        # Cache for CMSSW version availability at different sites.
        self.sites_and_versions_cache = {}

        # Store command line options for later use.
        if cmd_line_opts is None:
            cmd_line_opts = sys.argv[1:]
        self.cmd_line_opts = cmd_line_opts

        # Set up the logger.
        log_handler = logging.StreamHandler()
        # This is the default log formatter, the debug option switches
        # on some more information.
        log_formatter = logging.Formatter("%(message)s")
        log_handler.setFormatter(log_formatter)
        logger = logging.getLogger()
        logger.name = "main"
        logger.addHandler(log_handler)
        self.logger = logger
        # The default output mode is quite verbose.
        self.set_output_level("NORMAL")

        #logger.debug("Initialized successfully")

        # End of __init__.

    ##########

    def cleanup(self):
        "Clean up after ourselves."

        # NOTE: This is the safe replacement of __del__.

        #self.logger.debug("All done -> shutting down")
        logging.shutdown()

        # End of cleanup.

    ##########

    def time_stamp(self):
        "Create a timestamp to use in the created config files."

        time_now = datetime.datetime.utcnow()
        # We don't care about the microseconds.
        time_now = time_now.replace(microsecond = 0)
        time_stamp = "%sUTC" % datetime.datetime.isoformat(time_now)

        # End of time_stamp.
        return time_stamp

    ##########

    def ident_string(self):
        "Spit out an identification string for cmsHarvester.py."

        ident_str = "`cmsHarvester.py " \
                    "version %s': cmsHarvester.py %s" % \
                    (__version__,
                     reduce(lambda x, y: x+' '+y, sys.argv[1:]))

        return ident_str

    ##########

    def format_conditions_string(self, globaltag):
        """Create the conditions string needed for `cmsDriver'.

        Just glueing the FrontierConditions bit in front of it really.

        """

        # Not very robust but okay. The idea is that if the user
        # specified (since this cannot happen with GlobalTags coming
        # from DBS) something containing `conditions', they probably
        # know what they're doing and we should not muck things up. In
        # all other cases we just assume we only received the
        # GlobalTag part and we built the usual conditions string from
        # that .
        if globaltag.lower().find("conditions") > -1:
            conditions_string = globaltag
        else:
            conditions_string = "FrontierConditions_GlobalTag,%s" % \
                                globaltag

        # End of format_conditions_string.
        return conditions_string

    ##########

    def config_file_header(self):
        "Create a nice header to be used to mark the generated files."

        tmp = []

        time_stamp = self.time_stamp()
        ident_str = self.ident_string()
        tmp.append("# %s" % time_stamp)
        tmp.append("# WARNING: This file was created automatically!")
        tmp.append("")
        tmp.append("# Created by %s" % ident_str)

        header = "\n".join(tmp)

        # End of config_file_header.
        return header

    ##########

    def set_output_level(self, output_level):
        """Adjust the level of output generated.

        Choices are:
          - normal  : default level of output
          - quiet   : less output than the default
          - verbose : some additional information
          - debug   : lots more information, may be overwhelming

        NOTE: The debug option is a bit special in the sense that it
              also modifies the output format.

        """

        # NOTE: These levels are hooked up to the ones used in the
        #       logging module.
        output_levels = {
            "NORMAL"  : logging.INFO,
            "QUIET"   : logging.WARNING,
            "VERBOSE" : logging.INFO,
            "DEBUG"   : logging.DEBUG
            }

        output_level = output_level.upper()

        try:
            # Update the logger.
            self.log_level = output_levels[output_level]
            self.logger.setLevel(self.log_level)
        except KeyError:
            # Show a complaint
            self.logger.fatal("Unknown output level `%s'" % ouput_level)
            # and re-raise an exception.
            raise Exception

        # End of set_output_level.

    ##########

    def option_handler_debug(self, option, opt_str, value, parser):
        """Switch to debug mode.

        This both increases the amount of output generated, as well as
        changes the format used (more detailed information is given).

        """

        # Switch to a more informative log formatter for debugging.
        log_formatter_debug = logging.Formatter("[%(levelname)s] " \
                                                # NOTE: funcName was
                                                # only implemented
                                                # starting with python
                                                # 2.5.
                                                #"%(funcName)s() " \
                                                #"@%(filename)s:%(lineno)d " \
                                                "%(message)s")
        # Hmmm, not very nice. This assumes there's only a single
        # handler associated with the current logger.
        log_handler = self.logger.handlers[0]
        log_handler.setFormatter(log_formatter_debug)
        self.set_output_level("DEBUG")

        # End of option_handler_debug.

    ##########

    def option_handler_quiet(self, option, opt_str, value, parser):
        "Switch to quiet mode: less verbose."

        self.set_output_level("QUIET")

        # End of option_handler_quiet.

    ##########

    def option_handler_force(self, option, opt_str, value, parser):
        """Switch on `force mode' in which case we don't brake for nobody.

        In so-called `force mode' all sanity checks are performed but
        we don't halt on failure. Of course this requires some care
        from the user.

        """

        self.logger.debug("Switching on `force mode'.")
        self.force_running = True

        # End of option_handler_force.

    ##########

    def option_handler_harvesting_type(self, option, opt_str, value, parser):
        """Set the harvesting type to be used.

        This checks that no harvesting type is already set, and sets
        the harvesting type to be used to the one specified. If a
        harvesting type is already set an exception is thrown. The
        same happens when an unknown type is specified.

        """

        # Check for (in)valid harvesting types.
        # NOTE: The matching is done in a bit of a complicated
        # way. This allows the specification of the type to be
        # case-insensitive while still ending up with the properly
        # `cased' version afterwards.
        value = value.lower()
        harvesting_types_lowered = [i.lower() for i in self.harvesting_types]
        try:
            type_index = harvesting_types_lowered.index(value)
            # If this works, we now have the index to the `properly
            # cased' version of the harvesting type.
        except ValueError:
            self.logger.fatal("Unknown harvesting type `%s'" % \
                              value)
            self.logger.fatal("  possible types are: %s" %
                              ", ".join(self.harvesting_types))
            raise Usage("Unknown harvesting type `%s'" % \
                        value)

        # Check if multiple (by definition conflicting) harvesting
        # types are being specified.
        if not self.harvesting_type is None:
            msg = "Only one harvesting type should be specified"
            self.logger.fatal(msg)
            raise Usage(msg)
        self.harvesting_type = self.harvesting_types[type_index]

        self.logger.info("Harvesting type to be used: `%s' (%s)" % \
                         (self.harvesting_type,
                          "HARVESTING:%s" % \
                          self.harvesting_info[self.harvesting_type] \
                          ["step_string"]))

        # End of option_handler_harvesting_type.

    ##########

    def option_handler_harvesting_mode(self, option, opt_str, value, parser):
        """Set the harvesting mode to be used.

        Single-step harvesting can be used for samples that are
        located completely at a single site (= SE). Otherwise use
        two-step mode.

        """

        # Check for valid mode.
        harvesting_mode = value.lower()
        if not harvesting_mode in self.harvesting_modes:
            msg = "Unknown harvesting mode `%s'" % harvesting_mode
            self.logger.fatal(msg)
            self.logger.fatal("  possible modes are: %s" % \
                              ", ".join(self.harvesting_modes))
            raise Usage(msg)

        # Check if we've been given only a single mode, otherwise
        # complain.
        if not self.harvesting_mode is None:
            msg = "Only one harvesting mode should be specified"
            self.logger.fatal(msg)
            raise Usage(msg)
        self.harvesting_mode = harvesting_mode

        self.logger.info("Harvesting mode to be used: `%s'" % \
                         self.harvesting_mode)

        # End of option_handler_harvesting_mode.

    ##########

    def option_handler_globaltag(self, option, opt_str, value, parser):
        """Set the GlobalTag to be used, overriding our own choices.

        By default the cmsHarvester will use the GlobalTag with which
        a given dataset was created also for the harvesting. The
        --globaltag option is the way to override this behaviour.

        """

        # Make sure that this flag only occurred once.
        if not self.globaltag is None:
            msg = "Only one GlobalTag should be specified"
            self.logger.fatal(msg)
            raise Usage(msg)
        self.globaltag = value

        self.logger.info("GlobalTag to be used: `%s'" % \
                         self.globaltag)

        # End of option_handler_globaltag.

    ##########

    def option_handler_input_spec(self, option, opt_str, value, parser):
        """TODO TODO TODO
        Document this...

        """

        # Figure out if we were called for the `use these datasets' or
        # the `ignore these datasets' case.
        if opt_str.lower().find("ignore") > -1:
            spec_type = "ignore"
        else:
            spec_type = "use"

        if not self.input_method[spec_type] is None:
            msg = "Please only specify one input method " \
                  "(for the `%s' case)" % spec_type
            self.logger.fatal(msg)
            raise Usage(msg)

        input_method = opt_str.replace("-","").replace("ignore", "")
        self.input_method[spec_type] = input_method
        self.input_name[spec_type] = value

        self.logger.debug("Input method for the `%s' case: %s" % \
                          (spec_type, input_method))

        # End of option_handler_input_spec.

    ##########

    def option_handler_book_keeping_file(self, option, opt_str, value, parser):
        """Store the name of the file to be used for book keeping.

        The only check done here is that only a single book keeping
        file is specified.

        """

        file_name = value

        if not self.book_keeping_file_name is None:
            msg = "Only one book keeping file should be specified"
            self.logger.fatal(msg)
            raise Usage(msg)
        self.book_keeping_file_name = file_name

        self.logger.info("Book keeping file to be used: `%s'" % \
                         self.book_keeping_file_name)

        # End of option_handler_book_keeping_file.

    ##########

    # OBSOLETE OBSOLETE OBSOLETE

##    def option_handler_dataset_name(self, option, opt_str, value, parser):
##        """Specify the name(s) of the dataset(s) to be processed.

##        It is checked to make sure that no dataset name or listfile
##        names are given yet. If all is well (i.e. we still have a
##        clean slate) the dataset name is stored for later use,
##        otherwise a Usage exception is raised.

##        """

##        if not self.input_method is None:
##            if self.input_method == "dataset":
##                raise Usage("Please only feed me one dataset specification")
##            elif self.input_method == "listfile":
##                raise Usage("Cannot specify both dataset and input list file")
##            else:
##                assert False, "Unknown input method `%s'" % self.input_method
##        self.input_method = "dataset"
##        self.input_name = value
##        self.logger.info("Input method used: %s" % self.input_method)

##        # End of option_handler_dataset_name.

##    ##########

##    def option_handler_listfile_name(self, option, opt_str, value, parser):
##        """Specify the input list file containing datasets to be processed.

##        It is checked to make sure that no dataset name or listfile
##        names are given yet. If all is well (i.e. we still have a
##        clean slate) the listfile name is stored for later use,
##        otherwise a Usage exception is raised.

##        """

##        if not self.input_method is None:
##            if self.input_method == "listfile":
##                raise Usage("Please only feed me one list file")
##            elif self.input_method == "dataset":
##                raise Usage("Cannot specify both dataset and input list file")
##            else:
##                assert False, "Unknown input method `%s'" % self.input_method
##        self.input_method = "listfile"
##        self.input_name = value
##        self.logger.info("Input method used: %s" % self.input_method)

##        # End of option_handler_listfile_name.

    # OBSOLETE OBSOLETE OBSOLETE end

    ##########

    def option_handler_castor_dir(self, option, opt_str, value, parser):
        """Specify where on CASTOR the output should go.

        At the moment only output to CERN CASTOR is
        supported. Eventually the harvested results should go into the
        central place for DQM on CASTOR anyway.

        """

        # Check format of specified CASTOR area.
        castor_dir = value
        #castor_dir = castor_dir.lstrip(os.path.sep)
        castor_prefix = self.castor_prefix

        # Add a leading slash if necessary and clean up the path.
        castor_dir = os.path.join(os.path.sep, castor_dir)
        self.castor_base_dir = os.path.normpath(castor_dir)

        self.logger.info("CASTOR (base) area to be used: `%s'" % \
                         self.castor_base_dir)

        # End of option_handler_castor_dir.

    ##########

    def create_castor_path_name_common(self, dataset_name):
        """Build the common part of the output path to be used on
        CASTOR.

        This consists of the CASTOR area base path specified by the
        user and a piece depending on the data type (data vs. MC), the
        harvesting type and the dataset name followed by a piece
        containing the run number and event count. (See comments in
        create_castor_path_name_special for details.) This method
        creates the common part, without run number and event count.

        """

        castor_path = self.castor_base_dir

        ###

        # The data type: data vs. mc.
        datatype = self.datasets_information[dataset_name]["datatype"]
        datatype = datatype.lower()
        castor_path = os.path.join(castor_path, datatype)

        # The harvesting type.
        harvesting_type = self.harvesting_type
        harvesting_type = harvesting_type.lower()
        castor_path = os.path.join(castor_path, harvesting_type)

        # The CMSSW release version (only the `digits'). Note that the
        # CMSSW version used here is the version used for harvesting,
        # not the one from the dataset. This does make the results
        # slightly harder to find. On the other hand it solves
        # problems in case one re-harvests a given dataset with a
        # different CMSSW version, which would lead to ambiguous path
        # names. (Of course for many cases the harvesting is done with
        # the same CMSSW version the dataset was created with.)
        release_version = self.cmssw_version
        release_version = release_version.lower(). \
                          replace("cmssw", ""). \
                          strip("_")
        castor_path = os.path.join(castor_path, release_version)

        # The dataset name.
        dataset_name_escaped = self.escape_dataset_name(dataset_name)
        castor_path = os.path.join(castor_path, dataset_name_escaped)

        ###

        castor_path = os.path.normpath(castor_path)

        # End of create_castor_path_name_common.
        return castor_path

    ##########

    def create_castor_path_name_special(self,
                                        dataset_name, run_number,
                                        castor_path_common):
        """Create the specialised part of the CASTOR output dir name.

        NOTE: To avoid clashes with `incremental harvesting'
        (re-harvesting when a dataset grows) we have to include the
        event count in the path name. The underlying `problem' is that
        CRAB does not overwrite existing output files so if the output
        file already exists CRAB will fail to copy back the output.

        NOTE: It's not possible to create different kinds of
        harvesting jobs in a single call to this tool. However, in
        principle it could be possible to create both data and MC jobs
        in a single go.

        """

        castor_path = castor_path_common

        ###

        # The run number part.
        castor_path = os.path.join(castor_path, "run_%d" % run_number)

        ###

        # The event count (i.e. the number of events we currently see
        # for this dataset).
        nevents = self.datasets_information[dataset_name] \
                  ["num_events"][run_number]
        castor_path = os.path.join(castor_path, "nevents_%d" % nevents)

        ###

        castor_path = os.path.normpath(castor_path)

        # End of create_castor_path_name_special.
        return castor_path

    ##########

    def create_and_check_castor_dirs(self):
        """Make sure all required CASTOR output dirs exist.

        This checks the CASTOR base dir specified by the user as well
        as all the subdirs required by the current set of jobs.

        """

        self.logger.info("Checking (and if necessary creating) CASTOR " \
                         "output area(s)...")

        # Call the real checker method for the base dir.
        self.create_and_check_castor_dir(self.castor_base_dir)

        # Now call the checker for all (unique) subdirs.
        castor_dirs = []
        for (dataset_name, runs) in self.datasets_to_use.iteritems():
            for run in runs:
                castor_dirs.append(self.datasets_information[dataset_name] \
                                   ["castor_path"][run])
        castor_dirs_unique = list(set(castor_dirs))
        castor_dirs_unique.sort()
        # This can take some time. E.g. CRAFT08 has > 300 runs, each
        # of which will get a new directory. So we show some (rough)
        # info in between.
        ndirs = len(castor_dirs_unique)
        step = max(ndirs / 10, 1)
        for (i, castor_dir) in enumerate(castor_dirs_unique):
            if (i + 1) % step == 0 or \
                   (i + 1) == ndirs:
                self.logger.info("  %d/%d" % \
                                 (i + 1, ndirs))
            self.create_and_check_castor_dir(castor_dir)

            # Now check if the directory is empty. If (an old version
            # of) the output file already exists CRAB will run new
            # jobs but never copy the results back. We assume the user
            # knows what they are doing and only issue a warning in
            # case the directory is not empty.
            self.logger.debug("Checking if path `%s' is empty" % \
                              castor_dir)
            cmd = "rfdir %s" % castor_dir
            (status, output) = commands.getstatusoutput(cmd)
            if status != 0:
                msg = "Could not access directory `%s'" \
                      " !!! This is bad since I should have just" \
                      " created it !!!" % castor_dir
                self.logger.fatal(msg)
                raise Error(msg)
            if len(output) > 0:
                self.logger.warning("Output directory `%s' is not empty:" \
                                    " new jobs will fail to" \
                                    " copy back output" % \
                                    castor_dir)

        # End of create_and_check_castor_dirs.

    ##########

    def create_and_check_castor_dir(self, castor_dir):
        """Check existence of the give CASTOR dir, if necessary create
        it.

        Some special care has to be taken with several things like
        setting the correct permissions such that CRAB can store the
        output results. Of course this means that things like
        /castor/cern.ch/ and user/j/ have to be recognised and treated
        properly.

        NOTE: Only CERN CASTOR area (/castor/cern.ch/) supported for
        the moment.

        NOTE: This method uses some slightly tricky caching to make
        sure we don't keep over and over checking the same base paths.

        """

        ###

        # Local helper function to fully split a path into pieces.
        def split_completely(path):
            (parent_path, name) = os.path.split(path)
            if name == "":
                return (parent_path, )
            else:
                return split_completely(parent_path) + (name, )

        ###

        # Local helper function to check rfio (i.e. CASTOR)
        # directories.
        def extract_permissions(rfstat_output):
            """Parse the output from rfstat and return the
            5-digit permissions string."""

            permissions_line = [i for i in output.split("\n") \
                                if i.lower().find("protection") > -1]
            regexp = re.compile(".*\(([0123456789]{5})\).*")
            match = regexp.search(rfstat_output)
            if not match or len(match.groups()) != 1:
                msg = "Could not extract permissions " \
                      "from output: %s" % rfstat_output
                self.logger.fatal(msg)
                raise Error(msg)
            permissions = match.group(1)

            # End of extract_permissions.
            return permissions

        ###

        # These are the pieces of CASTOR directories that we do not
        # want to touch when modifying permissions.

        # NOTE: This is all a bit involved, basically driven by the
        # fact that one wants to treat the `j' directory of
        # `/castor/cern.ch/user/j/jhegeman/' specially.
        # BUG BUG BUG
        # This should be simplified, for example by comparing to the
        # CASTOR prefix or something like that.
        # BUG BUG BUG end
        castor_paths_dont_touch = {
            0: ["/", "castor", "cern.ch", "cms", "store", "user"],
            -1: ["user", "store"]
            }

        self.logger.debug("Checking CASTOR path `%s'" % castor_dir)

        ###

        # First we take the full CASTOR path apart.
        castor_path_pieces = split_completely(castor_dir)

        # Now slowly rebuild the CASTOR path and see if a) all
        # permissions are set correctly and b) the final destination
        # exists.
        path = ""
        check_sizes = castor_paths_dont_touch.keys()
        check_sizes.sort()
        len_castor_path_pieces = len(castor_path_pieces)
        for piece_index in xrange (len_castor_path_pieces):
            skip_this_path_piece = False
            piece = castor_path_pieces[piece_index]
##            self.logger.debug("Checking CASTOR path piece `%s'" % \
##                              piece)
            for check_size in check_sizes:
                # Do we need to do anything with this?
                if (piece_index + check_size) > -1:
##                    self.logger.debug("Checking `%s' against `%s'" % \
##                                      (castor_path_pieces[piece_index + check_size],
##                                       castor_paths_dont_touch[check_size]))
                    if castor_path_pieces[piece_index + check_size] in castor_paths_dont_touch[check_size]:
##                        self.logger.debug("  skipping")
                        skip_this_path_piece = True
##                    else:
##                        # Piece not in the list, fine.
##                        self.logger.debug("  accepting")
            # Add piece to the path we're building.
##            self.logger.debug("!!! Skip path piece `%s'? %s" % \
##                              (piece, str(skip_this_path_piece)))
##            self.logger.debug("Adding piece to path...")
            path = os.path.join(path, piece)
##            self.logger.debug("Path is now `%s'" % \
##                              path)

            # Hmmmm, only at this point can we do some caching. Not
            # ideal, but okay.
            try:
                if path in self.castor_path_checks_cache:
                    continue
            except AttributeError:
                # This only happens the first time around.
                self.castor_path_checks_cache = []
            self.castor_path_checks_cache.append(path)

            # Now, unless we're supposed to skip this piece of the
            # path, let's make sure it exists and set the permissions
            # correctly for use by CRAB. This means that:
            # - the final output directory should (at least) have
            #   permissions 775
            # - all directories above that should (at least) have
            #   permissions 755.

            if not skip_this_path_piece:

                # Ok, first thing: let's make sure this directory
                # exists.
                # NOTE: The nice complication is of course that the
                # usual os.path.isdir() etc. methods don't work for an
                # rfio filesystem. So we call rfstat and interpret an
                # error as meaning that the path does not exist.
                self.logger.debug("Checking if path `%s' exists" % \
                                  path)
                cmd = "rfstat %s" % path
                (status, output) = commands.getstatusoutput(cmd)
                if status != 0:
                    # Path does not exist, let's try and create it.
                    self.logger.debug("Creating path `%s'" % path)
                    cmd = "rfmkdir %s" % path
                    (status, output) = commands.getstatusoutput(cmd)
                    if status != 0:
                        msg = "Could not create directory `%s'" % path
                        self.logger.fatal(msg)
                        raise Error(msg)
                    cmd = "rfstat %s" % path
                    (status, output) = commands.getstatusoutput(cmd)
                # Now check that it looks like a directory. If I'm not
                # mistaken one can deduce this from the fact that the
                # (octal) permissions string starts with `40' (instead
                # of `100').
                permissions = extract_permissions(output)
                if not permissions.startswith("40"):
                    msg = "Path `%s' is not a directory(?)" % path
                    self.logger.fatal(msg)
                    raise Error(msg)

                # Figure out the current permissions for this
                # (partial) path.
                self.logger.debug("Checking permissions for path `%s'" % path)
                cmd = "rfstat %s" % path
                (status, output) = commands.getstatusoutput(cmd)
                if status != 0:
                    msg = "Could not obtain permissions for directory `%s'" % \
                          path
                    self.logger.fatal(msg)
                    raise Error(msg)
                # Take the last three digits of the permissions.
                permissions = extract_permissions(output)[-3:]

                # Now if necessary fix permissions.
                # NOTE: Be careful never to `downgrade' permissions.
                if piece_index == (len_castor_path_pieces - 1):
                    # This means we're looking at the final
                    # destination directory.
                    permissions_target = "775"
                else:
                    # `Only' an intermediate directory.
                    permissions_target = "755"

                # Compare permissions.
                permissions_new = []
                for (i, j) in zip(permissions, permissions_target):
                    permissions_new.append(str(max(int(i), int(j))))
                permissions_new = "".join(permissions_new)
                self.logger.debug("  current permissions: %s" % \
                                  permissions)
                self.logger.debug("  target permissions : %s" % \
                                  permissions_target)
                if permissions_new != permissions:
                    # We have to modify the permissions.
                    self.logger.debug("Changing permissions of `%s' " \
                                      "to %s (were %s)" % \
                                      (path, permissions_new, permissions))
                    cmd = "rfchmod %s %s" % (permissions_new, path)
                    (status, output) = commands.getstatusoutput(cmd)
                    if status != 0:
                        msg = "Could not change permissions for path `%s' " \
                              "to %s" % (path, permissions_new)
                        self.logger.fatal(msg)
                        raise Error(msg)

                self.logger.debug("  Permissions ok (%s)" % permissions_new)

        # End of create_and_check_castor_dir.

    ##########

    def pick_a_site(self, sites, cmssw_version):
        """Select a site from the list.

        Basically just select one randomly, but be careful not to
        submit to things like T0.

        """

        # This is the T0.
        sites_forbidden = ["caf.cern.ch"]

        for site in sites_forbidden:
            if site in sites:
                sites.remove(site)

        # Looks like we have to do some caching here, otherwise things
        # become waaaay toooo sloooooow. So that's what the
        # sites_and_versions_cache does.

        site_name = None
        while len(sites) > 0 and \
              site_name is None:

            # Just pick one.
            se_name = choice(sites)

            # But check that it hosts the CMSSW version we want.

            if self.sites_and_versions_cache.has_key(se_name) and \
                   self.sites_and_versions_cache[se_name].has_key(cmssw_version):
                if self.sites_and_versions_cache[se_name][cmssw_version]:
                    site_name = se_name
                    break
                else:
                    self.logger.debug("  --> rejecting site `%s'" % se_name)
                    sites.remove(se_name)

            else:
                self.logger.info("Checking if site `%s' " \
                                 "has CMSSW version `%s'" % \
                                 (se_name, cmssw_version))
                self.sites_and_versions_cache[se_name] = {}

                cmd = "lcg-info --list-ce " \
                      "--query 'Tag=VO-cms-%s," \
                      "CEStatus=Production," \
                      "CloseSE=%s'" % \
                      (cmssw_version, se_name)
                (status, output) = commands.getstatusoutput(cmd)
                if status != 0:
                    self.logger.error("Could not check site information " \
                                      "for site `%s'" % se_name)
                else:
                    if len(output) > 0:
                        self.sites_and_versions_cache[se_name][cmssw_version] = True
                        site_name = se_name
                        break
                    else:
                        self.sites_and_versions_cache[se_name][cmssw_version] = False
                        self.logger.debug("  --> rejecting site `%s'" % se_name)
                        sites.remove(se_name)

        if site_name is None:
            self.logger.error("  --> no matching site found")
        else:
            self.logger.debug("  --> selected site `%s'" % site_name)

        # End of pick_a_site.
        return site_name

    ##########

    def parse_cmd_line_options(self):

        # Set up the command line parser. Note that we fix up the help
        # formatter so that we can add some text pointing people to
        # the Twiki etc.
        parser = optparse.OptionParser(version="%s %s" % \
                                       ("%prog", self.version),
                                       formatter=CMSHarvesterHelpFormatter())

        self.option_parser = parser

        # The debug switch.
        parser.add_option("-d", "--debug",
                          help="Switch on debug mode",
                          action="callback",
                          callback=self.option_handler_debug)

        # The quiet switch.
        parser.add_option("-q", "--quiet",
                          help="Be less verbose",
                          action="callback",
                          callback=self.option_handler_quiet)

        # The force switch. If this switch is used sanity checks are
        # performed but failures do not lead to aborts. Use with care.
        parser.add_option("", "--force",
                          help="Force mode. Do not abort on sanity check "
                          "failures",
                          action="callback",
                          callback=self.option_handler_force)

        # Choose between the different kinds of harvesting.
        harvesting_types_tmp = ["%s = HARVESTING:%s" % \
                                (i, self.harvesting_info[i]["step_string"]) \
                                for i in self.harvesting_types]
        parser.add_option("", "--harvesting_type",
                          help="Harvesting type: %s (%s)" % \
                          (", ".join(self.harvesting_types),
                           ", ".join(harvesting_types_tmp)),
                          action="callback",
                          callback=self.option_handler_harvesting_type,
                          type="string",
                          #nargs=1,
                          #dest="self.harvesting_type",
                          metavar="HARVESTING_TYPE")

        # Choose between single-step and two-step mode.
        parser.add_option("", "--harvesting_mode",
                          help="Harvesting mode: %s (default = %s)" % \
                          (", ".join(self.harvesting_modes),
                           self.harvesting_mode_default),
                          action="callback",
                          callback=self.option_handler_harvesting_mode,
                          type="string",
                          metavar="HARVESTING_MODE")

        # Override the GlobalTag chosen by the cmsHarvester.
        parser.add_option("", "--globaltag",
                          help="GlobalTag to use. Default is the ones " \
                          "the dataset was created with for MC, for data" \
                          "a GlobalTag has to be specified.",
                          action="callback",
                          callback=self.option_handler_globaltag,
                          type="string",
                          metavar="GLOBALTAG")

        # Option to specify the name (or a regexp) of the dataset(s)
        # to be used.
        parser.add_option("", "--dataset",
                          help="Name (or regexp) of dataset(s) to process",
                          action="callback",
                          #callback=self.option_handler_dataset_name,
                          callback=self.option_handler_input_spec,
                          type="string",
                          #dest="self.input_name",
                          metavar="DATASET")

        # Option to specify the name (or a regexp) of the dataset(s)
        # to be ignored.
        parser.add_option("", "--dataset-ignore",
                          help="Name (or regexp) of dataset(s) to ignore",
                          action="callback",
                          callback=self.option_handler_input_spec,
                          type="string",
                          metavar="DATASET-IGNORE")

        # Option to specify a file containing a list of dataset names
        # (or regexps) to be used.
        parser.add_option("", "--listfile",
                          help="File containing list of dataset names " \
                          "(or regexps) to process",
                          action="callback",
                          #callback=self.option_handler_listfile_name,
                          callback=self.option_handler_input_spec,
                          type="string",
                          #dest="self.input_name",
                          metavar="LISTFILE")

        # Option to specify a file containing a list of dataset names
        # (or regexps) to be used.
        parser.add_option("", "--listfile-ignore",
                          help="File containing list of dataset names " \
                          "(or regexps) to ignore",
                          action="callback",
                          callback=self.option_handler_input_spec,
                          type="string",
                          metavar="LISTFILE-IGNORE")

        # Option to specify which file to use for the book keeping
        # information.
        parser.add_option("", "--bookkeepingfile",
                          help="File to be used to keep track " \
                          "of which datasets and runs have " \
                          "already been processed.",
                          action="callback",
                          callback=self.option_handler_book_keeping_file,
                          type="string",
                          metavar="BOOKKEEPING-FILE")

        # Specify the place in CASTOR where the output should go.
        # NOTE: Only output to CASTOR is supported for the moment,
        # since the central DQM results place is on CASTOR anyway.
        parser.add_option("", "--castordir",
                          help="Place on CASTOR to store results",
                          action="callback",
                          callback=self.option_handler_castor_dir,
                          type="string",
                          metavar="CASTORDIR")

        # If nothing was specified: tell the user how to do things the
        # next time and exit.
        # NOTE: We just use the OptParse standard way of doing this by
        #       acting as if a '--help' was specified.
        if len(self.cmd_line_opts) < 1:
            self.cmd_line_opts = ["--help"]

        # Some trickery with the options. Why? Well, since these
        # options change the output level immediately from the option
        # handlers, the results differ depending on where they are on
        # the command line. Let's just make sure they are at the
        # front.
        # NOTE: Not very efficient or sophisticated, but it works and
        # it only has to be done once anyway.
        for i in ["-d", "--debug",
                  "-q", "--quiet"]:
            if i in self.cmd_line_opts:
                self.cmd_line_opts.remove(i)
                self.cmd_line_opts.insert(0, i)

        # Everything is set up, now parse what we were given.
        parser.set_defaults()
        (self.options, self.args) = parser.parse_args(self.cmd_line_opts)

        # End of parse_cmd_line_options.

    ##########

    def check_input_status(self):
        """Check completeness and correctness of input information.

        Check that all required information has been specified and
        that, at least as far as can be easily checked, it makes
        sense.

        NOTE: This is also where any default values are applied.

        """

        self.logger.info("Checking completeness/correctness of input...")

        # BUG BUG BUG
        # While we wait for some bugs left and right to get fixed, we
        # disable two-step.
        if self.harvesting_mode == "two-step":
            msg = "--------------------\n" \
                  "  Sorry, but for the moment (well, till it works)" \
                  "  the two-step mode has been disabled.\n" \
                  "--------------------\n"
            self.logger.fatal(msg)
            raise Error(msg)
        # BUG BUG BUG end

        # We need a harvesting method to be specified
        if self.harvesting_type is None:
            msg = "Please specify a harvesting type"
            self.logger.fatal(msg)
            raise Usage(msg)
        # as well as a harvesting mode.
        if self.harvesting_mode is None:
            self.harvesting_mode = self.harvesting_mode_default
            msg = "No harvesting mode specified --> using default `%s'" % \
                  self.harvesting_mode
            self.logger.warning(msg)
            #raise Usage(msg)

        ###

        # We need an input method so we can find the dataset name(s).
        if self.input_method is None:
            msg = "Please specify an input dataset name or a list file name"
            self.logger.fatal(msg)
            raise Usage(msg)

        # DEBUG DEBUG DEBUG
        # If we get here, we should also have an input name.
        assert not self.input_name is None
        # DEBUG DEBUG DEBUG end

        ###

        # We would like to be able to store the book keeping but we
        # need to know where it should go.
        if self.book_keeping_file_name is None:
            self.book_keeping_file_name = self.book_keeping_file_name_default
            msg = "No book keeping file specified --> using default `%s'" % \
                  self.book_keeping_file_name
            self.logger.warning(msg)
            #raise Usage(msg)

        ###

        # We need to know where to put the stuff (okay, the results)
        # on CASTOR.
        if self.castor_base_dir is None:
            self.castor_base_dir = self.castor_base_dir_default
            msg = "No CASTOR area specified -> using default `%s'" % \
                  self.castor_base_dir
            self.logger.warning(msg)
            #raise Usage(msg)

        # Only the CERN CASTOR area is supported.
        if not self.castor_base_dir.startswith(self.castor_prefix):
            msg = "CASTOR area does not start with `%s'" % \
                  self.castor_prefix
            self.logger.fatal(msg)
            if self.castor_base_dir.contains("castor") and \
               not self.castor_base_dir.contains("cern.ch"):
                self.logger.fatal("Only CERN CASTOR is supported")
            raise Usage(msg)

        ###

        # TODO TODO TODO
        # This should be removed in the future, once I find out how to
        # get the config file used to create a given dataset from DBS.

        # For data we need to have a GlobalTag. (For MC we can figure
        # it out by ourselves.)
        if self.globaltag is None:
            self.logger.warning("No GlobalTag specified. This means I cannot")
            self.logger.warning("run on data, only on MC.")
            self.logger.warning("I will skip all data datasets.")

        # TODO TODO TODO end

        # End of check_input_status.

    ##########

    def check_cmssw(self):
        """Check if CMSSW is setup.

        """

        # Try to access the CMSSW_VERSION environment variable. If
        # it's something useful we consider CMSSW to be set up
        # properly. Otherwise we raise an error.
        cmssw_version = os.getenv("CMSSW_VERSION")
        if cmssw_version is None:
            self.logger.fatal("It seems CMSSW is not setup...")
            self.logger.fatal("($CMSSW_VERSION is empty)")
            raise Error("ERROR: CMSSW needs to be setup first!")

        self.cmssw_version = cmssw_version
        self.logger.info("Found CMSSW version %s properly set up" % \
                          self.cmssw_version)

        # End of check_cmsssw.
        return True

    ##########

    def check_dbs(self):
        """Check if DBS is setup.

        """

        # Try to access the DBSCMD_HOME environment variable. If this
        # looks useful we consider DBS to be set up
        # properly. Otherwise we raise an error.
        dbs_home = os.getenv("DBSCMD_HOME")
        if dbs_home is None:
            self.logger.fatal("It seems DBS is not setup...")
            self.logger.fatal("  $DBSCMD_HOME is empty")
            raise Error("ERROR: DBS needs to be setup first!")

##        # Now we try to do a very simple DBS search. If that works
##        # instead of giving us the `Unsupported API call' crap, we
##        # should be good to go.
##        # NOTE: Not ideal, I know, but it reduces the amount of
##        #       complaints I get...
##        cmd = "dbs search --query=\"find dataset where dataset = impossible\""
##        (status, output) = commands.getstatusoutput(cmd)
##        pdb.set_trace()
##        if status != 0 or \
##           output.lower().find("unsupported api call") > -1:
##            self.logger.fatal("It seems DBS is not setup...")
##            self.logger.fatal("  %s returns crap:" % cmd)
##            for line in output.split("\n"):
##                self.logger.fatal("  %s" % line)
##            raise Error("ERROR: DBS needs to be setup first!")

        self.logger.debug("Found DBS properly set up")

        # End of check_dbs.
        return True

    ##########

    def setup_dbs(self):
        """Setup the Python side of DBS.

        For more information see the DBS Python API documentation:
        https://twiki.cern.ch/twiki/bin/view/CMS/DBSApiDocumentation

        """

        try:
            args={}
            args["url"]= "http://cmsdbsprod.cern.ch/cms_dbs_prod_global/" \
                         "servlet/DBSServlet"
            api = DbsApi(args)
            self.dbs_api = api

        except DBSAPI.dbsApiException.DbsApiException, ex:
            self.logger.fatal("Caught DBS API exception %s: %s "  % \
                              (ex.getClassName(), ex.getErrorMessage()))
            if ex.getErrorCode() not in (None, ""):
                logger.debug("DBS exception error code: ", ex.getErrorCode())
            raise

        # End of setup_dbs.

    ##########

    def dbs_resolve_dataset_name(self, dataset_name):
        """Use DBS to resolve a wildcarded dataset name.

        """

        # DEBUG DEBUG DEBUG
        # If we get here DBS should have been set up already.
        assert not self.dbs_api is None
        # DEBUG DEBUG DEBUG end

        api = self.dbs_api
        dbs_query = "find dataset where dataset like %s " \
                    "and dataset.status = VALID" % \
                    dataset_name
        try:
            api_result = api.executeQuery(dbs_query)
        except DbsApiException:
            msg = "ERROR: Could not execute DBS query"
            self.logger.fatal(msg)
            raise Error(msg)

        try:
            datasets = []
            class Handler(xml.sax.handler.ContentHandler):
                def startElement(self, name, attrs):
                    if name == "result":
                        datasets.append(str(attrs["PATH"]))
            xml.sax.parseString(api_result, Handler())
        except SAXParseException:
            msg = "ERROR: Could not parse DBS server output"
            self.logger.fatal(msg)
            raise Error(msg)

        # End of dbs_resolve_dataset_name.
        return datasets

    ##########

    def dbs_resolve_cmssw_version(self, dataset_name):
        """Ask DBS for the CMSSW version used to create this dataset.

        """

        # DEBUG DEBUG DEBUG
        # If we get here DBS should have been set up already.
        assert not self.dbs_api is None
        # DEBUG DEBUG DEBUG end

        api = self.dbs_api
        dbs_query = "find algo.version where dataset = %s " \
                    "and dataset.status = VALID" % \
                    dataset_name
        try:
            api_result = api.executeQuery(dbs_query)
        except DbsApiException:
            msg = "ERROR: Could not execute DBS query"
            self.logger.fatal(msg)
            raise Error(msg)

        try:
            cmssw_version = []
            class Handler(xml.sax.handler.ContentHandler):
                def startElement(self, name, attrs):
                    if name == "result":
                        cmssw_version.append(str(attrs["APPVERSION_VERSION"]))
            xml.sax.parseString(api_result, Handler())
        except SAXParseException:
            msg = "ERROR: Could not parse DBS server output"
            self.logger.fatal(msg)
            raise Error(msg)

        # DEBUG DEBUG DEBUG
        assert len(cmssw_version) == 1
        # DEBUG DEBUG DEBUG end

        cmssw_version = cmssw_version[0]

        # End of dbs_resolve_cmssw_version.
        return cmssw_version

    ##########

##    def dbs_resolve_dataset_number_of_events(self, dataset_name):
##        """Ask DBS across how many events this dataset has been spread
##        out.

##        This is especially useful to check that we do not submit a job
##        supposed to run on a complete sample that is not contained at
##        a single site.

##        """

##        # DEBUG DEBUG DEBUG
##        # If we get here DBS should have been set up already.
##        assert not self.dbs_api is None
##        # DEBUG DEBUG DEBUG end

##        api = self.dbs_api
##        dbs_query = "find count(site) where dataset = %s " \
##                    "and dataset.status = VALID" % \
##                    dataset_name
##        try:
##            api_result = api.executeQuery(dbs_query)
##        except DbsApiException:
##            raise Error("ERROR: Could not execute DBS query")

##        try:
##            num_events = []
##            class Handler(xml.sax.handler.ContentHandler):
##                def startElement(self, name, attrs):
##                    if name == "result":
##                        num_events.append(str(attrs["COUNT_STORAGEELEMENT"]))
##            xml.sax.parseString(api_result, Handler())
##        except SAXParseException:
##            raise Error("ERROR: Could not parse DBS server output")

##        # DEBUG DEBUG DEBUG
##        assert len(num_events) == 1
##        # DEBUG DEBUG DEBUG end

##        num_events = int(num_events[0])

##        # End of dbs_resolve_dataset_number_of_events.
##        return num_events

    ##########

    def dbs_resolve_runs(self, dataset_name):
        """Ask DBS for the list of runs in a given dataset.

        # NOTE: This does not (yet?) skip/remove empty runs. There is
        # a bug in the DBS entry run.numevents (i.e. it always returns
        # zero) which should be fixed in the `next DBS release'.
        # See also:
        #   https://savannah.cern.ch/bugs/?53452
        #   https://savannah.cern.ch/bugs/?53711

        """

        # TODO TODO TODO
        # We should remove empty runs as soon as the above mentioned
        # bug is fixed.
        # TODO TODO TODO end

        # DEBUG DEBUG DEBUG
        # If we get here DBS should have been set up already.
        assert not self.dbs_api is None
        # DEBUG DEBUG DEBUG end

        api = self.dbs_api
        dbs_query = "find run where dataset = %s " \
                    "and dataset.status = VALID" % \
                    dataset_name
        try:
            api_result = api.executeQuery(dbs_query)
        except DbsApiException:
            msg = "ERROR: Could not execute DBS query"
            self.logger.fatal(msg)
            raise Error(msg)

        try:
            runs = []
            class Handler(xml.sax.handler.ContentHandler):
                def startElement(self, name, attrs):
                    if name == "result":
                        runs.append(int(attrs["RUNS_RUNNUMBER"]))
            xml.sax.parseString(api_result, Handler())
        except SAXParseException:
            msg = "ERROR: Could not parse DBS server output"
            self.logger.fatal(msg)
            raise Error(msg)

        runs.sort()

        # End of dbs_resolve_runs.
        return runs

    ##########

    def dbs_resolve_globaltag(self, dataset_name):
        """Ask DBS for the globaltag corresponding to a given dataset.

        # BUG BUG BUG
        # This does not seem to work for data datasets? E.g. for
        # /Cosmics/Commissioning08_CRAFT0831X_V1_311_ReReco_FromSuperPointing_v1/RAW-RECO
        # Probaly due to the fact that the GlobalTag changed during
        # datataking...
        BUG BUG BUG end

        """

        # DEBUG DEBUG DEBUG
        # If we get here DBS should have been set up already.
        assert not self.dbs_api is None
        # DEBUG DEBUG DEBUG end

        api = self.dbs_api
        dbs_query = "find dataset.tag where dataset = %s " \
                    "and dataset.status = VALID" % \
                    dataset_name
        try:
            api_result = api.executeQuery(dbs_query)
        except DbsApiException:
            msg = "ERROR: Could not execute DBS query"
            self.logger.fatal(msg)
            raise Error(msg)

        try:
            globaltag = []
            class Handler(xml.sax.handler.ContentHandler):
                def startElement(self, name, attrs):
                    if name == "result":
                        globaltag.append(str(attrs["PROCESSEDDATASET_GLOBALTAG"]))
            xml.sax.parseString(api_result, Handler())
        except SAXParseException:
            msg = "ERROR: Could not parse DBS server output"
            self.logger.fatal(msg)
            raise Error(msg)

        # DEBUG DEBUG DEBUG
        assert len(globaltag) == 1
        # DEBUG DEBUG DEBUG end

        globaltag = globaltag[0]

        # End of dbs_resolve_globaltag.
        return globaltag

    ##########

    def dbs_resolve_datatype(self, dataset_name):
        """Ask DBS for the the data type (data or mc) of a given
        dataset.

        """

        # DEBUG DEBUG DEBUG
        # If we get here DBS should have been set up already.
        assert not self.dbs_api is None
        # DEBUG DEBUG DEBUG end

        api = self.dbs_api
        dbs_query = "find datatype.type where dataset = %s " \
                    "and dataset.status = VALID" % \
                    dataset_name
        try:
            api_result = api.executeQuery(dbs_query)
        except DbsApiException:
            msg = "ERROR: Could not execute DBS query"
            self.logger.fatal(msg)
            raise Error(msg)

        try:
            datatype = []
            class Handler(xml.sax.handler.ContentHandler):
                def startElement(self, name, attrs):
                    if name == "result":
                        datatype.append(str(attrs["PRIMARYDSTYPE_TYPE"]))
            xml.sax.parseString(api_result, Handler())
        except SAXParseException:
            msg = "ERROR: Could not parse DBS server output"
            self.logger.fatal(msg)
            raise Error(msg)

        # DEBUG DEBUG DEBUG
        assert len(datatype) == 1
        # DEBUG DEBUG DEBUG end

        datatype = datatype[0]

        # End of dbs_resolve_datatype.
        return datatype

    ##########

    def dbs_resolve_number_of_events(self, dataset_name, run_number=None):
        """Determine the number of events in a given dataset (and run).

        Ask DBS for the number of events in a dataset. If a run number
        is specified the number of events returned is that in that run
        of that dataset. If problems occur we throw an exception.

        # BUG BUG BUG
        # Since DBS does not return the number of events correctly,
        # neither for runs nor for whole datasets, we have to work
        # around that a bit...
        # BUG BUG BUG end

        """

        # DEBUG DEBUG DEBUG
        # If we get here DBS should have been set up already.
        assert not self.dbs_api is None
        # DEBUG DEBUG DEBUG end

        api = self.dbs_api
        dbs_query = "find file.name, file.numevents where dataset = %s " \
                    "and dataset.status = VALID" % \
                    dataset_name
        if not run_number is None:
            dbs_query = dbq_query + (" and run = %d" % run_number)
        try:
            api_result = api.executeQuery(dbs_query)
        except DbsApiException:
            msg = "ERROR: Could not execute DBS query"
            self.logger.fatal(msg)
            raise Error(msg)

        try:
            files_info = {}
            class Handler(xml.sax.handler.ContentHandler):
                def startElement(self, name, attrs):
                    if name == "result":
                        file_name = str(attrs["FILES_LOGICALFILENAME"])
                        nevents = int(attrs["FILES_NUMBEROFEVENTS"])
                        files_info[file_name] = nevents
            xml.sax.parseString(api_result, Handler())
        except SAXParseException:
            msg = "ERROR: Could not parse DBS server output"
            self.logger.fatal(msg)
            raise Error(msg)

        num_events = sum(files_info.values())

        # End of dbs_resolve_number_of_events.
        return num_events

    ##########

##    def dbs_resolve_dataset_number_of_sites(self, dataset_name):
##        """Ask DBS across how many sites this dataset has been spread
##        out.

##        This is especially useful to check that we do not submit a job
##        supposed to run on a complete sample that is not contained at
##        a single site.

##        """

##        # DEBUG DEBUG DEBUG
##        # If we get here DBS should have been set up already.
##        assert not self.dbs_api is None
##        # DEBUG DEBUG DEBUG end

##        api = self.dbs_api
##        dbs_query = "find count(site) where dataset = %s " \
##                    "and dataset.status = VALID" % \
##                    dataset_name
##        try:
##            api_result = api.executeQuery(dbs_query)
##        except DbsApiException:
##            raise Error("ERROR: Could not execute DBS query")

##        try:
##            num_sites = []
##            class Handler(xml.sax.handler.ContentHandler):
##                def startElement(self, name, attrs):
##                    if name == "result":
##                        num_sites.append(str(attrs["COUNT_STORAGEELEMENT"]))
##            xml.sax.parseString(api_result, Handler())
##        except SAXParseException:
##            raise Error("ERROR: Could not parse DBS server output")

##        # DEBUG DEBUG DEBUG
##        assert len(num_sites) == 1
##        # DEBUG DEBUG DEBUG end

##        num_sites = int(num_sites[0])

##        # End of dbs_resolve_dataset_number_of_sites.
##        return num_sites

    ##########

##    def dbs_check_dataset_spread(self, dataset_name):
##        """Figure out across how many sites this dataset is spread.

##        NOTE: This is something we need to figure out per run, since
##        we want to submit harvesting jobs per run.

##        Basically three things can happen with a given dataset:
##        - the whole dataset is available on a single site,
##        - the whole dataset is available (mirrored) at multiple sites,
##        - the dataset is spread across multiple sites and there is no
##          single site containing the full dataset in one place.

##        NOTE: If all goes well, it should not be possible that
##        anything but a _full_ dataset is mirrored. So we ignore the
##        possibility in which for example one site contains the full
##        dataset and two others mirror half of it.
##        ANOTHER NOTE: According to some people this last case _could_
##        actually happen. I will not design for it, but make sure it
##        ends up as a false negative, in which case we just loose some
##        efficiency and treat the dataset (unnecessarily) as
##        spread-out.

##        We don't really care about the first two possibilities, but in
##        the third case we need to make sure to run the harvesting in
##        two-step mode.

##        This method checks with DBS which of the above cases is true
##        for the dataset name given, and returns a 1 for the first two
##        cases, and the number of sites across which the dataset is
##        spread for the third case.

##        The way in which this is done is by asking how many files each
##        site has for the dataset. In the first case there is only one
##        site, in the second case all sites should have the same number
##        of files (i.e. the total number of files in the dataset) and
##        in the third case the file counts from all sites should add up
##        to the total file count for the dataset.

##        """

##        # DEBUG DEBUG DEBUG
##        # If we get here DBS should have been set up already.
##        assert not self.dbs_api is None
##        # DEBUG DEBUG DEBUG end

##        api = self.dbs_api
##        dbs_query = "find run, run.numevents, site, file.count " \
##                    "where dataset = %s " \
##                    "and dataset.status = VALID" % \
##                    dataset_name
##        try:
##            api_result = api.executeQuery(dbs_query)
##        except DbsApiException:
##            msg = "ERROR: Could not execute DBS query"
##            self.logger.fatal(msg)
##            raise Error(msg)

##        # Index things by run number. No cross-check is done to make
##        # sure we get results for each and every run in the
##        # dataset. I'm not sure this would make sense since we'd be
##        # cross-checking DBS info with DBS info anyway. Note that we
##        # use the file count per site to see if we're dealing with an
##        # incomplete vs. a mirrored dataset.
##        sample_info = {}
##        try:
##            class Handler(xml.sax.handler.ContentHandler):
##                def startElement(self, name, attrs):
##                    if name == "result":
##                        run_number = int(attrs["RUNS_RUNNUMBER"])
##                        site_name = str(attrs["STORAGEELEMENT_SENAME"])
##                        file_count = int(attrs["COUNT_FILES"])
##                        # BUG BUG BUG
##                        # Doh! For some reason DBS never returns any other
##                        # event count than zero.
##                        event_count = int(attrs["RUNS_NUMBEROFEVENTS"])
##                        # BUG BUG BUG end
##                        info = (site_name, file_count, event_count)
##                        try:
##                            sample_info[run_number].append(info)
##                        except KeyError:
##                            sample_info[run_number] = [info]
##            xml.sax.parseString(api_result, Handler())
##        except SAXParseException:
##            msg = "ERROR: Could not parse DBS server output"
##            self.logger.fatal(msg)
##            raise Error(msg)

##        # Now translate this into a slightly more usable mapping.
##        sites = {}
##        for (run_number, site_info) in sample_info.iteritems():
##            # Quick-n-dirty trick to see if all file counts are the
##            # same.
##            unique_file_counts = set([i[1] for i in site_info])
##            if len(unique_file_counts) == 1:
##                # Okay, so this must be a mirrored dataset.
##                # We have to pick one but we have to be careful. We
##                # cannot submit to things like a T0, a T1, or CAF.
##                site_names = [self.pick_a_site([i[0] for i in site_info])]
##                nevents = [site_info[0][2]]
##            else:
##                # Looks like this is a spread-out sample.
##                site_names = [i[0] for i in site_info]
##                nevents = [i[2] for i in site_info]
##            sites[run_number] = zip(site_names, nevents)

##        self.logger.debug("Sample `%s' spread is:" % dataset_name)
##        run_numbers = sites.keys()
##        run_numbers.sort()
##        for run_number in run_numbers:
##            self.logger.debug("  run # %6d: %d sites (%s)" % \
##                              (run_number,
##                               len(sites[run_number]),
##                               ", ".join([i[0] for i in sites[run_number]])))

##        # End of dbs_check_dataset_spread.
##        return sites

##    # DEBUG DEBUG DEBUG
##    # Just kept for debugging now.
##    def dbs_check_dataset_spread_old(self, dataset_name):
##        """Figure out across how many sites this dataset is spread.

##        NOTE: This is something we need to figure out per run, since
##        we want to submit harvesting jobs per run.

##        Basically three things can happen with a given dataset:
##        - the whole dataset is available on a single site,
##        - the whole dataset is available (mirrored) at multiple sites,
##        - the dataset is spread across multiple sites and there is no
##          single site containing the full dataset in one place.

##        NOTE: If all goes well, it should not be possible that
##        anything but a _full_ dataset is mirrored. So we ignore the
##        possibility in which for example one site contains the full
##        dataset and two others mirror half of it.
##        ANOTHER NOTE: According to some people this last case _could_
##        actually happen. I will not design for it, but make sure it
##        ends up as a false negative, in which case we just loose some
##        efficiency and treat the dataset (unnecessarily) as
##        spread-out.

##        We don't really care about the first two possibilities, but in
##        the third case we need to make sure to run the harvesting in
##        two-step mode.

##        This method checks with DBS which of the above cases is true
##        for the dataset name given, and returns a 1 for the first two
##        cases, and the number of sites across which the dataset is
##        spread for the third case.

##        The way in which this is done is by asking how many files each
##        site has for the dataset. In the first case there is only one
##        site, in the second case all sites should have the same number
##        of files (i.e. the total number of files in the dataset) and
##        in the third case the file counts from all sites should add up
##        to the total file count for the dataset.

##        """

##        # DEBUG DEBUG DEBUG
##        # If we get here DBS should have been set up already.
##        assert not self.dbs_api is None
##        # DEBUG DEBUG DEBUG end

##        api = self.dbs_api
##        dbs_query = "find run, run.numevents, site, file.count " \
##                    "where dataset = %s " \
##                    "and dataset.status = VALID" % \
##                    dataset_name
##        try:
##            api_result = api.executeQuery(dbs_query)
##        except DbsApiException:
##            msg = "ERROR: Could not execute DBS query"
##            self.logger.fatal(msg)
##            raise Error(msg)

##        # Index things by run number. No cross-check is done to make
##        # sure we get results for each and every run in the
##        # dataset. I'm not sure this would make sense since we'd be
##        # cross-checking DBS info with DBS info anyway. Note that we
##        # use the file count per site to see if we're dealing with an
##        # incomplete vs. a mirrored dataset.
##        sample_info = {}
##        try:
##            class Handler(xml.sax.handler.ContentHandler):
##                def startElement(self, name, attrs):
##                    if name == "result":
##                        run_number = int(attrs["RUNS_RUNNUMBER"])
##                        site_name = str(attrs["STORAGEELEMENT_SENAME"])
##                        file_count = int(attrs["COUNT_FILES"])
##                        # BUG BUG BUG
##                        # Doh! For some reason DBS never returns any other
##                        # event count than zero.
##                        event_count = int(attrs["RUNS_NUMBEROFEVENTS"])
##                        # BUG BUG BUG end
##                        info = (site_name, file_count, event_count)
##                        try:
##                            sample_info[run_number].append(info)
##                        except KeyError:
##                            sample_info[run_number] = [info]
##            xml.sax.parseString(api_result, Handler())
##        except SAXParseException:
##            msg = "ERROR: Could not parse DBS server output"
##            self.logger.fatal(msg)
##            raise Error(msg)

##        # Now translate this into a slightly more usable mapping.
##        sites = {}
##        for (run_number, site_info) in sample_info.iteritems():
##            # Quick-n-dirty trick to see if all file counts are the
##            # same.
##            unique_file_counts = set([i[1] for i in site_info])
##            if len(unique_file_counts) == 1:
##                # Okay, so this must be a mirrored dataset.
##                # We have to pick one but we have to be careful. We
##                # cannot submit to things like a T0, a T1, or CAF.
##                site_names = [self.pick_a_site([i[0] for i in site_info])]
##                nevents = [site_info[0][2]]
##            else:
##                # Looks like this is a spread-out sample.
##                site_names = [i[0] for i in site_info]
##                nevents = [i[2] for i in site_info]
##            sites[run_number] = zip(site_names, nevents)

##        self.logger.debug("Sample `%s' spread is:" % dataset_name)
##        run_numbers = sites.keys()
##        run_numbers.sort()
##        for run_number in run_numbers:
##            self.logger.debug("  run # %6d: %d site(s) (%s)" % \
##                              (run_number,
##                               len(sites[run_number]),
##                               ", ".join([i[0] for i in sites[run_number]])))

##        # End of dbs_check_dataset_spread_old.
##        return sites
##    # DEBUG DEBUG DEBUG end

    ##########

    def dbs_check_dataset_spread(self, dataset_name):
        """Figure out the number of events in each run of this dataset.

        This is a more efficient way of doing this than calling
        dbs_resolve_number_of_events for each run.

        """

        self.logger.debug("Checking spread of dataset `%s'" % dataset_name)

        # DEBUG DEBUG DEBUG
        # If we get here DBS should have been set up already.
        assert not self.dbs_api is None
        # DEBUG DEBUG DEBUG end

        api = self.dbs_api
        dbs_query = "find run.number, site, file.name, file.numevents " \
                    "where dataset = %s " \
                    "and dataset.status = VALID" % \
                    dataset_name
        try:
            api_result = api.executeQuery(dbs_query)
        except DbsApiException:
            msg = "ERROR: Could not execute DBS query"
            self.logger.fatal(msg)
            raise Error(msg)

        try:
            files_info = {}
            class Handler(xml.sax.handler.ContentHandler):
                def startElement(self, name, attrs):
                    if name == "result":
                        site_name = str(attrs["STORAGEELEMENT_SENAME"])
                        # TODO TODO TODO
                        # Ugly hack to get around cases like this:
                        #   $ dbs search --query="find dataset, site, file.count where dataset=/RelValQCD_Pt_3000_3500/CMSSW_3_3_0_pre1-STARTUP31X_V4-v1/GEN-SIM-RECO"
                        #   Using DBS instance at: http://cmsdbsprod.cern.ch/cms_dbs_prod_global/servlet/DBSServlet
                        #   Processing ... \
                        #   PATH    STORAGEELEMENT_SENAME   COUNT_FILES
                        #   _________________________________________________________________________________
                        #   /RelValQCD_Pt_3000_3500/CMSSW_3_3_0_pre1-STARTUP31X_V4-v1/GEN-SIM-RECO          1
                        #   /RelValQCD_Pt_3000_3500/CMSSW_3_3_0_pre1-STARTUP31X_V4-v1/GEN-SIM-RECO  cmssrm.fnal.gov 12
                        #   /RelValQCD_Pt_3000_3500/CMSSW_3_3_0_pre1-STARTUP31X_V4-v1/GEN-SIM-RECO  srm-cms.cern.ch 12
                        if len(site_name) < 1:
                            return
                        # TODO TODO TODO end
                        run_number = int(attrs["RUNS_RUNNUMBER"])
                        file_name = str(attrs["FILES_LOGICALFILENAME"])
                        nevents = int(attrs["FILES_NUMBEROFEVENTS"])
                        # I know, this is a bit of a kludge.
                        if not files_info.has_key(run_number):
                            # New run.
                            files_info[run_number] = {}
                            files_info[run_number][file_name] = (nevents,
                                                                 [site_name])
                        elif not files_info[run_number].has_key(file_name):
                            # New file for a known run.
                            files_info[run_number][file_name] = (nevents,
                                                                 [site_name])
                        else:
                            # New entry for a known file for a known run.
                            # DEBUG DEBUG DEBUG
                            # Each file should have the same number of
                            # events independent of the site it's at.
                            assert nevents == files_info[run_number][file_name][0]
                            # DEBUG DEBUG DEBUG end
                            files_info[run_number][file_name][1].append(site_name)
            xml.sax.parseString(api_result, Handler())
        except SAXParseException:
            msg = "ERROR: Could not parse DBS server output"
            self.logger.fatal(msg)
            raise Error(msg)

        # Remove any information for files that are not available
        # anywhere. NOTE: After introducing the ugly hack above, this
        # is a bit redundant, but let's keep it for the moment.
        for run_number in files_info.keys():
            files_without_sites = [i for (i, j) in \
                                   files_info[run_number].items() \
                                   if len(j[1]) < 1]
            if len(files_without_sites) > 0:
                self.logger.warning("Removing %d file(s)" \
                                    " with empty site names" % \
                                    len(files_without_sites))
                for file_name in files_without_sites:
                    del files_info[run_number][file_name]
                    # files_info[run_number][file_name] = (files_info \
                    #                                     [run_number] \
                    #                                      [file_name][0], [])

        # And another bit of a kludge.
        num_events_catalog = {}
        for run_number in files_info.keys():
            site_names = list(set([j for i in files_info[run_number].values() for j in i[1]]))

            # NOTE: The term `mirrored' does not have the usual
            # meaning here. It basically means that we can apply
            # single-step harvesting.
            mirrored = None
            if len(site_names) > 1:
                # Now we somehow need to figure out if we're dealing
                # with a mirrored or a spread-out dataset. The rule we
                # use here is that we're dealing with a spread-out
                # dataset unless we can find at least one site
                # containing exactly the full list of files for this
                # dataset that DBS knows about. In that case we just
                # use only that site.
                all_file_names = files_info[run_number].keys()
                all_file_names = set(all_file_names)
                sites_with_complete_copies = []
                for site_name in site_names:
                    files_at_site = [i for (i, (j, k)) \
                                     in files_info[run_number].items() \
                                     if site_name in k]
                    files_at_site = set(files_at_site)
                    if files_at_site == all_file_names:
                        sites_with_complete_copies.append(site_name)
                if len(sites_with_complete_copies) < 1:
                    # This dataset/run is available at more than one
                    # site, but no one has a complete copy.
                    mirrored = False
                else:
                    # This dataset/run is available at more than one
                    # site and at least one of them has a complete
                    # copy. Even if this is only a single site, let's
                    # call this `mirrored' and run the single-step
                    # harvesting.
                    mirrored = True

##                site_names_ref = set(files_info[run_number].values()[0][1])
##                for site_names_tmp in files_info[run_number].values()[1:]:
##                    if set(site_names_tmp[1]) != site_names_ref:
##                        mirrored = False
##                        break

                if mirrored:
                    self.logger.debug("    -> run appears to be `mirrored'")
                else:
                    self.logger.debug("    -> run appears to be spread-out")

                if mirrored and \
                       len(sites_with_complete_copies) != len(site_names):
                    # Remove any references to incomplete sites if we
                    # have at least one complete site (and if there
                    # are incomplete sites).
                    for (file_name, (i, sites)) in files_info[run_number].items():
                        complete_sites = [site for site in sites \
                                          if site in sites_with_complete_copies]
                        files_info[run_number][file_name] = (i, complete_sites)

            self.logger.debug("  for run #%d:" % run_number)
            num_events_catalog[run_number] = {}
            num_events_catalog[run_number]["all_sites"] = sum([i[0] for i in files_info[run_number].values()])
            if len(site_names) < 1:
                self.logger.debug("    run is not available at any site")
                self.logger.debug("      (but should contain %d events" % \
                                  num_events_catalog[run_number]["all_sites"])
            else:
                self.logger.debug("    at all sites combined there are %d events" % \
                                  num_events_catalog[run_number]["all_sites"])
                for site_name in site_names:
                    num_events_catalog[run_number][site_name] = sum([i[0] for i in files_info[run_number].values() if site_name in i[1]])
                    self.logger.debug("    at site `%s' there are %d events" % \
                                      (site_name, num_events_catalog[run_number][site_name]))
            num_events_catalog[run_number]["mirrored"] = mirrored

        # End of dbs_check_dataset_spread.
        return num_events_catalog

    # Beginning of old version.
##    def dbs_check_dataset_num_events(self, dataset_name):
##        """Figure out the number of events in each run of this dataset.

##        This is a more efficient way of doing this than calling
##        dbs_resolve_number_of_events for each run.

##        # BUG BUG BUG
##        # This might very well not work at all for spread-out samples. (?)
##        # BUG BUG BUG end

##        """

##        # DEBUG DEBUG DEBUG
##        # If we get here DBS should have been set up already.
##        assert not self.dbs_api is None
##        # DEBUG DEBUG DEBUG end

##        api = self.dbs_api
##        dbs_query = "find run.number, file.name, file.numevents where dataset = %s " \
##                    "and dataset.status = VALID" % \
##                    dataset_name
##        try:
##            api_result = api.executeQuery(dbs_query)
##        except DbsApiException:
##            msg = "ERROR: Could not execute DBS query"
##            self.logger.fatal(msg)
##            raise Error(msg)

##        try:
##            files_info = {}
##            class Handler(xml.sax.handler.ContentHandler):
##                def startElement(self, name, attrs):
##                    if name == "result":
##                        run_number = int(attrs["RUNS_RUNNUMBER"])
##                        file_name = str(attrs["FILES_LOGICALFILENAME"])
##                        nevents = int(attrs["FILES_NUMBEROFEVENTS"])
##                        try:
##                            files_info[run_number][file_name] = nevents
##                        except KeyError:
##                            files_info[run_number] = {file_name: nevents}
##            xml.sax.parseString(api_result, Handler())
##        except SAXParseException:
##            msg = "ERROR: Could not parse DBS server output"
##            self.logger.fatal(msg)
##            raise Error(msg)

##        num_events_catalog = {}
##        for run_number in files_info.keys():
##            num_events_catalog[run_number] = sum(files_info[run_number].values())

##        # End of dbs_check_dataset_num_events.
##        return num_events_catalog
    # End of old version.

    ##########

    def build_dataset_list(self, input_method, input_name):
        """Build a list of all datasets to be processed.

        """

        dataset_names = []

        # It may be, but only for the list of datasets to ignore, that
        # the input method and name are None because nothing was
        # specified. In that case just an empty list is returned.
        if input_method is None:
            pass
        elif input_method == "dataset":
            # Input comes from a dataset name directly on the command
            # line. But, this can also contain wildcards so we need
            # DBS to translate it conclusively into a list of explicit
            # dataset names.
            self.logger.info("Asking DBS for dataset names")
            dataset_names = self.dbs_resolve_dataset_name(input_name)
        elif input_method == "listfile":
            # In this case a file containing a list of dataset names
            # is specified. Still, each line may contain wildcards so
            # this step also needs help from DBS.
            # NOTE: Lines starting with a `#' are ignored.
            self.logger.info("Reading input from list file `%s'" % \
                             input_name)
            try:
                listfile = open(self.input_name, "r")
                for dataset in listfile:
                    # Skip lines starting with a `#'.
                    if dataset.strip()[0] != "#":
                        dataset_names.extend(self. \
                                             dbs_resolve_dataset_name(dataset))
                listfile.close()
            except IOError:
                msg = "ERROR: Could not open input list file `%s'" % \
                      self.input_name
                self.logger.fatal(msg)
                raise Error(msg)
        else:
            # DEBUG DEBUG DEBUG
            # We should never get here.
            assert False, "Unknown input method `%s'" % input_method
            # DEBUG DEBUG DEBUG end

        # Remove duplicates from the dataset list.
        # NOTE: There should not be any duplicates in any list coming
        # from DBS, but maybe the user provided a list file with less
        # care.
        dataset_names = list(set(dataset_names))

        # Store for later use.
        dataset_names.sort()

        # End of build_dataset_list.
        return dataset_names

    ##########

    def build_dataset_use_list(self):
        """Build a list of datasets to process.

        """

        self.logger.info("Building list of datasets to consider...")

        input_method = self.input_method["use"]
        input_name = self.input_name["use"]
        dataset_names = self.build_dataset_list(input_method,
                                                input_name)
        self.datasets_to_use = dict(zip(dataset_names,
                                        [None] * len(dataset_names)))

        self.logger.info("  found %d dataset(s) to process:" % \
                         len(dataset_names))
        for dataset in dataset_names:
            self.logger.info("  `%s'" % dataset)


        # End of build_dataset_list.

    ##########

    def build_dataset_ignore_list(self):
        """Build a list of datasets to ignore.

        NOTE: We should always have a list of datasets to process, but
        it may be that we don't have a list of datasets to ignore.

        """

        self.logger.info("Building list of datasets to ignore...")

        input_method = self.input_method["ignore"]
        input_name = self.input_name["ignore"]
        dataset_names = self.build_dataset_list(input_method,
                                                input_name)
        self.datasets_to_ignore = dict(zip(dataset_names,
                                           [None] * len(dataset_names)))

        self.logger.info("  found %d dataset(s) to ignore:" % \
                         len(dataset_names))
        for dataset in dataset_names:
            self.logger.info("  `%s'" % dataset)

        # End of build_dataset_ignore_list.

    ##########

    def process_dataset_ignore_list(self):
        """Update the list of datasets taking into account the ones to
        ignore.

        Both lists have been generated before from DBS and both are
        assumed to be unique.

        NOTE: The advantage of creating the ignore list from DBS (in
        case a regexp is given) and matching that instead of directly
        matching the ignore criterion against the list of datasets (to
        consider) built from DBS is that in the former case we're sure
        that all regexps are treated exactly as DBS would have done
        without the cmsHarvester.

        NOTE: This only removes complete samples. Exclusion of single
        runs is done by the book keeping. So the assumption is that a
        user never wants to harvest just part (i.e. n out of N runs)
        of a sample.

        """

        self.logger.info("Processing list of datasets to ignore...")

        self.logger.debug("Before processing ignore list there are %d " \
                          "datasets in the list to be processed" % \
                          len(self.datasets_to_use))

        # Simple approach: just loop and search.
        dataset_names_filtered = copy.deepcopy(self.datasets_to_use)
        for dataset_name in self.datasets_to_use.keys():
            if dataset_name in self.datasets_to_ignore.keys():
                del dataset_names_filtered[dataset_name]

        self.logger.info("  --> Removed %d datasets" % \
                         (len(self.datasets_to_use) -
                          len(dataset_names_filtered)))

        self.datasets_to_use = dataset_names_filtered

        self.logger.debug("After processing ignore list there are %d " \
                          "datasets in the list to be processed" % \
                          len(self.datasets_to_use))

    # End of process_dataset_ignore_list.

    ##########

    def process_book_keeping(self):
        """Fold the results of the book keeping we read into the list of
        things to do.

        The difference with the processing of the ignore-list is that
        that list contains dataset names, i.e. complete datasets,
        whereas this list is a nested list of datasets and run
        numbers.

        """

        self.logger.info("Processing book keeping information " \
                         "(from previous runs I presume)...")

        self.logger.debug("Before processing the book keeping there are %d " \
                          "datasets in the list to be processed" % \
                          len(self.datasets_to_use))

        # Simple approach: just loop and search.
        dataset_names_filtered = copy.deepcopy(self.datasets_to_use)
        nruns_removed = 0
        for (dataset_name, runs) in self.datasets_to_use.iteritems():
            if dataset_name in self.book_keeping_information.keys():
                for run in runs:
                    if run in self.book_keeping_information[dataset_name]:
                        # Don't forget to check event counts. It could
                        # be that since we processed this run more
                        # events have become available.
                        num_events_processed = self.book_keeping_information \
                                               [dataset_name][run]
                        num_events_now = self.datasets_information \
                                         [dataset_name]["num_events"][run]
                        if num_events_processed >= num_events_now:
                            dataset_names_filtered[dataset_name].remove(run)
                            nruns_removed = nruns_removed + 1
                # Clean out empty datasets (just in case we removed
                # all runs).
                if len(dataset_names_filtered[dataset_name]) < 1:
                    del dataset_names_filtered[dataset_name]

        self.logger.info("  --> Removed %d datasets" % \
                         (len(self.datasets_to_use) -
                          len(dataset_names_filtered)))
        self.logger.debug("      (removed %d runs)" % nruns_removed)

        self.datasets_to_use = dataset_names_filtered

        self.logger.debug("After processing the book keeping there are %d " \
                          "datasets in the list to be processed" % \
                          len(self.datasets_to_use))

        # End of process_book_keeping.

    ##########

    def singlify_datasets(self):
        """Remove all but the largest part of all datasets.

        This allows us to harvest at least part of these datasets
        using single-step harvesting until the two-step approach
        works.

        """

        # DEBUG DEBUG DEBUG
        assert self.harvesting_mode == "single-step-allow-partial"
        # DEBUG DEBUG DEBUG end

        for dataset_name in self.datasets_to_use:
            for run_number in self.datasets_information[dataset_name]["runs"]:
                max_events = max(self.datasets_information[dataset_name]["sites"][run_number].values())
                sites_with_max_events = [i[0] for i in self.datasets_information[dataset_name]["sites"][run_number].items() if i[1] == max_events]
                cmssw_version = self.datasets_information[dataset_name] \
                                ["cmssw_version"]
                selected_site = self.pick_a_site(sites_with_max_events,
                                                 cmssw_version)
                self.datasets_information[dataset_name]["sites"][run_number] = {selected_site: max_events}
                #self.datasets_information[dataset_name]["sites"][run_number] = [selected_site]

        # End of singlify_datasets.

    ##########

    def check_dataset_list(self):
        """Check list of dataset names for impossible ones.

        Two kinds of checks are done:
        - Checks for things that do not make sense. These lead to
          errors and skipped datasets.
        - Sanity checks. For these warnings are issued but the user is
          considered to be the authoritative expert.

        Checks performed:
        - The CMSSW version encoded in the dataset name should match
          self.cmssw_version. This is critical.
        - There should be some events in the dataset/run. This is
          critical in the sense that CRAB refuses to create jobs for
          zero events. And yes, this does happen in practice. E.g. the
          reprocessed CRAFT08 datasets contain runs with zero events.
        - A cursory check is performed to see if the harvesting type
          makes sense for the data type. This should prevent the user
          from inadvertently running RelVal for data.
        - It is not possible to run single-step harvesting jobs on
          samples that are not fully contained at a single site.
        - Each dataset/run has to be available at at least one site.

        """

        self.logger.info("Performing sanity checks on dataset list...")

        dataset_names_after_checks = copy.deepcopy(self.datasets_to_use)

        for dataset_name in self.datasets_to_use.keys():

            # Check CMSSW version.
            version_from_dataset = self.datasets_information[dataset_name] \
                                   ["cmssw_version"]
            if version_from_dataset != self.cmssw_version:
                msg = "  CMSSW version mismatch for dataset `%s' " \
                      "(%s vs. %s)" % \
                      (dataset_name,
                       self.cmssw_version, version_from_dataset)
                if self.force_running:
                    # Expert mode: just warn, then continue.
                    self.logger.warning("%s " \
                                        "--> `force mode' active: " \
                                        "run anyway" % msg)
                else:
                    del dataset_names_after_checks[dataset_name]
                    self.logger.warning("%s " \
                                        "--> skipping" % msg)
                    continue

            ###

            # Check that the harvesting type makes sense for the
            # sample. E.g. normally one would not run the DQMOffline
            # harvesting on Monte Carlo.
            # TODO TODO TODO
            # This should be further refined.
            suspicious = False
            datatype = self.datasets_information[dataset_name]["datatype"]
            if datatype == "data":
                # Normally only DQM harvesting is run on data.
                if self.harvesting_type != "DQMOffline":
                    suspicious = True
            elif datatype == "mc":
                if self.harvesting_type == "DQMOffline":
                    suspicious = True
            else:
                # Doh!
                assert False, "ERROR Impossible data type `%s' " \
                       "for dataset `%s'" % \
                       (datatype, dataset_name)
            if suspicious:
                msg = "  Normally one does not run `%s' harvesting " \
                      "on %s samples, are you sure?" % \
                      (self.harvesting_type, datatype)
                if self.force_running:
                    self.logger.warning("%s " \
                                        "--> `force mode' active: " \
                                        "run anyway" % msg)
                else:
                    del dataset_names_after_checks[dataset_name]
                    self.logger.warning("%s " \
                                        "--> skipping" % msg)
                    continue

            # TODO TODO TODO end

            ###

            # BUG BUG BUG
            # For the moment, due to a problem with DBS, I cannot
            # figure out the GlobalTag for data by myself. (For MC
            # it's no problem.) This means that unless a GlobalTag was
            # specified from the command line, we will have to skip
            # any data datasets.

            if datatype == "data":
                if self.globaltag is None:
                    msg = "For data datasets (like `%s') " \
                          "we need a GlobalTag" % \
                          dataset_name
                    del dataset_names_after_checks[dataset_name]
                    self.logger.warning("%s " \
                                        "--> skipping" % msg)
                    continue

            # BUG BUG BUG end

            ###

            # Require that each run is available at least somewhere.
            runs_without_sites = [i for (i, j) in \
                                  self.datasets_information[dataset_name] \
                                  ["sites"].items() \
                                  if len(j) < 1 and \
                                  i in self.datasets_to_use[dataset_name]]
            if len(runs_without_sites) > 0:
                for run_without_sites in runs_without_sites:
                    try:
                        dataset_names_after_checks[dataset_name].remove(run_without_sites)
                    except KeyError:
                        pass
                self.logger.warning("  removed %d unavailable runs " \
                                    "from dataset `%s'" % \
                                    (len(runs_without_sites), dataset_name))
                self.logger.debug("    (%s)" % \
                                  ", ".join([str(i) for i in \
                                             runs_without_sites]))

            ###

            # Unless we're running two-step harvesting: only allow
            # samples located on a single site.
            if not self.harvesting_mode == "two-step":
                for run_number in self.datasets_to_use[dataset_name]:
                    # DEBUG DEBUG DEBUG
##                    if self.datasets_information[dataset_name]["num_events"][run_number] != 0:
##                        pdb.set_trace()
                    # DEBUG DEBUG DEBUG end
                    num_sites = len(self.datasets_information[dataset_name] \
                                ["sites"][run_number])
                    if num_sites > 1 and \
                           not self.datasets_information[dataset_name] \
                           ["mirrored"][run_number]:
                        # Cannot do this with a single-step job, not
                        # even in force mode. It just does not make
                        # sense.
                        msg = "  Dataset `%s', run %d is spread across more " \
                              "than one site.\n" \
                              "  Cannot run single-step harvesting on " \
                              "samples spread across multiple sites" % \
                              (dataset_name, run_number)
                        try:
                            dataset_names_after_checks[dataset_name].remove(run_number)
                        except KeyError:
                            pass
                        self.logger.warning("%s " \
                                            "--> skipping" % msg)

            ###

            # Require that the dataset/run is non-empty.
            # NOTE: To avoid reconsidering empty runs/datasets next
            # time around, we do include them in the book keeping.
            # BUG BUG BUG
            # This should sum only over the runs that we use!
            tmp = [j for (i, j) in self.datasets_information \
                   [dataset_name]["num_events"].items() \
                   if i in self.datasets_to_use[dataset_name]]
            num_events_dataset = sum(tmp)
            # BUG BUG BUG end
            if num_events_dataset < 1:
                msg = "  dataset `%s' is empty" % dataset_name
                del dataset_names_after_checks[dataset_name]
                self.logger.warning("%s " \
                                    "--> skipping" % msg)
                # Update the book keeping with all the runs in the dataset.
                # DEBUG DEBUG DEBUG
                assert set([j for (i, j) in self.datasets_information \
                            [dataset_name]["num_events"].items() \
                            if i in self.datasets_to_use[dataset_name]]) == \
                            set([0])
                # DEBUG DEBUG DEBUG end
                self.book_keeping_information[dataset_name] = self.datasets_information \
                                                              [dataset_name]["num_events"]
                continue
            tmp = [i for i in \
                   self.datasets_information[dataset_name] \
                   ["num_events"].items() if i[1] < 1]
            tmp = [i for i in tmp if i[0] in self.datasets_to_use[dataset_name]]
            empty_runs = dict(tmp)
            if len(empty_runs) > 0:
                for empty_run in empty_runs:
                    try:
                        dataset_names_after_checks[dataset_name].remove(empty_run)
                    except KeyError:
                        pass
                self.logger.info("  removed %d empty runs from dataset `%s'" % \
                                 (len(empty_runs), dataset_name))
                self.logger.debug("    (%s)" % \
                                  ", ".join([str(i) for i in empty_runs]))

                # Update the book keeping (for single runs this time).
                # DEBUG DEBUG DEBUG
                assert not self.book_keeping_information.has_key(dataset_name)
                # DEBUG DEBUG DEBUG end
                self.book_keeping_information[dataset_name] = empty_runs

        ###

        # If we emptied out a complete dataset, remove the whole
        # thing.
        dataset_names_after_checks_tmp = copy.deepcopy(dataset_names_after_checks)
        for (dataset_name, runs) in dataset_names_after_checks.iteritems():
            if len(runs) < 1:
                self.logger.warning("  Removing dataset without any runs " \
                                    "(left) `%s'" % \
                                    dataset_name)
                del dataset_names_after_checks_tmp[dataset_name]
        dataset_names_after_checks = dataset_names_after_checks_tmp

        ###

        self.logger.warning("  --> Removed %d datasets" % \
                            (len(self.datasets_to_use) -
                             len(dataset_names_after_checks)))

        # Now store the modified version of the dataset list.
        self.datasets_to_use = dataset_names_after_checks

        # End of check_dataset_list.

    ##########

    def escape_dataset_name(self, dataset_name):
        """Escape a DBS dataset name.

        Escape a DBS dataset name such that it does not cause trouble
        with the file system. This means turning each `/' into `__',
        except for the first one which is just removed.

        """

        escaped_dataset_name = dataset_name
        escaped_dataset_name = escaped_dataset_name.strip("/")
        escaped_dataset_name = escaped_dataset_name.replace("/", "__")

        return escaped_dataset_name

    ##########

    # BUG BUG BUG
    # This is a bit of a redundant method, isn't it?
    def create_config_file_name(self, dataset_name):
        """Generate the name of the configuration file to be run by
        CRAB.

        Depending on the harvesting mode (single-step or two-step)
        this is the name of the real harvesting configuration or the
        name of the first-step ME summary extraction configuration.

        """

        if self.harvesting_mode == "single-step":
            config_file_name = self.create_harvesting_config_file_name(dataset_name)
        elif self.harvesting_mode == "single-step-allow-partial":
            config_file_name = self.create_harvesting_config_file_name(dataset_name)
            config_file_name = config_file_name.replace(".py", "_partial.py")
        elif self.harvesting_mode == "two-step":
            config_file_name = self.create_me_summary_config_file_name(dataset_name)
        else:
            assert False, "ERROR Unknown harvesting mode `%s'" % \
                   self.harvesting_mode

        # End of create_config_file_name.
        return config_file_name
    # BUG BUG BUG end

    ##########

    def create_harvesting_config_file_name(self, dataset_name):
        "Generate the name to be used for the harvesting config file."

        file_name_base = "harvesting.py"
        dataset_name_escaped = self.escape_dataset_name(dataset_name)
        config_file_name = file_name_base.replace(".py",
                                                  "_%s.py" % \
                                                  dataset_name_escaped)

        # End of create_harvesting_config_file_name.
        return config_file_name

    ##########

    def create_me_summary_config_file_name(self, dataset_name):
        "Generate the name of the ME summary extraction config file."

        file_name_base = "me_extraction.py"
        dataset_name_escaped = self.escape_dataset_name(dataset_name)
        config_file_name = file_name_base.replace(".py",
                                                  "_%s.py" % \
                                                  dataset_name_escaped)

        # End of create_me_summary_config_file_name.
        return config_file_name

    ##########

    def create_output_file_name(self, dataset_name, run_number=None):
        """Create the name of the output file name to be used.

        This is the name of the output file of the `first step'. In
        the case of single-step harvesting this is already the final
        harvesting output ROOT file. In the case of two-step
        harvesting it is the name of the intermediary ME summary
        file.

        """

        # BUG BUG BUG
        # This method has become a bit of a mess. Originally it was
        # nice to have one entry point for both single- and two-step
        # output file names. However, now the former needs the run
        # number, while the latter does not even know about run
        # numbers. This should be fixed up a bit.
        # BUG BUG BUG end

        if self.harvesting_mode == "single-step":
            # DEBUG DEBUG DEBUG
            assert not run_number is None
            # DEBUG DEBUG DEBUG end
            output_file_name = self.create_harvesting_output_file_name(dataset_name, run_number)
        elif self.harvesting_mode == "single-step-allow-partial":
            # DEBUG DEBUG DEBUG
            assert not run_number is None
            # DEBUG DEBUG DEBUG end
            output_file_name = self.create_harvesting_output_file_name(dataset_name, run_number)
        elif self.harvesting_mode == "two-step":
            # DEBUG DEBUG DEBUG
            assert run_number is None
            # DEBUG DEBUG DEBUG end
            output_file_name = self.create_me_summary_output_file_name(dataset_name)
        else:
            # This should not be possible, but hey...
            assert False, "ERROR Unknown harvesting mode `%s'" % \
                   self.harvesting_mode

        # End of create_harvesting_output_file_name.
        return output_file_name

    ##########

    def create_harvesting_output_file_name(self, dataset_name, run_number):
        """Generate the name to be used for the harvesting output file.

        This harvesting output file is the _final_ ROOT output file
        containing the harvesting results. In case of two-step
        harvesting there is an intermediate ME output file as well.

        """

        dataset_name_escaped = self.escape_dataset_name(dataset_name)

        # Hmmm, looking at the code for the DQMFileSaver this might
        # actually be the place where the first part of this file
        # naming scheme comes from.
        # NOTE: It looks like the `V0001' comes from the DQM
        # version. This is something that cannot be looked up from
        # here, so let's hope it does not change too often.
        output_file_name = "DQM_V0001_R%09d__%s.root" % \
                           (run_number, dataset_name_escaped)
        if self.harvesting_mode.find("partial") > -1:
            output_file_name = output_file_name.replace(".root", \
                                                        "_partial.root")

        # End of create_harvesting_output_file_name.
        return output_file_name

    ##########

    def create_me_summary_output_file_name(self, dataset_name):
        """Generate the name of the intermediate ME file name to be
        used in two-step harvesting.

        """

        dataset_name_escaped = self.escape_dataset_name(dataset_name)
        output_file_name = "me_summary_%s.root" % \
                           dataset_name_escaped

        # End of create_me_summary_output_file_name.
        return output_file_name

    ##########

    def create_multicrab_block_name(self, dataset_name, run_number):
        """Create the block name to use for this dataset/run number.

        This is what appears in the brackets `[]' in multicrab.cfg. It
        is used as the name of the job and to create output
        directories.

        """

        dataset_name_escaped = self.escape_dataset_name(dataset_name)
        block_name = "%s_%09d" % (dataset_name_escaped, run_number)

        # End of create_multicrab_block_name.
        return block_name

    ##########

    def create_crab_config(self):
        """Create a CRAB configuration for a given job.

        NOTE: This is _not_ a complete (as in: submittable) CRAB
        configuration. It is used to store the common settings for the
        multicrab configuration.

        NOTE: Only CERN CASTOR area (/castor/cern.ch/) is supported.

        NOTE: According to CRAB, you `Must define exactly two of
        total_number_of_events, events_per_job, or
        number_of_jobs.'. For single-step harvesting we force one job,
        for the rest we don't really care.

        # BUG BUG BUG
        # With the current version of CRAB (2.6.1), in which Daniele
        # fixed the behaviour of no_block_boundary for me, one _has to
        # specify_ the total_number_of_events and one single site in
        # the se_white_list.
        # BUG BUG BUG end

        """

        tmp = []

        # This is the stuff we will need to fill in.
        castor_prefix = self.castor_prefix

        tmp.append(self.config_file_header())
        tmp.append("")
        tmp.append("[CRAB]")
        tmp.append("jobtype = cmssw")
        tmp.append("scheduler = glite")
        tmp.append("")
        tmp.append("[GRID]")
        tmp.append("# This removes the default blacklisting of T1 sites.")
        tmp.append("remove_default_blacklist = 1")
        tmp.append("rb = CERN")
        tmp.append("role = t1access")
        tmp.append("")
        tmp.append("[USER]")
        tmp.append("copy_data = 1")
        tmp.append("storage_element=srm-cms.cern.ch")
        tmp.append("storage_path=/srm/managerv2?SFN=%s" % castor_prefix)
        tmp.append("")
        tmp.append("[CMSSW]")
        tmp.append("# This reveals data hosted on T1 sites,")
        tmp.append("# which is normally hidden by CRAB.")
        tmp.append("show_prod = 1")
        tmp.append("total_number_of_events = -1")
        tmp.append("number_of_jobs = 1")

        if self.harvesting_mode.find("single-step") > -1:
            tmp.append("# Force everything to run in one job.")
            tmp.append("no_block_boundary = 1")

        crab_config = "\n".join(tmp)

        # End of create_crab_config.
        return crab_config

    ##########

    def create_multicrab_config(self):
        """Create a multicrab.cfg file for all samples.

        This creates the contents for a multicrab.cfg file that uses
        the crab.cfg file (generated elsewhere) for the basic settings
        and contains blocks for each run of each dataset.

        # BUG BUG BUG
        # The fact that it's necessary to specify the se_white_list
        # and the total_number_of_events is due to our use of CRAB
        # version 2.6.1. This should no longer be necessary in the
        # future.
        # BUG BUG BUG end

        """

        multicrab_config_lines = []
        multicrab_config_lines.append(self.config_file_header())
        multicrab_config_lines.append("")
        multicrab_config_lines.append("[MULTICRAB]")
        multicrab_config_lines.append("cfg = crab.cfg")
        multicrab_config_lines.append("")

        dataset_names = self.datasets_to_use.keys()
        dataset_names.sort()
        for dataset_name in dataset_names:
            runs = self.datasets_to_use[dataset_name]
            dataset_name_escaped = self.escape_dataset_name(dataset_name)
            config_file_name = self. \
                               create_config_file_name(dataset_name)
            castor_prefix = self.castor_prefix
            for run in runs:
                output_file_name = self. \
                                   create_output_file_name(dataset_name, run)

                # DEBUG DEBUG DEBUG
                # We should only get here if we're treating a
                # dataset/run that is fully contained at a single
                # site.
                assert (len(self.datasets_information[dataset_name] \
                            ["sites"][run]) == 1) or \
                            self.datasets_information[dataset_name]["mirrored"]
                # DEBUG DEBUG DEBUG end

                site_names = self.datasets_information[dataset_name] \
                             ["sites"][run].keys()
                # If we're looking at a mirrored dataset we just pick
                # one of the sites. Otherwise there is nothing to
                # choose.
                if len(site_names) > 1:
                    cmssw_version = self.datasets_information[dataset_name] \
                                    ["cmssw_version"]
                    site_name = self.pick_a_site(site_names, cmssw_version)
                else:
                    site_name = site_names[0]
                nevents = self.datasets_information[dataset_name]["num_events"][run]

                # The block name.
                multicrab_block_name = self.create_multicrab_block_name( \
                    dataset_name, run)
                multicrab_config_lines.append("[%s]" % \
                                              multicrab_block_name)

                # The site (better: SE) where to run this job.
                # See comment at start of method.
                multicrab_config_lines.append("GRID.se_white_list = %s" % \
                                              site_name)

                # The parameter set (i.e. the configuration for this
                # dataset).
                multicrab_config_lines.append("CMSSW.pset = %s" % \
                                              config_file_name)
                # The dataset.
                multicrab_config_lines.append("CMSSW.datasetpath = %s" % \
                                              dataset_name)
                # The run selection: one job (i.e. one block in
                # multicrab.cfg) for each run of each dataset.
                multicrab_config_lines.append("CMSSW.runselection = %d" % \
                                              run)
                # The number of events to process.
                # See comment at start of method.
                multicrab_config_lines.append("CMSSW.total_number_of_events = %d" % \
                                              nevents)
                # The output file name.
                multicrab_config_lines.append("CMSSW.output_file = %s" % \
                                              output_file_name)

                # CASTOR output dir.
                castor_dir = self.datasets_information[dataset_name] \
                             ["castor_path"][run]
                castor_dir = castor_dir.replace(castor_prefix, "")
                multicrab_config_lines.append("USER.user_remote_dir = %s" % \
                                              castor_dir)

                # End of block.
                multicrab_config_lines.append("")

        multicrab_config = "\n".join(multicrab_config_lines)

        # End of create_multicrab_config.
        return multicrab_config

    ##########

    def create_harvesting_config(self, dataset_name):
        """Create the Python harvesting configuration for harvesting.

        The basic configuration is created by
        Configuration.PyReleaseValidation.ConfigBuilder. (This mimics
        what cmsDriver.py does.) After that we add some specials
        ourselves.

        NOTE: On one hand it may not be nice to circumvent
        cmsDriver.py, on the other hand cmsDriver.py does not really
        do anything itself. All the real work is done by the
        ConfigBuilder so there is not much risk that we miss out on
        essential developments of cmsDriver in the future.

        """

        # Setup some options needed by the ConfigBuilder.
        config_options = defaultOptions

        # These are fixed for all kinds of harvesting jobs. Some of
        # them are not needed for the harvesting config, but to keep
        # the ConfigBuilder happy.
        config_options.name = "harvesting"
        config_options.scenario = "pp"
        config_options.number = 1
        config_options.arguments = self.ident_string()
        config_options.evt_type = config_options.name
        config_options.customisation_file = None
        config_options.filein = "dummy_value"
        config_options.filetype = "EDM"
        # This seems to be new in CMSSW 3.3.X, no clue what it does.
        config_options.gflash = "dummy_value"

        ###

        # These options depend on the type of harvesting we're doing
        # and are stored in self.harvesting_info.

        config_options.step = "HARVESTING:%s" % \
                              self.harvesting_info[self.harvesting_type] \
                              ["step_string"]
        config_options.beamspot = self.harvesting_info[self.harvesting_type] \
                                  ["beamspot"]
        config_options.eventcontent = self.harvesting_info \
                                      [self.harvesting_type] \
                                      ["eventcontent"]
        config_options.harvesting = self.harvesting_info \
                                    [self.harvesting_type] \
                                    ["harvesting"]

        ###

        # This one is required (see also above) for each dataset.

        datatype = self.datasets_information[dataset_name]["datatype"]
        config_options.isMC = (datatype.lower() == "mc")
        globaltag = self.datasets_information[dataset_name]["globaltag"]

        config_options.conditions = self.format_conditions_string(globaltag)

        ###

        if "with_input" in getargspec(ConfigBuilder.__init__)[0]:
            # This is the case for 3.3.X.
            config_builder = ConfigBuilder(config_options, with_input=True)
        else:
            # This is the case in older CMSSW versions.
            config_builder = ConfigBuilder(config_options)
        config_builder.prepare(True)
        config_contents = config_builder.pythonCfgCode

        ###

        # Add our signature to the top of the configuration.  and add
        # some markers to the head and the tail of the Python code
        # generated by the ConfigBuilder.
        marker_lines = []
        sep = "#" * 30
        marker_lines.append(sep)
        marker_lines.append("# Code between these markers was generated by")
        marker_lines.append("# Configuration.PyReleaseValidation." \
                            "ConfigBuilder")

        marker_lines.append(sep)
        marker = "\n".join(marker_lines)

        tmp = [self.config_file_header()]
        tmp.append("")
        tmp.append(marker)
        tmp.append("")
        tmp.append(config_contents)
        tmp.append("")
        tmp.append(marker)
        tmp.append("")
        config_contents = "\n".join(tmp)

        ###

        # Now we add some stuff of our own.
        customisations = [""]

        customisations.append("# Now follow some customisations")
        customisations.append("")

        # This makes sure all reference histograms are saved to the
        # output ROOT file.
        customisations.append("process.dqmSaver.referenceHandling = \"all\"")

        # Make sure we get the `workflow' correct. As far as I can see
        # this is only important for the output file name.
        customisations.append("process.dqmSaver.workflow = \"%s\"" % \
                              dataset_name)

        # BUG BUG BUG
        # This still does not work. The current two-step harvesting
        # efforts are on hold waiting for the solution to come from
        # elsewhere. (In this case the elsewhere is Daniele Spiga.)

##        # In case this file is the second step (the real harvesting
##        # step) of the two-step harvesting we have to tell it to use
##        # our local files.
##        if self.harvesting_mode == "two-step":
##            castor_dir = self.datasets_information[dataset_name] \
##                         ["castor_path"][run]
##            customisations.append("")
##            customisations.append("# This is the second step (the real")
##            customisations.append("# harvesting step) of a two-step")
##            customisations.append("# harvesting procedure.")
##            # BUG BUG BUG
##            # To be removed in production version.
##            customisations.append("import pdb")
##            # BUG BUG BUG end
##            customisations.append("import commands")
##            customisations.append("import os")
##            customisations.append("castor_dir = \"%s\"" % castor_dir)
##            customisations.append("cmd = \"rfdir %s\" % castor_dir")
##            customisations.append("(status, output) = commands.getstatusoutput(cmd)")
##            customisations.append("if status != 0:")
##            customisations.append("    print \"ERROR\"")
##            customisations.append("    raise Exception, \"ERROR\"")
##            customisations.append("file_names = [os.path.join(\"rfio:%s\" % path, i) for i in output.split() if i.startswith(\"EDM_summary\") and i.endswith(\".root\")]")
##            #customisations.append("pdb.set_trace()")
##            customisations.append("process.source.fileNames = cms.untracked.vstring(*file_names)")
##            customisations.append("")

        # BUG BUG BUG end

        config_contents = config_contents + "\n".join(customisations)

        ###

        # End of create_harvesting_config.
        return config_contents

##    ##########

##    def create_harvesting_config_two_step(self, dataset_name):
##        """Create the Python harvesting configuration for two-step
##        harvesting.

##        """

##        # BUG BUG BUG
##        config_contents = self.create_harvesting_config_single_step(dataset_name)
##        # BUG BUG BUG end

##        # End of create_harvesting_config_two_step.
##        return config_contents

    ##########

    def create_me_extraction_config(self, dataset_name):
        """

        """

        # Big chunk of hard-coded Python. Not such a big deal since
        # this does not do much and is not likely to break.
        tmp = []
        tmp.append(self.config_file_header())
        tmp.append("")
        tmp.append("import FWCore.ParameterSet.Config as cms")
        tmp.append("")
        tmp.append("process = cms.Process(\"ME2EDM\")")
        tmp.append("")
        tmp.append("# Import of standard configurations")
        tmp.append("process.load(\"Configuration/EventContent/EventContent_cff\")")
        tmp.append("")
        tmp.append("# We don't really process any events, just keep this set to one to")
        tmp.append("# make sure things work.")
        tmp.append("process.maxEvents = cms.untracked.PSet(")
        tmp.append("    input = cms.untracked.int32(1)")
        tmp.append("    )")
        tmp.append("")
        tmp.append("process.options = cms.untracked.PSet(")
        tmp.append("    Rethrow = cms.untracked.vstring(\"ProductNotFound\")")
        tmp.append("    )")
        tmp.append("")
        tmp.append("process.source = cms.Source(\"PoolSource\",")
        tmp.append("                            processingMode = \\")
        tmp.append("                            cms.untracked.string(\"RunsAndLumis\"),")
        tmp.append("                            fileNames = \\")
        tmp.append("                            cms.untracked.vstring(\"no_file_specified\")")
        tmp.append("                            )")
        tmp.append("")
        tmp.append("# Output definition: drop everything except for the monitoring.")
        tmp.append("process.output = cms.OutputModule(")
        tmp.append("    \"PoolOutputModule\",")
        tmp.append("    outputCommands = \\")
        tmp.append("    cms.untracked.vstring(\"drop *\", \\")
        tmp.append("                          \"keep *_MEtoEDMConverter_*_*\"),")
        output_file_name = self. \
                           create_output_file_name(dataset_name)
        tmp.append("    fileName = \\")
        tmp.append("    cms.untracked.string(\"%s\")," % output_file_name)
        tmp.append("    dataset = cms.untracked.PSet(")
        tmp.append("    dataTier = cms.untracked.string(\"RECO\"),")
        tmp.append("    filterName = cms.untracked.string(\"\")")
        tmp.append("    )")
        tmp.append("    )")
        tmp.append("")
        tmp.append("# Additional output definition")
        tmp.append("process.out_step = cms.EndPath(process.output)")
        tmp.append("")
        tmp.append("# Schedule definition")
        tmp.append("process.schedule = cms.Schedule(process.out_step)")
        tmp.append("")

        config_contents = "\n".join(tmp)

        # End of create_me_extraction_config.
        return config_contents

    ##########

##    def create_harvesting_config(self, dataset_name):
##        """Create the Python harvesting configuration for a given job.

##        NOTE: The reason to have a single harvesting configuration per
##        sample is to be able to specify the GlobalTag corresponding to
##        each sample. Since it has been decided that (apart from the
##        prompt reco) datasets cannot contain runs with different
##        GlobalTags, we don't need a harvesting config per run.

##        NOTE: This is the place where we distinguish between
##        single-step and two-step harvesting modes (at least for the
##        Python job configuration).

##        """

##        ###

##        if self.harvesting_mode == "single-step":
##            config_contents = self.create_harvesting_config_single_step(dataset_name)
##        elif self.harvesting_mode == "two-step":
##            config_contents = self.create_harvesting_config_two_step(dataset_name)
##        else:
##            # Impossible harvesting mode, we should never get here.
##            assert False, "ERROR: unknown harvesting mode `%s'" % \
##                   self.harvesting_mode

##        ###

##        # End of create_harvesting_config.
##        return config_contents

    ##########

    def write_crab_config(self):
        """Write a CRAB job configuration Python file.

        """

        self.logger.info("Writing CRAB configuration...")

        file_name_base = "crab.cfg"

        # Create CRAB configuration.
        crab_contents = self.create_crab_config()

        # Write configuration to file.
        crab_file_name = file_name_base
        try:
            crab_file = file(crab_file_name, "w")
            crab_file.write(crab_contents)
            crab_file.close()
        except IOError:
            self.logger.fatal("Could not write " \
                              "CRAB configuration to file `%s'" % \
                              crab_file_name)
            raise Error("ERROR: Could not write to file `%s'!" % \
                        crab_file_name)

        # End of write_crab_config.

    ##########

    def write_multicrab_config(self):
        """Write a multi-CRAB job configuration Python file.

        """

        self.logger.info("Writing multi-CRAB configuration...")

        file_name_base = "multicrab.cfg"

        # Create multi-CRAB configuration.
        multicrab_contents = self.create_multicrab_config()

        # Write configuration to file.
        multicrab_file_name = file_name_base
        try:
            multicrab_file = file(multicrab_file_name, "w")
            multicrab_file.write(multicrab_contents)
            multicrab_file.close()
        except IOError:
            self.logger.fatal("Could not write " \
                              "multi-CRAB configuration to file `%s'" % \
                              multicrab_file_name)
            raise Error("ERROR: Could not write to file `%s'!" % \
                        multicrab_file_name)

        # End of write_multicrab_config.

    ##########

    def write_harvesting_config(self, dataset_name):
        """Write a harvesting job configuration Python file.

        NOTE: This knows nothing about single-step or two-step
        harvesting. That's all taken care of by
        create_harvesting_config.

        """

        self.logger.debug("Writing harvesting configuration for `%s'..." % \
                          dataset_name)

        # Create Python configuration.
        config_contents = self.create_harvesting_config(dataset_name)

        # Write configuration to file.
        config_file_name = self. \
                           create_harvesting_config_file_name(dataset_name)
        try:
            config_file = file(config_file_name, "w")
            config_file.write(config_contents)
            config_file.close()
        except IOError:
            self.logger.fatal("Could not write " \
                              "harvesting configuration to file `%s'" % \
                              config_file_name)
            raise Error("ERROR: Could not write to file `%s'!" % \
                        config_file_name)

        # End of write_harvesting_config.

    ##########

    def write_me_extraction_config(self, dataset_name):
        """Write an ME-extraction configuration Python file.

        This `ME-extraction' (ME = Monitoring Element) is the first
        step of the two-step harvesting.

        """

        self.logger.debug("Writing ME-extraction configuration for `%s'..." % \
                          dataset_name)

        # Create Python configuration.
        config_contents = self.create_me_extraction_config(dataset_name)

        # Write configuration to file.
        config_file_name = self. \
                           create_me_summary_config_file_name(dataset_name)
        try:
            config_file = file(config_file_name, "w")
            config_file.write(config_contents)
            config_file.close()
        except IOError:
            self.logger.fatal("Could not write " \
                              "ME-extraction configuration to file `%s'" % \
                              config_file_name)
            raise Error("ERROR: Could not write to file `%s'!" % \
                        config_file_name)

        # End of write_me_extraction_config.

    ##########

    def read_book_keeping(self):
        """Read any book keeping information if present.

        Read the book keeping information from previous runs if
        present. If the file does not exist we keep going, it will be
        created at the time we want to write out the book keeping
        information of this run.

        """

        self.logger.info("Reading book keeping information")

        file_name = self.book_keeping_file_name
        self.logger.debug("Reading book keeping information " \
                          "from previous runs from file `%s'" % \
                          file_name)

        try:
            in_file = open(file_name, "r")
            # Okay, not very safe, but this is the only way with
            # built-in Python tools to serialize something while
            # keeping it human-readable. And I _did_ do something to
            # make it less dangerous.
            for line in in_file:
                line = line.strip()
                if len(line) < 1:
                    continue
                if not line.startswith("#"):
                    tmp = eval(line, {"__builtins__": {}})
                    # DEBUG DEBUG DEBUG
                    assert type(tmp) == type(self.book_keeping_information)
                    # DEBUG DEBUG DEBUG end
                    self.book_keeping_information.update(tmp)
            in_file.close()
        except IOError, err:
            # No big deal if the file does not exist. Halt for more
            # serious problems.
            errno = err.errno
            if errno == 2:
                # This is `No such file or directory'.
                self.logger.warning("Book keeping file does not yet exist " \
                                    "(which is fine, just continue " \
                                    "with a clean slate and use it " \
                                    "for output only)")
            else:
                # Hmm, sounds more serious, let's abort.
                msg = "Could not read from book keeping file `%s'" % file_name
                self.logger.fatal(msg)
                raise Error(msg)

        self.logger.info("  found %d dataset(s) for a total of %d run(s)" % \
                         (len(self.book_keeping_information),
                          sum([len(i) for i in \
                               self.book_keeping_information.values()])))

        # End of read_book_keeping.

    ##########

    def write_book_keeping_file(self):
        """Write the book keeping for this run to file.

        Write the book keeping for this run (of the cmsHarvester) to
        file. Note that we _re_write the original file if present. But
        you never expected the cmsHarvester to be thread-safe, did
        you? ;-)

        NOTE: Since this is a point we would _always_ like to reach,
        even if an exception was thrown and even if the input was not
        good enough to even start doing anything, we have to be a bit
        careful.

        """

        # Little local helper function.
        def dump_to_screen(contents):
            sep_line = "-" * 50
            self.logger.info(sep_line)
            self.logger.info("!!! Dumping book keeping information " \
                             "to screen as backup measure: !!!")
            self.logger.info(sep_line)
            self.logger.info(contents)
            self.logger.info(sep_line)

        ###

        file_name = self.book_keeping_file_name
        self.logger.debug("Writing book keeping information to file `%s'" % \
                          file_name)

        contents_lines = []
        contents_lines.append("# %s" % self.time_stamp())
        contents_lines.append("# Created by %s" % self.ident_string())
        contents_lines.append("")
        contents_lines.append("# Format: Python dictionary with")
        contents_lines.append("# dataset name as key,")
        contents_lines.append("# dict of processed runs into number of")
        contents_lines.append("# processed events as value.")
        contents_lines.append("# Everything present in the dictionary")
        contents_lines.append("# has been processed by cmsHarvester.")
        contents_lines.append("# Admittedly this only means that the")
        contents_lines.append("# configurations were created at some point.")
        contents_lines.append("")
        contents_lines.append(repr(self.book_keeping_information))
        contents = "\n".join(contents_lines)
        try:
            out_file = open(file_name, "w")
            time_stamp = self.time_stamp()
            out_file.write("# %s\n" % time_stamp)
            out_file.write("%s\n" % contents)
            out_file.close()
        except Exception:
            # Frak! Could not do the book keeping. Whine to the user
            # and dump book keeping info to the screen. That way at
            # least the user can copy-paste things to salvage them. No
            # need to raise any exceptions here after that.
            msg = "Could not write book keeping information to file `%s'" % \
                  file_name
            self.logger.error(msg)
            # Dump book keeping information to the screen.
            dump_to_screen(contents)

        # End of write_book_keeping_file.

    ##########

    def build_datasets_information(self):
        """Obtain all information on the datasets that we need to run.

        Use DBS to figure out all required information on our
        datasets, like the run numbers and the GlobalTag. All
        information is stored in the datasets_information member
        variable.

        """

        # Get a list of runs in the dataset.
        # NOTE: The harvesting has to be done run-by-run, so we
        # split up datasets based on the run numbers. Strictly
        # speaking this is not (yet?) necessary for Monte Carlo
        # since all those samples use run number 1. Still, this
        # general approach should work for all samples.

        # Now loop over all datasets in the list and process them.
        # NOTE: This processing has been split into several loops
        # to be easier to follow, sacrificing a bit of efficiency.
        self.datasets_information = {}
        self.logger.info("Collecting information for all datasets to process")
        dataset_names = self.datasets_to_use.keys()
        dataset_names.sort()
        for dataset_name in dataset_names:

            # Tell the user which dataset: nice with many datasets.
            sep_line = "-" * 30
            self.logger.info(sep_line)
            self.logger.info("  `%s'" % dataset_name)
            self.logger.info(sep_line)

            runs = self.dbs_resolve_runs(dataset_name)
            self.logger.info("    found %d run(s)" % len(runs))
            if len(runs) > 0:
                self.logger.debug("      run number(s): %s" % \
                                  ", ".join([str(i) for i in runs]))
            else:
                # DEBUG DEBUG DEBUG
                # This should never happen after the DBS checks.
                self.logger.warning("  --> skipping dataset "
                                    "without any runs")
                assert False
                # DEBUG DEBUG DEBUG end

            cmssw_version = self.dbs_resolve_cmssw_version(dataset_name)
            self.logger.info("    found CMSSW version `%s'" % cmssw_version)

            # Figure out if this is data or MC.
            datatype = self.dbs_resolve_datatype(dataset_name)
            self.logger.info("    sample is data or MC? --> %s" % \
                             datatype)

            # Try and figure out the GlobalTag to be used.
            if self.globaltag is None:
                globaltag = self.dbs_resolve_globaltag(dataset_name)
            else:
                globaltag = self.globaltag

            self.logger.info("    found GlobalTag `%s'" % globaltag)

            # DEBUG DEBUG DEBUG
            if globaltag == "":
                # Actually we should not even reach this point, after
                # our dataset sanity checks.
                assert datatype == "data", \
                       "ERROR Empty GlobalTag for MC dataset!!!"
            # DEBUG DEBUG DEBUG end

            # DEBUG DEBUG DEBUG
            #tmp = self.dbs_check_dataset_spread_old(dataset_name)
            # DEBUG DEBUG DEBUG end
            sites_catalog = self.dbs_check_dataset_spread(dataset_name)

            # Extract the total event counts.
            num_events = {}
            for run_number in sites_catalog.keys():
                num_events[run_number] = sites_catalog \
                                         [run_number]["all_sites"]
                del sites_catalog[run_number]["all_sites"]

            # Extract the information about whether or not datasets
            # are mirrored.
            mirror_catalog = {}
            for run_number in sites_catalog.keys():
                mirror_catalog[run_number] = sites_catalog \
                                             [run_number]["mirrored"]
                del sites_catalog[run_number]["mirrored"]

            # BUG BUG BUG
            # I think I could now get rid of that and just fill the
            # "sites" entry with the `inverse' of this
            # num_events_catalog(?).
            #num_sites = self.dbs_resolve_dataset_number_of_sites(dataset_name)
            #sites_catalog = self.dbs_check_dataset_spread(dataset_name)
            #sites_catalog = dict(zip(num_events_catalog.keys(),
            #                         [[j for i in num_events_catalog.values() for j in i.keys()]]))
            # BUG BUG BUG end

##            # DEBUG DEBUG DEBUG
##            # This is probably only useful to make sure we don't muck
##            # things up, right?
##            # Figure out across how many sites this sample has been spread.
##            if num_sites == 1:
##                self.logger.info("    sample is contained at a single site")
##            else:
##                self.logger.info("    sample is spread across %d sites" % \
##                                 num_sites)
##            if num_sites < 1:
##                # NOTE: This _should not_ happen with any valid dataset.
##                self.logger.warning("  --> skipping dataset which is not " \
##                                    "hosted anywhere")
##            # DEBUG DEBUG DEBUG end

            # Now put everything in a place where we can find it again
            # if we need it.
            self.datasets_information[dataset_name] = {}
            self.datasets_information[dataset_name]["runs"] = runs
            self.datasets_information[dataset_name]["cmssw_version"] = \
                                                                     cmssw_version
            self.datasets_information[dataset_name]["globaltag"] = globaltag
            self.datasets_information[dataset_name]["datatype"] = datatype
            self.datasets_information[dataset_name]["num_events"] = num_events
            self.datasets_information[dataset_name]["mirrored"] = mirror_catalog
            self.datasets_information[dataset_name]["sites"] = sites_catalog

            # Each run of each dataset has a different CASTOR output
            # path.
            castor_path_common = self.create_castor_path_name_common(dataset_name)
            self.logger.info("    output will go into `%s'" % \
                             castor_path_common)

            castor_paths = dict(zip(runs,
                                    [self.create_castor_path_name_special(dataset_name, i, castor_path_common) \
                                     for i in runs]))
            for path_name in castor_paths.values():
                self.logger.debug("      %s" % path_name)
            self.datasets_information[dataset_name]["castor_path"] = \
                                                                   castor_paths

        # End of build_datasets_information.

    ##########

    def show_exit_message(self):
        """Tell the user what to do now, after this part is done.

        This should provide the user with some (preferably
        copy-pasteable) instructions on what to do now with the setups
        and files that have been created.

        """

        # TODO TODO TODO
        # This could be improved a bit.
        # TODO TODO TODO end

        sep_line = "-" * 60

        self.logger.info("")
        self.logger.info(sep_line)
        self.logger.info("  Configuration files have been created.")
        self.logger.info("  From here on please follow the usual CRAB instructions.")
        self.logger.info("  Quick copy-paste instructions are shown below.")
        self.logger.info(sep_line)

        self.logger.info("")
        self.logger.info("    Create all CRAB jobs:")
        self.logger.info("      multicrab -create")
        self.logger.info("")
        self.logger.info("    Submit all CRAB jobs:")
        self.logger.info("      multicrab -submit")
        self.logger.info("")
        self.logger.info("    Check CRAB status:")
        self.logger.info("      multicrab -status")
        self.logger.info("")

        self.logger.info("")
        self.logger.info("  For more information please see the CMS Twiki:")
        self.logger.info("    %s" % twiki_url)
        self.logger.info(sep_line)

        # End of show_exit_message.

    ##########

    def run(self):
        "Main entry point of the CMS harvester."

        # Start with a positive thought.
        exit_code = 0

        try:

            try:

                # Parse all command line options and arguments
                self.parse_cmd_line_options()
                # and check that they make sense.
                self.check_input_status()

                # Check if CMSSW is setup.
                self.check_cmssw()

                # Check if DBS is setup,
                self.check_dbs()
                # and if all is fine setup the Python side.
                self.setup_dbs()

                # Obtain list of dataset names to consider
                self.build_dataset_use_list()
                # and the list of dataset names to ignore.
                self.build_dataset_ignore_list()

                # Read book keeping file. This _could_ contain a list
                # of things we have already done previously, so we
                # want to skip those.
                self.read_book_keeping()

                # Process the list of datasets to ignore and fold that
                # into the list of datasets to consider.
                self.process_dataset_ignore_list()

                # Obtain all required information on the datasets,
                # like run numbers and GlobalTags.
                self.build_datasets_information()

                # TODO TODO TODO
                # Need to think about where this should go, but
                # somewhere we have to move over the fact that we want
                # to process all runs for each dataset that we're
                # considering. This basically means copying over the
                # information from self.datasets_information[]["runs"]
                # to self.datasets_to_use[].
                for dataset_name in self.datasets_to_use.keys():
                    self.datasets_to_use[dataset_name] = self.datasets_information[dataset_name]["runs"]
                # TODO TODO TODO end

                # Process the datasets and runs that we have already
                # done according to the book keeping.
                self.process_book_keeping()

                # If we've been asked to sacrifice some parts of
                # spread-out samples in order to be able to partially
                # harvest them, we'll do that here.
                if self.harvesting_mode == "single-step-allow-partial":
                    self.singlify_datasets()

                # Check dataset name(s)
                self.check_dataset_list()
                # and see if there is anything left to do.
                if len(self.datasets_to_use) < 1:
                    self.logger.info("No datasets (left?) to process")
                else:

                    self.logger.info("After all checks etc. we are left " \
                                     "with %d dataset(s) to process " \
                                     "for a total of %d runs" % \
                                     (len(self.datasets_to_use),
                                      sum([len(i) for i in \
                                           self.datasets_to_use.values()])))

                    # NOTE: The order in which things are done here is
                    # important. At the end of the job, independent on
                    # how it ends (exception, CTRL-C, normal end) the
                    # book keeping is written to file. At that time it
                    # should be clear which jobs are done and can be
                    # submitted. This means we first create the
                    # general files, and then the per-job config
                    # files.

                    # TODO TODO TODO
                    # It would be good to modify the book keeping a
                    # bit. Now we write the crab.cfg (which is the
                    # same for all samples and runs) and the
                    # multicrab.cfg (which contains blocks for all
                    # runs of all samples) without updating our book
                    # keeping. The only place we update the book
                    # keeping is after writing the harvesting config
                    # file for a given dataset. Since there is only
                    # one single harvesting configuration for each
                    # dataset, we have no book keeping information on
                    # a per-run basis.
                    # TODO TODO TODO end

                    # Check if the CASTOR output area exists. If
                    # necessary create it.
                    self.create_and_check_castor_dirs()

                    # Create one crab and one multicrab configuration
                    # for all jobs together.
                    self.write_crab_config()
                    self.write_multicrab_config()

                    # Loop over all datasets and create harvesting
                    # config files for all of them. One harvesting
                    # config per dataset is enough. The same file will
                    # be re-used by CRAB for each run.
                    # NOTE: We always need a harvesting
                    # configuration. For the two-step harvesting we
                    # also need a configuration file for the first
                    # step: the monitoring element extraction.
                    for dataset_name in self.datasets_to_use.keys():
                        try:
                            self.write_harvesting_config(dataset_name)
                            if self.harvesting_mode == "two-step":
                                self.write_me_extraction_config(dataset_name)
                        except:
                            # Doh! Just re-raise the damn thing.
                            raise
                        else:
                            tmp = self.datasets_information[dataset_name] \
                                  ["num_events"]
                            if self.book_keeping_information. \
                                   has_key(dataset_name):
                                self.book_keeping_information[dataset_name].update(tmp)
                            else:
                                self.book_keeping_information[dataset_name] = tmp

                    # Explain the user what to do now.
                    self.show_exit_message()

            except Usage, err:
                # self.logger.fatal(err.msg)
                # self.option_parser.print_help()
                pass

            except Error, err:
                # self.logger.fatal(err.msg)
                exit_code = 1

            except Exception, err:
                # Hmmm, ignore keyboard interrupts from the
                # user. These are not a `serious problem'. We also
                # skip SystemExit, which is the exception thrown when
                # one calls sys.exit(). This, for example, is done by
                # the option parser after calling print_help(). We
                # also have to catch all `no such option'
                # complaints. Everything else we catch here is a
                # `serious problem'.
                if isinstance(err, SystemExit):
                    self.logger.fatal(err.code)
                elif not isinstance(err, KeyboardInterrupt):
                    self.logger.fatal("!" * 50)
                    self.logger.fatal("  This looks like a serious problem.")
                    self.logger.fatal("  If you are sure you followed all " \
                                      "instructions")
                    self.logger.fatal("  please copy the below stack trace together")
                    self.logger.fatal("  with a description of what you were doing to")
                    self.logger.fatal("  jeroen.hegeman@cern.ch.")
                    self.logger.fatal("  %s" % self.ident_string())
                    self.logger.fatal("!" * 50)
                    self.logger.fatal(str(err))
                    import traceback
                    traceback_string = traceback.format_exc()
                    for line in traceback_string.split("\n"):
                        self.logger.fatal(line)
                    self.logger.fatal("!" * 50)
                    exit_code = 2

        # This is the stuff that we should really do, no matter
        # what. Of course cleaning up after ourselves is also done
        # from this place.  This alsokeeps track of the book keeping
        # so far. (This means that if half of the configuration files
        # were created before e.g. the disk was full, we should still
        # have a consistent book keeping file.
        finally:

            # The only reason not to write any book keeping
            # information is if there is none. This has the benefit of
            # making sure that if an exception was raised while trying
            # to read the original book keeping file, we don't mess up
            # by trying to access that file again to write to it.
            if len(self.book_keeping_information) > 0:
                self.write_book_keeping_file()

            self.cleanup()

        ###

        # End of run.
        return exit_code

    # End of CMSHarvester.

###########################################################################
## Main entry point.
###########################################################################

if __name__ == "__main__":
    "Main entry point for harvesting."

    CMSHarvester().run()

    # Done.

###########################################################################