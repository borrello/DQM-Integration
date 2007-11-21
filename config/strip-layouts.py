def striplayout(i, p, *rows): i["Layouts/Strip Layouts/" + p] = DQMItem(layout=rows)

striplayout(dqmitems, "SiStrip_NumberOfDigis_Summary",
  ["SiStrip/MechanicalView/TIB/Summary_NumberOfDigis_in_TIB"],
  ["SiStrip/MechanicalView/TOB/Summary_NumberOfDigis_in_TOB"],
  ["SiStrip/MechanicalView/TID/side_0/Summary_NumberOfDigis_in_side_0",
   "SiStrip/MechanicalView/TID/side_1/Summary_NumberOfDigis_in_side_1"],
  ["SiStrip/MechanicalView/TEC/side_0/Summary_NumberOfDigis_in_side_0",
   "SiStrip/MechanicalView/TEC/side_1/Summary_NumberOfDigis_in_side_1"])
striplayout(dqmitems, "SiStrip_NumberOfClusters_Summary",
  ["SiStrip/MechanicalView/TIB/Summary_NumberOfClusters_in_TIB"],
  ["SiStrip/MechanicalView/TOB/Summary_NumberOfClusters_in_TOB"],
  ["SiStrip/MechanicalView/TID/side_0/Summary_NumberOfClusters_in_side_0",
   "SiStrip/MechanicalView/TID/side_1/Summary_NumberOfClusters_in_side_1"],
  ["SiStrip/MechanicalView/TEC/side_0/Summary_NumberOfClusters_in_side_0",
   "SiStrip/MechanicalView/TEC/side_1/Summary_NumberOfClusters_in_side_1"])
striplayout(dqmitems, "SiStrip_ClusterWidth_Summary",
  ["SiStrip/MechanicalView/TIB/Summary_ClusterWidth_in_TIB"],
  ["SiStrip/MechanicalView/TOB/Summary_ClusterWidth_in_TOB"],
  ["SiStrip/MechanicalView/TID/side_0/Summary_ClusterWidth_in_side_0",
   "SiStrip/MechanicalView/TID/side_1/Summary_ClusterWidth_in_side_1"],
  ["SiStrip/MechanicalView/TEC/side_0/Summary_ClusterWidth_in_side_0",
   "SiStrip/MechanicalView/TEC/side_1/Summary_ClusterWidth_in_side_1"])
striplayout(dqmitems, "SiStrip_NumberOfDigis_Summary_TIB_Layer1",
  ["SiStrip/MechanicalView/TIB/layer_1/Summary_NumberOfDigis_in_layer_1"],
  ["SiStrip/MechanicalView/TIB/layer_2/Summary_NumberOfDigis_in_layer_2"],
  ["SiStrip/MechanicalView/TIB/layer_3/Summary_NumberOfDigis_in_layer_3"],
  ["SiStrip/MechanicalView/TIB/layer_4/Summary_NumberOfDigis_in_layer_4"])
