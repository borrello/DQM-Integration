import FWCore.ParameterSet.Config as cms

process = cms.Process("ECALDQM")

process.load("DQM.Integration.test.inputsource_playback_cfi")

process.load("DQMServices.Core.DQM_cfg")

process.load("DQMServices.Components.DQMEnvironment_cfi")

process.load("DQM.Integration.test.environment_playback_cfi")
#process.DQMStore.referenceFileName = '/home/dqmdevlocal/reference/DQM_EcalEndcap_R000046798.root'

process.load("EventFilter.EcalRawToDigiDev.EcalUnpackerMapping_cfi")

process.load("EventFilter.EcalRawToDigiDev.EcalUnpackerData_cfi")

process.load("EventFilter.L1GlobalTriggerRawToDigi.l1GtEvmUnpack_cfi")

process.load("L1TriggerConfig.L1GtConfigProducers.L1GtConfig_cff")

import RecoLocalCalo.EcalRecProducers.ecalFixedAlphaBetaFitUncalibRecHit_cfi
process.ecalUncalibHit2 = RecoLocalCalo.EcalRecProducers.ecalFixedAlphaBetaFitUncalibRecHit_cfi.ecalFixedAlphaBetaFitUncalibRecHit.clone()

import RecoLocalCalo.EcalRecProducers.ecalWeightUncalibRecHit_cfi
process.ecalUncalibHit = RecoLocalCalo.EcalRecProducers.ecalWeightUncalibRecHit_cfi.ecalWeightUncalibRecHit.clone()

process.load("RecoLocalCalo.EcalRecProducers.ecalRecHit_cfi")

process.load("Geometry.CaloEventSetup.CaloGeometry_cfi")

process.load("Geometry.CaloEventSetup.CaloTopology_cfi")

process.load("Geometry.CaloEventSetup.EcalTrigTowerConstituents_cfi")

process.load("Geometry.CMSCommonData.cmsIdealGeometryXML_cfi")

process.load("Geometry.EcalMapping.EcalMapping_cfi")

process.load("Geometry.EcalMapping.EcalMappingRecord_cfi")

process.load("DQM.EcalEndcapMonitorModule.EcalEndcapMonitorModule_cfi")

process.load("DQM.EcalEndcapMonitorTasks.EcalEndcapMonitorTasks_cfi")

process.load("SimCalorimetry.EcalTrigPrimProducers.ecalTriggerPrimitiveDigis_cff")

process.load("DQM.EcalEndcapMonitorClient.EcalEndcapMonitorClient_cfi")

process.load("RecoEcal.EgammaClusterProducers.ecalClusteringSequence_cff")

process.load("CalibCalorimetry.EcalLaserCorrection.ecalLaserCorrectionService_cfi")

process.load("HLTrigger.special.TriggerTypeFilter_cfi")

process.load("FWCore.Modules.preScaler_cfi")

process.ecalPrescaler = cms.EDFilter("EcalMonitorPrescaler",
    EcalRawDataCollection = cms.InputTag("ecalEBunpacker"),
    laserPrescaleFactor = cms.untracked.int32(1),
    ledPrescaleFactor = cms.untracked.int32(1),
    pedestalPrescaleFactor = cms.untracked.int32(1),
    testpulsePrescaleFactor = cms.untracked.int32(1)
)

process.triggerTypeFilter.SelectedTriggerType = 1

process.dqmQTestEE = cms.EDAnalyzer("QualityTester",
#    reportThreshold = cms.untracked.string('red'),
    prescaleFactor = cms.untracked.int32(4),
    qtList = cms.untracked.FileInPath('DQM/Integration/test/EcalEndcapQualityTests.xml'),
    getQualityTestsFromFile = cms.untracked.bool(True)
)

process.load("Configuration.StandardSequences.FrontierConditions_GlobalTag_cff")
process.GlobalTag.connect = "frontier://(proxyurl=http://localhost:3128)(serverurl=http://frontier1.cms:8000/FrontierOnProd)(serverurl=http://frontier2.cms:8000/FrontierOnProd)(retrieve-ziplevel=0)/CMS_COND_21X_GLOBALTAG"
process.GlobalTag.globaltag = "CRAFT_V14H::All"
process.prefer("GlobalTag")

