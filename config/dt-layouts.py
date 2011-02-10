def dtlayout(i, p, *rows): i["DT/Layouts/" + p] = DQMItem(layout=rows)

dtlayout(dqmitems, "00-Summary/00-DataIntegritySummary",
  [{ 'path': "DT/00-DataIntegrity/DataIntegritySummary", 'description': "<a href=https://twiki.cern.ch/twiki/bin/view/CMS/DTDQMPlots>Description and Instructions</a>" }])

dtlayout(dqmitems, "00-Summary/00-ROChannelSummary",
  [{ 'path': "DT/00-ROChannels/ROChannelSummary", 'description': "<a href=https://twiki.cern.ch/twiki/bin/view/CMS/DTDQMPlots>Description and Instructions</a>" }])

dtlayout(dqmitems, "00-Summary/01-OccupancySummary",
  [{ 'path': "DT/01-Digi/OccupancySummary", 'description': "<a href=https://twiki.cern.ch/twiki/bin/view/CMS/DTDQMPlots>Description and Instructions</a>" }])

dtlayout(dqmitems, "00-Summary/02-SegmentSummary",
  [{ 'path': "DT/02-Segments/segmentSummary", 'description': "<a href=https://twiki.cern.ch/twiki/bin/view/CMS/DTDQMPlots>Description and Instructions</a>" }])

dtlayout(dqmitems, "00-Summary/03-DDU_TriggerCorrFractionSummary",
  [{ 'path': "DT/04-LocalTrigger-DDU/DDU_CorrFractionSummary", 'description': "<a href=https://twiki.cern.ch/twiki/bin/view/CMS/DTDQMPlots>Description and Instructions</a>" }])

dtlayout(dqmitems, "00-Summary/04-DDU_Trigger2ndFractionSummary",
  [{ 'path': "DT/04-LocalTrigger-DDU/DDU_2ndFractionSummary", 'description': "<a href=https://twiki.cern.ch/twiki/bin/view/CMS/DTDQMPlots>Description and Instructions</a>" }])

dtlayout(dqmitems, "00-Summary/05-DCC_TriggerCorrFractionSummary",
  [{ 'path': "DT/03-LocalTrigger-DCC/DCC_CorrFractionSummary", 'description': "<a href=https://twiki.cern.ch/twiki/bin/view/CMS/DTDQMPlots>Description and Instructions</a>" }])


dtlayout(dqmitems, "00-Summary/06-DCC_Trigger2ndFractionSummary",
  [{ 'path': "DT/03-LocalTrigger-DCC/DCC_2ndFractionSummary", 'description': "<a href=https://twiki.cern.ch/twiki/bin/view/CMS/DTDQMPlots>Description and Instructions</a>" }])


dtlayout(dqmitems, "00-Summary/07-NoiseChannelsSummary",
  [{ 'path': "DT/05-Noise/NoiseSummary", 'description': "<a href=https://twiki.cern.ch/twiki/bin/view/CMS/DTDQMPlots>Description and Instructions</a>" }])


dtlayout(dqmitems, "00-Summary/08-SynchNoiseSummary",
         [{ 'path': "DT/05-Noise/SynchNoise/SynchNoiseSummary", 'description': "<a href=https://twiki.cern.ch/twiki/bin/view/CMS/DTDQMPlots>Description and Instructions</a>" }])

#dtlayout(dqmitems, "00-Summary/09-TestPulseOccupancy",
#         [{ 'path': "DT/10-TestPulses/OccupancySummary", 'description': "<a href=https://twiki.cern.ch/twiki/bin/view/CMS/DTDQMPlots>Description and Instructions</a>" }])


#### OCCUPANCIES #################################################################################

