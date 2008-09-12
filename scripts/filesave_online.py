#! /usr/bin/env python

import os,time,sys,shutil,stat,glob
from sets import Set
from ROOT import TFile

def filecheck(rootfile):
	f = TFile(rootfile)
	if (f.IsZombie()):
		#print "File corrupted"
		f.Close()
		return 0
	else:
		hist = f.FindObjectAny("reportSummaryContents")
		if (hist == None):
			#print "File is incomplete"
			f.Close()
			return 0
		else:
			#print "File is OK"
			f.Close()
			return 1


def copy2dropbox(org,tmp,final):
	#server = 'srv-c2c06-02' #machine to which files are transfered
	server = 'srv-c2d17-02' #machine to which files are transfered (2008-07-29)
	#file_stats = os.stat(org)
	#t1 = time.localtime(file_stats[stat.ST_CTIME])[0:5]
	#t2 = time.localtime()[0:5]
	#while t1 == t2:
		#print t1, t2
		#print 'waiting for file creation is completed...'
		#time.sleep(60)
		#t2 = time.localtime()[0:5]
	### copy files to stealth area on cmsmon and move to final area
	os.popen('scp '+org+' '+server+':'+tmp).read()
	os.popen('ssh '+server+' -t mv '+tmp+' '+final).read()

		
def convert(infile, ofile):
	exedir = '/cms/mon/data/dqm/filereg'
	cmd = exedir + '/convert.sh ' + infile + ' ' +ofile
	os.system(cmd)


DIR = '/home/dqmprolocal/output'  #directory to search new files
TMPDIR = '/cms/mon/data/.dropbox_tmp' # stealth area on cmsmon
FILEDIR = '/cms/mon/data/dropbox' # directory, to which files are stored
TimeTag = '/home/dqmprolocal/output/timetag' #file for time tag for searching new file

### Fore test and development
#DIR = '/cms/mon/data/dqm/filereg_test/output'  #directory to search new files
#TMPDIR = '/cms/mon/data/dqm/filereg_test/output-tmp' # stealth area on cmsmon
#FILEDIR = '/cms/mon/data/dropbox_test' # directory, to which files are stored
#TimeTag = DIR+'/timetag' #file for time tag for searching new file

WAITTIME = 120 # waiting time for new files (sec)

#os.popen('rm '+TMPDIR+'/DQM*')  # clean up temporary directory when start
TempTag = TimeTag + '-tmp'
if not os.path.exists(TimeTag):
        os.system('touch -t 01010000 '+ TimeTag)



####### ENDLESS LOOP WITH SLEEP
while 1:
    #### search new tag files
    #NEW_ = os.popen('find '+ DIR +'/ -type f -name "DQM_*_R?????????.root" -newer '+ TimeTag).read().split()
    NEW_ = os.popen('find '+ DIR +'/ -type f -name "tagfile_runend_?????_*" -newer '+ TimeTag).read().split()
    
    if len(NEW_)==0:
        print 'waiting for new files...'
        time.sleep(WAITTIME)
        continue

    os.system('touch '+ TempTag)

    #print 'Found '+str(len(NEW_))+' new file(s).'
    #print os.popen('ls -l '+TimeTag).read()

    #### sort tag files by run number
    pairs = []
    for tagfile in NEW_:
	    i = tagfile.find('/tagfile_runend_')
	    run = tagfile[i+16:i+21] #run number of new tagfile
	    pairs.append((run,tagfile))
    pairs.sort()

    #### extract uniq runs
    Runs = []
    for pair in pairs:
	    Runs.append(pair[0])
    UniqRuns = list(Set(Runs)) #remove duplicate run
    UniqRuns.sort()
		
    #### extract new files & copy to dropbox
    for run in UniqRuns:#loop for runs
	    subfiles = []
	    subfiles = glob.glob(DIR + '/DQM_*_R????' + run + '_T*.root')
	    playbacks = glob.glob(DIR + '/Playback*SiStrip_R????' + run + '_T*.root')
	    subfiles = subfiles + playbacks

	    ## extract head of file name (ex.'/home/dqmprolocal/output/DQM_SiStrip')
	    fheads = []
	    for fname in subfiles:
		    i = fname.rfind('_R')
		    fhead = fname[:i]
		    fheads.append(fhead)
	    UniqHeads = list(Set(fheads))

	    ## extract single good file for single subsys
	    for fhead in UniqHeads:
		    fname = fhead +'_R0000'+run+'.root'
		    fname_Ts = os.popen('ls -rt '+fhead+'_R????'+run+'_T*.root').read().split()
		    if os.path.exists(fname): fname_Ts.append(fname)
		    
		    numbers = range(len(fname_Ts))
		    numbers.reverse()
		    for i in numbers:
			    fname_T = fname_Ts[i]
			    if filecheck(fname_T) == 0:
				    print fname_T +' is incomplete'
			    else:
				    print fname_T +' is OK'
				    ### For SiStrip files
				    if fname_T.rfind('Playback') != -1:
					    dqmfile = fname_T.replace('Playback','DQM')
					    convert(fname_T,dqmfile)
					    fname_T = dqmfile
					    fname = fname.replace('Playback','DQM')
					    
				    tmpfile = fname.replace(fname[:fname.find('/DQM_')],TMPDIR)
				    file = fname.replace(fname[:fname.find('/DQM_')],FILEDIR)
				    copy2dropbox(fname_T,tmpfile,file)
				    #if not fname_T == fname:
					    #shutil.copy2(fname_T,fname)
				    break								    

    shutil.copy2(TempTag,TimeTag)
    
