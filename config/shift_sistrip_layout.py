def shiftsistriplayout(i, p, *rows): i["00 Shift/SiStrip/" + p] = DQMItem(layout=rows)

shiftsistriplayout(dqmitems, "00 - SiStrip ReportSummary",
 [{ 'path': "SiStrip/MechanicalView/detFractionReportMap",
    'description': "Fraction of Good Detector Modules plotted in different parts of the Tracker - <a href=https://twiki.cern.ch/twiki/bin/view/CMS/DQMShiftSiStrip>DQMShiftOnlineSiStrip</a> ", 'draw': { 'withref': "no" }},
  { 'path': "SiStrip/MechanicalView/sToNReportMap",
    'description': "Accepted S/N Ratios in different parts of the Tracker. The values are 1 if the ratio is within the accepted range otherwise it is 0  - <a href=https://twiki.cern.ch/twiki/bin/view/CMS/DQMShiftSiStrip>DQMShiftOnlineSiStrip</a> ", 'draw': { 'withref': "yes" }}],
 [{ 'path': "SiStrip/EventInfo/reportSummaryMap",
    'description': "Overall Report Summary where detector fraction and S/N flags are combined together -  <a href=https://twiki.cern.ch/twiki/bin/view/CMS/DQMShiftSiStrip>DQMShiftOnlineSiStrip</a> ", 'draw': { 'withref': "no" }}])
shiftsistriplayout(dqmitems, "01 - FED errors",
  [{ 'path': "SiStrip/ReadoutView/FedMonitoringSummary/FEDLevel/nFEDErrors",
     'description': "# of FEDs in error per event - Call Tracker DOC 165503 if the mean value is above 10 - <a href=https://twiki.cern.ch/twiki/bin/view/CMS/DQMShiftSiStrip>DQMShiftOnlineSiStrip</a>"}])
shiftsistriplayout(dqmitems, "02 - # of Cluster Trend",
  [{ 'path': "SiStrip/MechanicalView/TIB/TotalNumberOfClusterProfile__TIB",
     'description': "Total # of Clusters in TIB with event time in Seconds  - <a href=https://twiki.cern.ch/twiki/bin/view/CMS/DQMShiftSiStrip>DQMShiftOnlineSiStrip</a> "},
   { 'path': "SiStrip/MechanicalView/TOB/TotalNumberOfClusterProfile__TOB",
     'description': "Total # of Clusters in TOB with event time in Seconds  - <a href=https://twiki.cern.ch/twiki/bin/view/CMS/DQMShiftSiStrip>DQMShiftOnlineSiStrip</a> "}],
  [{ 'path': "SiStrip/MechanicalView/TID/side_1/TotalNumberOfClusterProfile__TID__side__1",
     'description': "Total # of Clusters in TID -ve side with event time in Seconds  - <a href=https://twiki.cern.ch/twiki/bin/view/CMS/DQMShiftSiStrip>DQMShiftOnlineSiStrip</a> "},
   { 'path': "SiStrip/MechanicalView/TID/side_2/TotalNumberOfClusterProfile__TID__side__2",
     'description': "Total # of Clusters in TID +ve side with event time in Seconds  - <a href=https://twiki.cern.ch/twiki/bin/view/CMS/DQMShiftSiStrip>DQMShiftOnlineSiStrip</a> "}],
  [{  'path':"SiStrip/MechanicalView/TEC/side_1/TotalNumberOfClusterProfile__TEC__side__1",
     'description': "Total # of Clusters in TEC -ve side with event time in Seconds  - <a href=https://twiki.cern.ch/twiki/bin/view/CMS/DQMShiftSiStrip>DQMShiftOnlineSiStrip</a> "},
   {  'path':"SiStrip/MechanicalView/TEC/side_2/TotalNumberOfClusterProfile__TEC__side__2",
     'description': "Total # of Clusters in TEC +ve side with event time in Seconds  - <a href=https://twiki.cern.ch/twiki/bin/view/CMS/DQMShiftSiStrip>DQMShiftOnlineSiStrip</a> "}])
