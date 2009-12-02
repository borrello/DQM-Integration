import FWCore.ParameterSet.Config as cms

process = cms.Process("SiStrpDQMLive")

process.MessageLogger = cms.Service("MessageLogger",
    debugModules = cms.untracked.vstring('siStripDigis', 
                                         'siStripClusters', 
                                         'siStripZeroSuppression', 
                                         'SiStripClusterizer'),
    cout = cms.untracked.PSet(threshold = cms.untracked.string('ERROR')),
    destinations = cms.untracked.vstring('cout')
)

#----------------------------
# Event Source
#-----------------------------
process.load("DQM.Integration.test.inputsource_cfi")
process.EventStreamHttpReader.consumerName = 'SiStrip DQM Consumer'
process.EventStreamHttpReader.SelectEvents = cms.untracked.PSet(SelectEvents = cms.vstring('HLT_MinBia*','HLT_L1*','HLT_TrackerCosmics'))
#process.EventStreamHttpReader.sourceURL = cms.string('http://srv-c2c05-07.cms:22100/urn:xdaq-application:lid=30')

#----------------------------
# DQM Environment
#-----------------------------
process.load("DQMServices.Core.DQM_cfg")
process.DQMStore.referenceFileName = '/dqmdata/dqm/reference/sistrip_reference.root'
process.DQM.filter = '^(SiStrip|Tracking)(/[^/]+){0,5}$'

process.load("DQMServices.Components.DQMEnvironment_cfi")

#----------------------------
# DQM Live Environment
#-----------------------------
process.load("DQM.Integration.test.environment_cfi")
process.dqmEnv.subSystemFolder    = "SiStrip"
process.dqmSaver.producer = "Playback"
process.dqmSaver.saveByTime = 16
process.dqmSaver.saveByMinute = 16

process.dqmEnvTr = cms.EDFilter("DQMEventInfo",
                 subSystemFolder = cms.untracked.string('Tracking'),
                 eventRateWindow = cms.untracked.double(0.5),
                 eventInfoFolder = cms.untracked.string('EventInfo')
)

#-----------------------------
# Magnetic Field
#-----------------------------
# 0T field
#process.load("Configuration.StandardSequences.MagneticField_0T_cff")
# 3.8T field
#process.load("Configuration.StandardSequences.MagneticField_38T_cff")
# 4.0T field
#process.load("Configuration.StandardSequences.MagneticField_40T_cff")
#process.prefer("VolumeBasedMagneticFieldESProducer")

process.load('Configuration.StandardSequences.MagneticField_AutoFromDBCurrent_cff')

#-------------------------------------------------
# GEOMETRY
#-------------------------------------------------
process.load("Configuration.StandardSequences.Geometry_cff")

#--------------------------
# Calibration
#--------------------------
process.load("DQM.Integration.test.FrontierCondition_GT_cfi")
#--------------------------------------------
## Patch to avoid using Run Info information in reconstruction
#
process.siStripQualityESProducer.ListOfRecordToMerge = cms.VPSet(
   cms.PSet( record = cms.string("SiStripDetVOffRcd"),    tag    = cms.string("") ),
   cms.PSet( record = cms.string("SiStripDetCablingRcd"), tag    = cms.string("") ),
#  cms.PSet( record = cms.string("RunInfoRcd"),           tag    = cms.string("") ),
   cms.PSet( record = cms.string("SiStripBadChannelRcd"), tag    = cms.string("") ),
   cms.PSet( record = cms.string("SiStripBadFiberRcd"),   tag    = cms.string("") ),
   cms.PSet( record = cms.string("SiStripBadModuleRcd"),  tag    = cms.string("") )
   )
#-------------------------------------------
                                                                                           
#-----------------------
#  Reconstruction Modules
#-----------------------
## Collision Reconstruction
process.load("Configuration.StandardSequences.RawToDigi_Data_cff")
process.load("Configuration.StandardSequences.Reconstruction_cff")

