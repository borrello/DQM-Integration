import FWCore.ParameterSet.Config as cms

process = cms.Process("hlxdqmlive")

from FWCore.MessageLogger.MessageLogger_cfi import *

## Input source
process.load("DQM.Integration.test.inputsource_cfi")
process.DQMEventStreamHttpReader.consumerName = 'HLX DQM Consumer'
process.DQMEventStreamHttpReader.maxEventRequestRate = cms.untracked.double(5.0)

## HLX configuration
process.load("DQM.HLXMonitor.hlx_dqm_sourceclient_cfi")
## changed machine below from 22 to 21 
process.hlxdqmsource.PrimaryHLXDAQIP = 'vmepcs2f17-21'
## keeping machine 18 below out; haven't tested it to find out what it does
## process.hlxdqmsource.SecondaryHLXDAQIP = 'vmepcs2f17-18'
## changed port below from 51007 to 51010; connects to DQMIsolator
process.hlxdqmsource.SourcePort = 51010

## Set up env and saver
process.load("DQM.Integration.test.environment_cfi")
process.dqmEnv.subSystemFolder    = "HLX"

## Lumi reference file
process.DQMStore.referenceFileName = '/dqmdata/dqm/reference/hlx_reference.root'

process.hlxQualityTester = cms.EDAnalyzer("QualityTester",
    # default is 1
    prescaleFactor = cms.untracked.int32(10000),
    # use eventloop for testing only ! default is false
    # untracked bool testInEventloop = false
    qtList = cms.untracked.FileInPath('DQM/HLXMonitor/test/HLXQualityTests.xml'),
    qtestOnEndLumi = cms.untracked.bool(True),
    qtestOnEndRun = cms.untracked.bool(True)
)

process.p = cms.Path(process.hlxdqmsource*process.hlxQualityTester*process.dqmEnv*process.dqmSaver)

## Shouldn't need this anymore ...
##process.hlxdqmsource.outputDir = process.dqmSaver.dirName