process.MessageLogger = cms.Service("MessageLogger",
    cout = cms.untracked.PSet(
        threshold = cms.untracked.string('WARNING'),
        noLineBreaks = cms.untracked.bool(True),
        noTimeStamps = cms.untracked.bool(True),
        default = cms.untracked.PSet(
            limit = cms.untracked.int32(0)
        ),
        EcalRawToDigiDev = cms.untracked.PSet(
            limit = cms.untracked.int32(1000)
        ),
        EcalRawToDigiDevTriggerType = cms.untracked.PSet(
            limit = cms.untracked.int32(1000)
        ),
        EcalRawToDigiDevTpg = cms.untracked.PSet(
            limit = cms.untracked.int32(1000)
        ),
        EcalRawToDigiDevNumTowerBlocks = cms.untracked.PSet(
            limit = cms.untracked.int32(1000)
        ),
        EcalRawToDigiDevTowerId = cms.untracked.PSet(
            limit = cms.untracked.int32(1000)
        ),
        EcalRawToDigiDevTowerSize = cms.untracked.PSet(
            limit = cms.untracked.int32(1000)
        ),
        EcalRawToDigiDevChId = cms.untracked.PSet(
            limit = cms.untracked.int32(1000)
        ),
        EcalRawToDigiDevGainZero = cms.untracked.PSet(
            limit = cms.untracked.int32(1000)
        ),
        EcalRawToDigiDevGainSwitch = cms.untracked.PSet(
            limit = cms.untracked.int32(1000)
        ),
        EcalRawToDigiDevDccBlockSize = cms.untracked.PSet(
            limit = cms.untracked.int32(1000)
        ),
        EcalRawToDigiDevMemBlock = cms.untracked.PSet(
            limit = cms.untracked.int32(1000)
        ),
        EcalRawToDigiDevMemTowerId = cms.untracked.PSet(
            limit = cms.untracked.int32(1000)
        ),
        EcalRawToDigiDevMemChId = cms.untracked.PSet(
            limit = cms.untracked.int32(1000)
        ),
        EcalRawToDigiDevMemGain = cms.untracked.PSet(
            limit = cms.untracked.int32(1000)
        ),
        EcalRawToDigiDevTCC = cms.untracked.PSet(
            limit = cms.untracked.int32(1000)
        ),
        EcalRawToDigiDevSRP = cms.untracked.PSet(
            limit = cms.untracked.int32(1000)
        ),
        EcalDCCHeaderRuntypeDecoder = cms.untracked.PSet(
            limit = cms.untracked.int32(1000)
        ),
        EcalBarrelMonitorModule = cms.untracked.PSet(
            limit = cms.untracked.int32(1000)
        ),
        EcalEndcapMonitorModule = cms.untracked.PSet(
            limit = cms.untracked.int32(1000)
        )
    ),
    categories = cms.untracked.vstring('EcalRawToDigiDev',
                                       'EcalRawToDigiDevTriggerType',
                                       'EcalRawToDigiDevTpg',
                                       'EcalRawToDigiDevNumTowerBlocks',
                                       'EcalRawToDigiDevTowerId',
                                       'EcalRawToDigiDevTowerSize',
                                       'EcalRawToDigiDevChId',
                                       'EcalRawToDigiDevGainZero',
                                       'EcalRawToDigiDevGainSwitch',
                                       'EcalRawToDigiDevDccBlockSize',
                                       'EcalRawToDigiDevMemBlock',
                                       'EcalRawToDigiDevMemTowerId',
                                       'EcalRawToDigiDevMemChId',
                                       'EcalRawToDigiDevMemGain',
                                       'EcalRawToDigiDevTCC',
                                       'EcalRawToDigiDevSRP',
                                       'EcalDCCHeaderRuntypeDecoder',
                                       'EcalBarrelMonitorModule',
                                       'EcalEndcapMonitorModule'),
    destinations = cms.untracked.vstring('cout')
)

process.ModuleWebRegistry = cms.Service("ModuleWebRegistry")

process.preScaler.prescaleFactor = 1

process.ecalDataSequence = cms.Sequence(process.preScaler*process.ecalEBunpacker*process.l1GtEvmUnpack*process.ecalUncalibHit*process.ecalUncalibHit2*process.ecalRecHit*process.simEcalTriggerPrimitiveDigis)

process.ecalEndcapMonitorSequence = cms.Sequence(process.ecalEndcapMonitorModule*process.dqmEnv*process.ecalEndcapMonitorClient*process.dqmQTestEE)

