import FWCore.ParameterSet.Config as cms

process = cms.Process("DQM")
process.options = cms.untracked.PSet(
  SkipEvent = cms.untracked.vstring('ProductNotFound') 
)

#### leave the following few lines uncommented for online running
process.load("DQM.Integration.test.inputsource_cfi")
process.load("DQM.Integration.test.environment_cfi")
process.EventStreamHttpReader.SelectHLTOutput = cms.untracked.string('hltOutputHLTDQMResults')
process.EventStreamHttpReader.maxEventRequestRate = cms.untracked.double(1000.0)
process.EventStreamHttpReader.consumerName = 'HLTTrigerResults DQM Consumer'

#### end first online running section

############ Test offline running


# process.source = cms.Source("PoolSource",
#                                 fileNames = cms.untracked.vstring('file:/data/ndpc0/b/slaunwhj/rawData/June/0091D91D-D19B-E011-BDCE-001D09F2512C.root')
#                             )

# process.maxEvents = cms.untracked.PSet(
#         input = cms.untracked.int32(-1)
#         )

##############################


# old, not used
#process.EventStreamHttpReader.sourceURL = cms.string('http://srv-c2c07-13.cms:11100/urn:xdaq-application:lid=50')


process.load("DQMServices.Core.DQM_cfg")

# old, not used
#process.DQMStore.referenceFileName = "/dqmdata/dqm/reference/hlt_reference.root"

process.load("DQMServices.Components.DQMEnvironment_cfi")

###  remove for online running
#process.dqmSaver.dirName = '.'
###  end remove section 

process.dqmSaver.version = 2
process.dqmSaver.saveByRun = 1
process.dqmSaver.saveByMinute = -1
process.dqmSaver.saveByLumiSection = -1
process.dqmSaver.saveByTime = -1
#process.load("Configuration.StandardSequences.GeometryPilot2_cff")
#process.load("Configuration.StandardSequences.MagneticField_cff")
#process.GlobalTrackingGeometryESProducer = cms.ESProducer( "GlobalTrackingGeometryESProducer" ) # for muon hlt dqm
#SiStrip Local Reco
#process.SiStripDetInfoFileReader = cms.Service("SiStripDetInfoFileReader")
#process.TkDetMap = cms.Service("TkDetMap")

#---- for P5 (online) DB access
process.load("DQM.Integration.test.FrontierCondition_GT_cfi")

#---- for offline DB access
#process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')
#process.GlobalTag.globaltag = 'GR_E_V19::All'



################################
#
# Need to do raw to digi
# in order to use PS providers
#
# This is a hassle
# but I will try it
# following lines are only for
# running the silly RawToDigi
#
################################
process.load('Configuration.StandardSequences.Geometry_cff')
process.load('Configuration/StandardSequences/RawToDigi_Data_cff')

process.SiStripDetInfoFileReader = cms.Service("SiStripDetInfoFileReader")
process.TkDetMap = cms.Service("TkDetMap")

process.load("DQM.HLTEvF.TrigResRateMon_cfi")

# run on 1 out of 8 SM, LSSize 23 -> 23/8 = 2.875
# stream is prescaled by 10, to correct change LSSize 23 -> 23/10 = 2.3
process.trRateMon.LuminositySegmentSize = cms.untracked.double(2.3)


# Add RawToDigi
process.p = cms.EndPath(process.RawToDigi*process.trRateMon)


process.pp = cms.Path(process.dqmEnv+process.dqmSaver)

process.dqmEnv.subSystemFolder = 'HLT/TrigResults'
#process.hltResults.plotAll = True

