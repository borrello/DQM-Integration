def shiftsistriplayout(i, p, *rows): i["00 Shift/SiStrip/" + p] = DQMItem(layout=rows)

shiftsistriplayout(dqmitems, "00 - SiStrip ReportSummary",
 [{ 'path': "SiStrip/MechanicalView/detFractionReportMap",
    'description': "Fraction of Good Detector Modules plotted in different parts of the Tracker - <a href=https://twiki.cern.ch/twiki/bin/view/CMS/DQMShiftOfflineSiStrip>DQMShiftOfflineSiStrip</a> ", 'draw': { 'withref': "no" }},
  { 'path': "SiStrip/MechanicalView/sToNReportMap",
    'description': "Accepted S/N Ratios in different parts of the Tracker. The values are 1 if the ratio is within the accepted range otherwise it is 0  - <a href=https://twiki.cern.ch/twiki/bin/view/CMS/DQMShiftOfflineSiStrip>DQMShiftOfflineSiStrip</a> ", 'draw': { 'withref': "yes" }}],
 [{ 'path': "SiStrip/EventInfo/reportSummaryMap",
    'description': "Overall Report Summary where detector fraction and S/N flags are combined together -  <a href=https://twiki.cern.ch/twiki/bin/view/CMS/DQMShiftOfflineSiStrip>DQMShiftOfflineSiStrip</a> ", 'draw': { 'withref': "no" }}])
shiftsistriplayout(dqmitems, "01 OnTrackCluster",
  [{ 'path': "SiStrip/MechanicalView/TIB/Summary_ClusterStoNCorr_OnTrack__TIB",
     'description': "Signal-to-Noise (corrected for the angle) for On-Track clusters in TIB  - <a href=https://twiki.cern.ch/twiki/bin/view/CMS/DQMShiftOfflineSiStrip>DQMShiftOfflineSiStrip</a> ", 'draw': { 'withref': "yes" }},
   { 'path': "SiStrip/MechanicalView/TOB/Summary_ClusterStoNCorr_OnTrack__TOB",
     'description': "Signal-to-Noise (corrected for the angle) for On-Track clusters in TOB  - <a href=https://twiki.cern.ch/twiki/bin/view/CMS/DQMShiftOfflineSiStrip>DQMShiftOfflineSiStrip</a> ", 'draw': { 'withref': "yes" } }],
  [{ 'path': "SiStrip/MechanicalView/TID/side_1/Summary_ClusterStoNCorr_OnTrack__TID__side__1",
     'description': "Signal-to-Noise (corrected for the angle) for On-Track clusters in TID -ve side - <a href=https://twiki.cern.ch/twiki/bin/view/CMS/DQMShiftOfflineSiStrip>DQMShiftOfflineSiStrip</a> ", 'draw': { 'withref': "yes" }},
   { 'path': "SiStrip/MechanicalView/TID/side_2/Summary_ClusterStoNCorr_OnTrack__TID__side__2",
     'description': "Signal-to-Noise (corrected for the angle) for On-Track clusters in TID +ve side - <a href=https://twiki.cern.ch/twiki/bin/view/CMS/DQMShiftOfflineSiStrip>DQMShiftOfflineSiStrip</a> ", 'draw': { 'withref': "yes" } }],
  [{ 'path': "SiStrip/MechanicalView/TEC/side_1/Summary_ClusterStoNCorr_OnTrack__TEC__side__1",
     'description': "Signal-to-Noise (corrected for the angle) for On-Track clusters in TEC -ve side - <a href=https://twiki.cern.ch/twiki/bin/view/CMS/DQMShiftOfflineSiStrip>DQMShiftOfflineSiStrip</a> ", 'draw': { 'withref': "yes" }},
   { 'path': "SiStrip/MechanicalView/TEC/side_2/Summary_ClusterStoNCorr_OnTrack__TEC__side__2",
     'description': "Signal-to-Noise (corrected for the angle) for On-Track clusters in TEC +ve side - <a href=https://twiki.cern.ch/twiki/bin/view/CMS/DQMShiftOfflineSiStrip>DQMShiftOfflineSiStrip</a> ", 'draw': { 'withref': "yes" } }])
shiftsistriplayout(dqmitems, "02 - Tracking ReportSummary",
 [{ 'path': "Tracking/EventInfo/reportSummaryMap",
    'description': " Quality Test results plotted for Tracking parameters : Chi2, TrackRate, #of Hits in Track - <a href=https://twiki.cern.ch/twiki/bin/view/CMS/DQMShiftOfflineSiStrip>DQMShiftOfflineSiStrip</a> ", 'draw': { 'withref': "no" }}])
shiftsistriplayout(dqmitems, "03 - Tracks",
 [{ 'path': "Tracking/TrackParameters/GeneralProperties/NumberOfTracks_HeavyIonTk",
    'description': "Number of Reconstructed Tracks  - <a href=https://twiki.cern.ch/twiki/bin/view/CMS/DQMShiftOfflineSiStrip>DQMShiftOfflineSiStrip</a> ", 'draw': { 'withref': "yes" }},
  { 'path': "Tracking/TrackParameters/HitProperties/NumberOfRecHitsPerTrack_HeavyIonTk",
    'description': "Number of RecHits per Track  - <a href=https://twiki.cern.ch/twiki/bin/view/CMS/DQMShiftOfflineSiStrip>DQMShiftOfflineSiStrip</a> ", 'draw': { 'withref': "yes" }},
  { 'path': "Tracking/TrackParameters/GeneralProperties/TrackPt_ImpactPoint_HeavyIonTk",
    'description': "Pt of Reconstructed Track  - <a href=https://twiki.cern.ch/twiki/bin/view/CMS/DQMShiftOfflineSiStrip>DQMShiftOfflineSiStrip</a> ", 'draw': { 'withref': "yes" }}],
 [{ 'path': "Tracking/TrackParameters/GeneralProperties/Chi2oNDF_HeavyIonTk",
    'description': "Chi Sqare per DoF  -  <a href=https://twiki.cern.ch/twiki/bin/view/CMS/DQMShiftOfflineSiStrip>DQMShiftOfflineSiStrip</a> ", 'draw': { 'withref': "yes" }},
  { 'path': "Tracking/TrackParameters/GeneralProperties/TrackPhi_ImpactPoint_HeavyIonTk",
    'description': "Phi distribution of Reconstructed Tracks  -  <a href=https://twiki.cern.ch/twiki/bin/view/CMS/DQMShiftOfflineSiStrip>DQMShiftOfflineSiStrip</a> ", 'draw': { 'withref': "yes" }},
  { 'path': "Tracking/TrackParameters/GeneralProperties/TrackEta_ImpactPoint_HeavyIonTk",
    'description': " Eta distribution of Reconstructed Tracks - <a href=https://twiki.cern.ch/twiki/bin/view/CMS/DQMShiftOfflineSiStrip>DQMShiftOfflineSiStrip</a> ", 'draw': { 'withref': "yes" }}])