process.ecalEndcapCosmicTasksSequenceP5 = cms.Sequence(process.ecalEndcapOccupancyTask*process.ecalEndcapIntegrityTask*process.ecalEndcapStatusFlagsTask*process.ecalEndcapSelectiveReadoutTask*process.ecalEndcapRawDataTask*process.ecalEndcapLaserTask*process.ecalEndcapLedTask*process.ecalEndcapPedestalOnlineTask*process.ecalEndcapPedestalTask*process.ecalEndcapTestPulseTask*process.ecalEndcapTriggerTowerTask*process.ecalEndcapTimingTask*process.ecalEndcapCosmicTask)

process.ecalEndcapCosmicTasksSequenceP5.remove(process.ecalEndcapSelectiveReadoutTask)

process.p = cms.Path(process.ecalDataSequence*process.ecalEndcapMonitorSequence*process.dqmSaver)
process.q = cms.Path(process.ecalDataSequence*~process.ecalPrescaler*process.triggerTypeFilter*process.hybridSuperClusters*process.correctedHybridSuperClusters*process.multi5x5BasicClusters*process.multi5x5SuperClusters*process.ecalEndcapPedestalOnlineTask)
process.r = cms.EndPath(process.ecalEndcapCosmicTasksSequenceP5*process.ecalEndcapClusterTask)

process.r.remove(process.ecalEndcapPedestalOnlineTask)

process.l1GtEvmUnpack.EvmGtInputTag = 'source'

process.EventStreamHttpReader.consumerName = 'EcalEndcap DQM Consumer'

process.dqmEnv.subSystemFolder = 'EcalEndcap'
process.dqmSaver.referenceHandling = 'all'

process.ecalUncalibHit2.MinAmplBarrel = 12.
process.ecalUncalibHit2.MinAmplEndcap = 16.
process.ecalUncalibHit2.EBdigiCollection = 'ecalEBunpacker:ebDigis'
process.ecalUncalibHit2.EEdigiCollection = 'ecalEBunpacker:eeDigis'

process.ecalUncalibHit.EBdigiCollection = 'ecalEBunpacker:ebDigis'
process.ecalUncalibHit.EEdigiCollection = 'ecalEBunpacker:eeDigis'

process.ecalRecHit.EBuncalibRecHitCollection = 'ecalUncalibHit2:EcalUncalibRecHitsEB'
process.ecalRecHit.EEuncalibRecHitCollection = 'ecalUncalibHit2:EcalUncalibRecHitsEE'

process.ecalEndcapCosmicTask.EcalUncalibratedRecHitCollection = 'ecalUncalibHit2:EcalUncalibRecHitsEE'

process.ecalEndcapLaserTask.EcalUncalibratedRecHitCollection = 'ecalUncalibHit2:EcalUncalibRecHitsEE'

process.ecalEndcapLedTask.EcalUncalibratedRecHitCollection = 'ecalUncalibHit2:EcalUncalibRecHitsEE'

process.ecalEndcapTimingTask.EcalUncalibratedRecHitCollection = 'ecalUncalibHit2:EcalUncalibRecHitsEE'

process.simEcalTriggerPrimitiveDigis.Label = 'ecalEBunpacker'
process.simEcalTriggerPrimitiveDigis.InstanceEB = 'ebDigis'
process.simEcalTriggerPrimitiveDigis.InstanceEE = 'eeDigis'

process.EcalTrigPrimESProducer.DatabaseFile = 'TPG_cosmics.txt.gz'
#process.EcalTrigPrimESProducer.DatabaseFile = 'TPG_startup.txt.gz'

process.ecalEndcapMonitorClient.maskFile = '/nfshome0/ecalpro/MASKING-DQM/maskfile-EE.dat'
process.ecalEndcapMonitorClient.location = 'P5'
process.ecalEndcapMonitorClient.updateTime = 4
process.ecalEndcapMonitorClient.enabledClients = ['Integrity', 'StatusFlags', 'Occupancy', 'PedestalOnline', 'Pedestal', 'TestPulse', 'Laser', 'Led', 'Timing', 'Cosmic', 'Cluster', 'TriggerTower', 'Summary']

process.hybridSuperClusters.HybridBarrelSeedThr = 0.150
process.hybridSuperClusters.step = 1
process.hybridSuperClusters.eseed = 0.150

process.multi5x5BasicClusters.IslandBarrelSeedThr = 0.150
process.multi5x5BasicClusters.IslandEndcapSeedThr = 0.150

process.multi5x5SuperClusters.seedTransverseEnergyThreshold = 0.150