shiftsistriplayout(dqmitems, "03 OnTrackCluster",
  [{ 'path': "SiStrip/MechanicalView/TIB/Summary_ClusterStoNCorr_OnTrack__TIB",
     'description': "Signal-to-Noise (corrected for the angle) for On-Track clusters in TIB  - <a href=https://twiki.cern.ch/twiki/bin/view/CMS/DQMShiftSiStrip>DQMShiftOnlineSiStrip</a> ", 'draw': { 'withref': "yes" }},
   { 'path': "SiStrip/MechanicalView/TOB/Summary_ClusterStoNCorr_OnTrack__TOB",
     'description': "Signal-to-Noise (corrected for the angle) for On-Track clusters in TOB  - <a href=https://twiki.cern.ch/twiki/bin/view/CMS/DQMShiftSiStrip>DQMShiftOnlineSiStrip</a> ", 'draw': { 'withref': "yes" } }],
  [{ 'path': "SiStrip/MechanicalView/TID/side_1/Summary_ClusterStoNCorr_OnTrack__TID__side__1",
     'description': "Signal-to-Noise (corrected for the angle) for On-Track clusters in TID -ve side - <a href=https://twiki.cern.ch/twiki/bin/view/CMS/DQMShiftOfflineSiStrip>DQMShiftOfflineSiStrip</a> ", 'draw': { 'withref': "yes" }},
   { 'path': "SiStrip/MechanicalView/TID/side_2/Summary_ClusterStoNCorr_OnTrack__TID__side__2",
     'description': "Signal-to-Noise (corrected for the angle) for On-Track clusters in TID +ve side - <a href=https://twiki.cern.ch/twiki/bin/view/CMS/DQMShiftOfflineSiStrip>DQMShiftOfflineSiStrip</a> ", 'draw': { 'withref': "yes" } }],
  [{ 'path': "SiStrip/MechanicalView/TEC/side_1/Summary_ClusterStoNCorr_OnTrack__TEC__side__1",
     'description': "Signal-to-Noise (corrected for the angle) for On-Track clusters in TEC -ve side - <a href=https://twiki.cern.ch/twiki/bin/view/CMS/DQMShiftOfflineSiStrip>DQMShiftOfflineSiStrip</a> ", 'draw': { 'withref': "yes" }},
   { 'path': "SiStrip/MechanicalView/TEC/side_2/Summary_ClusterStoNCorr_OnTrack__TEC__side__2",
     'description': "Signal-to-Noise (corrected for the angle) for On-Track clusters in TEC +ve side - <a href=https://twiki.cern.ch/twiki/bin/view/CMS/DQMShiftOfflineSiStrip>DQMShiftOfflineSiStrip</a> ", 'draw': { 'withref': "yes" } }])
shiftsistriplayout(dqmitems, "04 - Tracking ReportSummary",
 [{ 'path': "Tracking/EventInfo/reportSummaryMap",
    'description': " Quality Test results plotted for Tracking parameters : Chi2, TrackRate, #of Hits in Track - <a href=https://twiki.cern.ch/twiki/bin/view/CMS/DQMShiftSiStrip>DQMShiftSiStrip</a> ", 'draw': { 'withref': "no" }}])