for wheel in range(-2, 3):
    for station in range (1, 5):
        for sector in range (1, 15):
            if station != 4 and (sector == 13 or sector == 14):
                continue
            name = "01-Occupancy/Wheel" + str(wheel) + "/St" + str(station) + "_Sec" + str(sector)
            histoname = "DT/01-Digi/Wheel" + str(wheel) + "/Sector" + str(sector) + "/Station" + str(station) +  "/OccupancyAllHits_perCh_W" + str(wheel) + "_St" + str(station) + "_Sec" +  str(sector)
            dtlayout(dqmitems, name,[{ 'path': histoname}])

            
#### TIME BOXES #################################################################################

for wheel in range(-2, 3):
    for sector in range (1, 15):
        for station in range (1, 5):
            if station != 4 and (sector == 13 or sector == 14):
                continue
            name = "02-TimeBoxes/Wheel" + str(wheel) + "/St" + str(station) + "_Sec" + str(sector)
            histoname = "DT/01-Digi/Wheel" + str(wheel) + "/Sector" + str(sector) + "/Station" + str(station) +  "/TimeBox_W" + str(wheel) + "_St" + str(station) + "_Sec" +  str(sector)
            histoname_SL1 = histoname + "_SL1"
            histoname_SL2 = histoname + "_SL2"
            histoname_SL3 = histoname + "_SL3"
            if station != 4:
                dtlayout(dqmitems, name,[{ 'path': histoname_SL1}],
                         [{ 'path': histoname_SL2}],
                         [{ 'path': histoname_SL3}])
            else:
                dtlayout(dqmitems, name,[{ 'path': histoname_SL1}],
                         [{ 'path': histoname_SL3}])
                
                
#### EVENT SIZE #################################################################################
for fed in range(770, 780):
   name = name = "03-FEDEventSize/FED" + str(fed)
   histoname = "DT/00-DataIntegrity/FED" + str(fed) + "/FED" + str(fed) + "_EventLenght"
   dtlayout(dqmitems, name,[{ 'path': histoname}])
   for rosid in range(1, 7):
       ros = rosid + 6*(fed>774)
       name = "04-ROSEventSize/FED" + str(fed) + "_ROS" + str(ros)
       histoname = "DT/00-DataIntegrity/FED" + str(fed) + "/ROS" + str(ros) + "/FED" + str(fed) + "_ROS" + str(ros) + "_ROSEventLenght"
       dtlayout(dqmitems, name,[{ 'path': histoname}])

#### TRIGGER SYNCH ##############################################################################

for wheel in range(-2, 3):
    name = "05-TriggerSynch/CorrectBX_Wh" + str(wheel) + "_DDU"
    histoname = "DT/04-LocalTrigger-DDU/Wheel" + str(wheel) + "/DDU_CorrectBXPhi_W" + str(wheel)
    dtlayout(dqmitems, name,[{ 'path': histoname}])
    name = "05-TriggerSynch/CorrectBX_Wh" + str(wheel) + "_DCC"
    histoname = "DT/03-LocalTrigger-DCC/Wheel" + str(wheel) + "/DCC_CorrectBXPhi_W" + str(wheel)
    dtlayout(dqmitems, name,[{ 'path': histoname}])
    name = "05-TriggerSynch/DDU-DCC_BXDifference_Wh" + str(wheel)
    histoname = "DT/04-LocalTrigger-DDU/Wheel" + str(wheel) + "/COM_BXDiff_W" + str(wheel)
    dtlayout(dqmitems, name,[{ 'path': histoname}])
    name = "05-TriggerSynch/Peak-Mean/Peak-Mean_Wh" + str(wheel) + "_DDU"
    histoname = "DT/04-LocalTrigger-DDU/Wheel" + str(wheel) + "/DDU_ResidualBXPhi_W" + str(wheel)
    dtlayout(dqmitems, name,[{ 'path': histoname}])
    name = "05-TriggerSynch/Peak-Mean/Peak-Mean_Wh" + str(wheel) + "_DCC"
    histoname = "DT/03-LocalTrigger-DCC/Wheel" + str(wheel) + "/DCC_ResidualBXPhi_W" + str(wheel)
    dtlayout(dqmitems, name,[{ 'path': histoname}])

#    
#         
#         
#         
#         
        