# offline beam spot
process.load("RecoVertex.BeamSpotProducer.BeamSpot_cff")

#--------------------------
# Strip DQM Source and Client
#--------------------------
process.load("DQM.SiStripMonitorClient.SiStripSourceConfigP5_cff")

# Switching Off Digi/Cluster profiles temprarily
process.SiStripMonitorDigi.TProfTotalNumberOfDigis.subdetswitchon = False
process.SiStripMonitorClusterReal.TProfTotalNumberOfClusters.subdetswitchon = False

process.load("DQM.SiStripMonitorClient.SiStripSourceConfigHVOff_cff")
process.load("DQM.SiStripMonitorClient.SiStripClientConfigP5_cff")
process.SiStripAnalyser.TkMapCreationFrequency  = -1
process.SiStripAnalyser.ShiftReportFrequency = -1

#--------------------------
# Quality Test
#--------------------------
process.qTester = cms.EDFilter("QualityTester",
    qtList = cms.untracked.FileInPath('DQM/SiStripMonitorClient/data/sistrip_qualitytest_config.xml'),
    prescaleFactor = cms.untracked.int32(1),                               
    getQualityTestsFromFile = cms.untracked.bool(True)
)

#--------------------------
# Web Service
#--------------------------
process.ModuleWebRegistry = cms.Service("ModuleWebRegistry")

process.AdaptorConfig = cms.Service("AdaptorConfig")

#--------------------------
# Filters
#--------------------------
# HLT Filter
process.load("HLTrigger.special.HLTTriggerTypeFilter_cfi")
# 0=random, 1=physics, 2=calibration, 3=technical
process.hltTriggerTypeFilter.SelectedTriggerType = 1

# Global Trigger *L1GlobalTrigger) Selection for PhysicsON
process.physicsBitSelector = cms.EDFilter("PhysDecl",
                                                   applyfilter = cms.untracked.bool(True),
                                                   debugOn     = cms.untracked.bool(False)
                                          )
# L1 Trigger Bit Selection (bit 40 and 41 for BSC trigger)
process.load('L1TriggerConfig.L1GtConfigProducers.L1GtTriggerMaskTechTrigConfig_cff')
process.load('HLTrigger/HLTfilters/hltLevel1GTSeed_cfi')
process.hltLevel1GTSeed.L1TechTriggerSeeding = cms.bool(True)
process.hltLevel1GTSeed.L1SeedsLogicalExpression = cms.string('40 OR 41')

#--------------------------
# Scheduling
#--------------------------
process.SiStripSources_HVOff     = cms.Sequence(process.SiStripMonitorDigiHVOff*process.SiStripMonitorClusterHVOff)
process.SiStripSources_LocalReco = cms.Sequence(process.siStripFEDMonitor*process.SiStripMonitorDigi*process.SiStripMonitorClusterReal)
process.SiStripSources_TrkReco   = cms.Sequence(process.SiStripMonitorTrack_gentk*process.MonitorTrackResiduals_gentk*process.TrackMon_gentk)
process.SiStripClients           = cms.Sequence(process.SiStripAnalyser)
process.DQMCommon                = cms.Sequence(process.qTester*process.dqmEnv*process.dqmEnvTr*process.dqmSaver)
process.RecoForDQM_LocalReco     = cms.Sequence(process.siPixelDigis*process.siStripDigis*process.gtDigis*process.trackerlocalreco)
process.RecoForDQM_TrkReco       = cms.Sequence(process.offlineBeamSpot*process.recopixelvertexing*process.ckftracks)
process.p = cms.Path(process.RecoForDQM_LocalReco*
                                          process.DQMCommon*
                                          process.SiStripClients*
                                          process.SiStripSources_HVOff*
                                          process.physicsBitSelector*
                                          process.SiStripSources_LocalReco*
                                          process.hltLevel1GTSeed*
                                          process.RecoForDQM_TrkReco*
                                          process.SiStripSources_TrkReco)