shiftsistriplayout(dqmitems, "05 - Tracks",
 [{ 'path': "Tracking/TrackParameters/GeneralProperties/NumberOfGoodTracks_GenTk",
    'description': "Number of Reconstructed Tracks with high purity selection and pt > 1 GeV - <a href=https://twiki.cern.ch/twiki/bin/view/CMS/DQMShiftSiStrip>DQMShiftOnlineSiStrip</a> ", 'draw': { 'withref': "yes" }},
  { 'path': "Tracking/TrackParameters/HitProperties/GoodTrackNumberOfRecHitsPerTrack_GenTk",
    'description': "Number of RecHits per Track with high purity selection and pt > 1 GeV - <a href=https://twiki.cern.ch/twiki/bin/view/CMS/DQMShiftSiStrip>DQMShiftOnlineSiStrip</a> ", 'draw': { 'withref': "yes" }},
  { 'path': "Tracking/TrackParameters/GeneralProperties/GoodTrackPt_ImpactPoint_GenTk",
    'description': "Pt of Reconstructed Track with high purity selection and pt > 1 GeV - <a href=https://twiki.cern.ch/twiki/bin/view/CMS/DQMShiftSiStrip>DQMShiftOnlineSiStrip</a> ", 'draw': { 'withref': "yes" }}],
 [{ 'path': "Tracking/TrackParameters/GeneralProperties/GoodTrackChi2oNDF_GenTk",
    'description': "Chi Sqare per DoF for tracks with high purity selection and pt > 1 GeV - <a href=https://twiki.cern.ch/twiki/bin/view/CMS/DQMShiftSiStrip>DQMShiftOnlineSiStrip</a> ", 'draw': { 'withref': "yes" }},
  { 'path': "Tracking/TrackParameters/GeneralProperties/GoodTrackPhi_ImpactPoint_GenTk",
    'description': "Phi distribution of Reconstructed Tracks with high purity selection and pt > 1 GeV -  <a href=https://twiki.cern.ch/twiki/bin/view/CMS/DQMShiftSiStrip>DQMShiftOnlineSiStrip</a> ", 'draw': { 'withref': "yes" }},
  { 'path': "Tracking/TrackParameters/GeneralProperties/GoodTrackEta_ImpactPoint_GenTk",
    'description': " Eta distribution of Reconstructed Tracks with high purity selection and pt > 1 GeV - <a href=https://twiki.cern.ch/twiki/bin/view/CMS/DQMShiftSiStrip>DQMShiftOnlineSiStrip</a> ", 'draw': { 'withref': "yes" }}])
shiftsistriplayout(dqmitems, "06 - Cosmic Tracks",
 [{ 'path': "Tracking/TrackParameters/GeneralProperties/NumberOfTracks_CKFTk",
    'description': "Number of cosmic tracks  - <a href=https://twiki.cern.ch/twiki/bin/view/CMS/DQMShiftSiStrip>DQMShiftOnlineSiStrip</a> ", 'draw': { 'withref': "yes" }},
  { 'path': "Tracking/TrackParameters/HitProperties/NumberOfRecHitsPerTrack_CKFTk",
    'description': "Number of RecHits per track - <a href=https://twiki.cern.ch/twiki/bin/view/CMS/DQMShiftSiStrip>DQMShiftOnlineSiStrip</a> ", 'draw': { 'withref': "yes" }},
  { 'path': "Tracking/TrackParameters/GeneralProperties/TrackPt_CKFTk",
    'description': "Pt of cosmic track - <a href=https://twiki.cern.ch/twiki/bin/view/CMS/DQMShiftSiStrip>DQMShiftOnlineSiStrip</a> ", 'draw': { 'withref': "yes" }}],
 [{ 'path': "Tracking/TrackParameters/GeneralProperties/Chi2oNDF_CKFTk",
    'description': "Chi Sqare per DoF - <a href=https://twiki.cern.ch/twiki/bin/view/CMS/DQMShiftSiStrip>DQMShiftOnlineSiStrip</a> ", 'draw': { 'withref': "yes" }},
  { 'path': "Tracking/TrackParameters/GeneralProperties/TrackPhi_CKFTk",
    'description': "Phi distribution of cosmic tracks -  <a href=https://twiki.cern.ch/twiki/bin/view/CMS/DQMShiftSiStrip>DQMShiftOnlineSiStrip</a> ", 'draw': { 'withref': "yes" }},
  { 'path': "Tracking/TrackParameters/GeneralProperties/TrackEta_CKFTk",
    'description': " Eta distribution of cosmic tracks - <a href=https://twiki.cern.ch/twiki/bin/view/CMS/DQMShiftSiStrip>DQMShiftOnlineSiStrip</a> ", 'draw': { 'withref': "yes" }}])


