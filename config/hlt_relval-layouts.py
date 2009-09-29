###
# """
# file: DQM/Integration/config/hlt_relval-layouts.py
# 
# Layout file for trigger release validation
#  facilitating organization/regrouping of subsystem histograms
# -use subsystem top-folder as specified in previous stages eg
#  def trigval<subsys>(i, p, *rows): i["HLT/<subsys>/Preselection" + p] = DQMItem(layout=rows)
# """
###


###---- EGAMMA selection goes here: ----

def trigvalegammaZ(i, p, *rows): i["HLT/HLTEgammaValidation/Zee Preselection/" + p] = DQMItem(layout=rows)

trigvalegammaZ(dqmitems,"doubleEle5SWL1R/total",
           [{'path': "HLT/HLTEgammaValidation/HLT_DoubleEle5_SW_L1RDQMZee/efficiency_by_step_MC_matched", 'description':"per-event efficiency (MC matched) for doubleEle5SWL1R"},
            {'path': "HLT/HLTEgammaValidation/HLT_DoubleEle5_SW_L1RDQMZee/efficiency_by_step", 'description':"per-event efficiency (MC matched) for doubleEle5SWL1R"}])

trigvalegammaZ(dqmitems,"doubleEle5SWL1R/kinematics",
           [{'path': "HLT/HLTEgammaValidation/HLT_DoubleEle5_SW_L1RDQMZee/gen_et", 'description':"per-event efficiency (MC matched) for doubleEle5SWL1R"},
            {'path': "HLT/HLTEgammaValidation/HLT_DoubleEle5_SW_L1RDQMZee/gen_eta", 'description':"per-event efficiency (MC matched) for doubleEle5SWL1R"}])

trigvalegammaZ(dqmitems,"doubleEle5SWL1R/L1 match",
           [{'path': "HLT/HLTEgammaValidation/HLT_DoubleEle5_SW_L1RDQMZee/efficiency_hltL1NonIsoHLTNonIsoDoubleElectronEt5L1MatchFilterRegional_vs_eta_MC_matched", 'description':"per-object (MC matched) for hltL1NonIsoHLTNonIsoDoubleElectronEt5L1MatchFilterRegional in doubleEle5SWL1R_vs_eta"},
            {'path': "HLT/HLTEgammaValidation/HLT_DoubleEle5_SW_L1RDQMZee/efficiency_hltL1NonIsoHLTNonIsoDoubleElectronEt5L1MatchFilterRegional_vs_et_MC_matched", 'description':"per-object (MC matched) for hltL1NonIsoHLTNonIsoDoubleElectronEt5L1MatchFilterRegional in doubleEle5SWL1R_vs_et"}])

trigvalegammaZ(dqmitems,"doubleEle5SWL1R/Et cut",
           [{'path': "HLT/HLTEgammaValidation/HLT_DoubleEle5_SW_L1RDQMZee/efficiency_hltL1NonIsoHLTNonIsoDoubleElectronEt5EtFilter_vs_eta_MC_matched", 'description':"per-object (MC matched) for hltL1NonIsoHLTNonIsoDoubleElectronEt5EtFilter in doubleEle5SWL1R_vs_eta"},
            {'path': "HLT/HLTEgammaValidation/HLT_DoubleEle5_SW_L1RDQMZee/efficiency_hltL1NonIsoHLTNonIsoDoubleElectronEt5EtFilter_vs_et_MC_matched", 'description':"per-object (MC matched) for hltL1NonIsoHLTNonIsoDoubleElectronEt5EtFilter in doubleEle5SWL1R_vs_et"}])

trigvalegammaZ(dqmitems,"doubleEle5SWL1R/Hcal isolation",
           [{'path': "HLT/HLTEgammaValidation/HLT_DoubleEle5_SW_L1RDQMZee/efficiency_hltL1NonIsoHLTNonIsoDoubleElectronEt5HcalIsolFilter_vs_eta_MC_matched", 'description':"per-object (MC matched) for hltL1NonHLTnonIsoIsoDoubleElectronEt5HcalIsolFilter in doubleEle5SWL1R_vs_eta"},
            {'path': "HLT/HLTEgammaValidation/HLT_DoubleEle5_SW_L1RDQMZee/efficiency_hltL1NonIsoHLTNonIsoDoubleElectronEt5HcalIsolFilter_vs_et_MC_matched", 'description':"per-object (MC matched) for hltL1NonHLTnonIsoIsoDoubleElectronEt5HcalIsolFilter in doubleEle5SWL1R_vs_et"}])

trigvalegammaZ(dqmitems,"doubleEle5SWL1R/pixel match",
           [{'path': "HLT/HLTEgammaValidation/HLT_DoubleEle5_SW_L1RDQMZee/efficiency_hltL1NonIsoHLTNonIsoDoubleElectronEt5PixelMatchFilter_vs_eta_MC_matched", 'description':"per-object (MC matched) for hltL1NonIsoHLTNonIsoDoubleElectronEt5PixelMatchFilter in doubleEle5SWL1R_vs_eta"},
            {'path': "HLT/HLTEgammaValidation/HLT_DoubleEle5_SW_L1RDQMZee/efficiency_hltL1NonIsoHLTNonIsoDoubleElectronEt5PixelMatchFilter_vs_et_MC_matched", 'description':"per-object (MC matched) for hltL1NonIsoHLTNonIsoDoubleElectronEt5PixelMatchFilter in doubleEle5SWL1R_vs_et"}])



trigvalegammaZ(dqmitems,"Ele10LWL1R/total",
           [{'path': "HLT/HLTEgammaValidation/HLT_Ele10_LW_L1RDQMZee/efficiency_by_step_MC_matched", 'description':"per-event efficiency (MC matched) for Ele10LWL1R"},
            {'path': "HLT/HLTEgammaValidation/HLT_Ele10_LW_L1RDQMZee/efficiency_by_step", 'description':"per-event efficiency (MC matched) for Ele10LWL1R"}])

trigvalegammaZ(dqmitems,"Ele10LWL1R/kinematics",
           [{'path': "HLT/HLTEgammaValidation/HLT_Ele10_LW_L1RDQMZee/gen_et", 'description':"per-event efficiency (MC matched) for Ele10LWL1R"},
            {'path': "HLT/HLTEgammaValidation/HLT_Ele10_LW_L1RDQMZee/gen_eta", 'description':"per-event efficiency (MC matched) for Ele10LWL1R"}])

trigvalegammaZ(dqmitems,"Ele10LWL1R/L1 match",
           [{'path': "HLT/HLTEgammaValidation/HLT_Ele10_LW_L1RDQMZee/efficiency_hltL1NonIsoHLTNonIsoSingleElectronLWEt10L1MatchFilterRegional_vs_eta_MC_matched", 'description':"per-object (MC matched) for hltL1NonIsoHLTNonIsoSingleElectronLWEt10L1MatchFilterRegional in Ele10LWL1R_vs_eta"},
            {'path': "HLT/HLTEgammaValidation/HLT_Ele10_LW_L1RDQMZee/efficiency_hltL1NonIsoHLTNonIsoSingleElectronLWEt10L1MatchFilterRegional_vs_et_MC_matched", 'description':"per-object (MC matched) for hltL1NonIsoHLTNonIsoSingleElectronLWEt10L1MatchFilterRegional in Ele10LWL1R_vs_et"}])

trigvalegammaZ(dqmitems,"Ele10LWL1R/Et cut",
           [{'path': "HLT/HLTEgammaValidation/HLT_Ele10_LW_L1RDQMZee/efficiency_hltL1NonIsoHLTNonIsoSingleElectronLWEt10EtFilter_vs_eta_MC_matched", 'description':"per-object (MC matched) for hltL1NonIsoHLTNonIsoSingleElectronLWEt10EtFilter in Ele10LWL1R_vs_eta"},
            {'path': "HLT/HLTEgammaValidation/HLT_Ele10_LW_L1RDQMZee/efficiency_hltL1NonIsoHLTNonIsoSingleElectronLWEt10EtFilter_vs_et_MC_matched", 'description':"per-object (MC matched) for hltL1NonIsoHLTNonIsoSingleElectronLWEt10EtFilter in Ele10LWL1R_vs_et"}])

trigvalegammaZ(dqmitems,"Ele10LWL1R/Hcal isolation",
           [{'path': "HLT/HLTEgammaValidation/HLT_Ele10_LW_L1RDQMZee/efficiency_hltL1NonIsoHLTNonIsoSingleElectronLWEt10HcalIsolFilter_vs_eta_MC_matched", 'description':"per-object (MC matched) for hltL1NonIsoHLTNonIsoSingleElectronLWEt10HcalIsolFilter in Ele10LWL1R_vs_eta"},
            {'path': "HLT/HLTEgammaValidation/HLT_Ele10_LW_L1RDQMZee/efficiency_hltL1NonIsoHLTNonIsoSingleElectronLWEt10HcalIsolFilter_vs_et_MC_matched", 'description':"per-object (MC matched) for hltL1NonIsoHLTNonIsoSingleElectronLWEt10HcalIsolFilter in Ele10LWL1R_vs_et"}])

trigvalegammaZ(dqmitems,"Ele10LWL1R/pixel match",
           [{'path': "HLT/HLTEgammaValidation/HLT_Ele10_LW_L1RDQMZee/efficiency_hltL1NonIsoHLTNonIsoSingleElectronLWEt10PixelMatchFilter_vs_eta_MC_matched", 'description':"per-object (MC matched) for hltL1NonIsoHLTNonIsoSingleElectronLWEt10PixelMatchFilter in Ele10LWL1R_vs_eta"},
            {'path': "HLT/HLTEgammaValidation/HLT_Ele10_LW_L1RDQMZee/efficiency_hltL1NonIsoHLTNonIsoSingleElectronLWEt10PixelMatchFilter_vs_et_MC_matched", 'description':"per-object (MC matched) for hltL1NonIsoHLTNonIsoSingleElectronLWEt10PixelMatchFilter in Ele10LWL1R_vs_et"}])



trigvalegammaZ(dqmitems,"Ele10LWEleIdL1R/total",
           [{'path': "HLT/HLTEgammaValidation/HLT_Ele10_LW_EleId_L1RDQMZee/efficiency_by_step_MC_matched", 'description':"per-event efficiency (MC matched) for Ele10LWEleIdL1R"},
            {'path': "HLT/HLTEgammaValidation/HLT_Ele10_LW_EleId_L1RDQMZee/efficiency_by_step", 'description':"per-event efficiency (MC matched) for Ele10LWEleIdL1R"}])

trigvalegammaZ(dqmitems,"Ele10LWEleIdL1R/kinematics",
           [{'path': "HLT/HLTEgammaValidation/HLT_Ele10_LW_EleId_L1RDQMZee/gen_et", 'description':"per-event efficiency (MC matched) for Ele10LWEleIdL1R"},
            {'path': "HLT/HLTEgammaValidation/HLT_Ele10_LW_EleId_L1RDQMZee/gen_eta", 'description':"per-event efficiency (MC matched) for Ele10LWEleIdL1R"}])

trigvalegammaZ(dqmitems,"Ele10LWEleIdL1R/L1 match",
           [{'path': "HLT/HLTEgammaValidation/HLT_Ele10_LW_EleId_L1RDQMZee/efficiency_hltL1NonIsoHLTNonIsoSingleElectronLWEt10EleIdL1MatchFilterRegional_vs_eta_MC_matched", 'description':"per-object (MC matched) for hltL1NonIsoHLTNonIsoSingleElectronLWEt10EleIdL1MatchFilterRegional in Ele10LWEleIdL1R_vs_eta"},
            {'path': "HLT/HLTEgammaValidation/HLT_Ele10_LW_EleId_L1RDQMZee/efficiency_hltL1NonIsoHLTNonIsoSingleElectronLWEt10EleIdL1MatchFilterRegional_vs_et_MC_matched" , 'description':"per-object (MC matched) for hltL1NonIsoHLTNonIsoSingleElectronLWEt10EleIdL1MatchFilterRegional in Ele10LWEleIdL1R_vs_et"}])

trigvalegammaZ(dqmitems,"Ele10LWEleIdL1R/Et cut",
           [{'path': "HLT/HLTEgammaValidation/HLT_Ele10_LW_EleId_L1RDQMZee/efficiency_hltL1NonIsoHLTNonIsoSingleElectronLWEt10EleIdEtFilter_vs_eta_MC_matched", 'description':"per-object (MC matched) for hltL1NonIsoHLTNonIsoSingleElectronLWEt10EleIdEtFilter in Ele10LWEleIdL1R_vs_eta"},
            {'path': "HLT/HLTEgammaValidation/HLT_Ele10_LW_EleId_L1RDQMZee/efficiency_hltL1NonIsoHLTNonIsoSingleElectronLWEt10EleIdEtFilter_vs_et_MC_matched",  'description':"per-object (MC matched) for hltL1NonIsoHLTNonIsoSingleElectronLWEt10EleIdEtFilter in Ele10LWEleIdL1R_vs_et"}])

trigvalegammaZ(dqmitems,"Ele10LWEleIdL1R/cluster shape cut",
           [{'path': "HLT/HLTEgammaValidation/HLT_Ele10_LW_EleId_L1RDQMZee/efficiency_hltL1NonIsoHLTNonIsoSingleElectronLWEt10EleIdClusterShapeFilter_vs_eta_MC_matched", 'description':"per-object (MC matched) for hltL1NonIsoHLTNonIsoSingleElectronLWEt10EleIdClusterShapeFilter in Ele10LWEleIdL1R_vs_eta"},
            {'path': "HLT/HLTEgammaValidation/HLT_Ele10_LW_EleId_L1RDQMZee/efficiency_hltL1NonIsoHLTNonIsoSingleElectronLWEt10EleIdClusterShapeFilter_vs_et_MC_matched", 'description':"per-object (MC matched) for hltL1NonIsoHLTNonIsoSingleElectronLWEt10EleIdClusterShapeFilter in Ele10LWEleIdL1R_vs_et"}])

trigvalegammaZ(dqmitems,"Ele10LWEleIdL1R/Hcal isolation",
           [{'path': "HLT/HLTEgammaValidation/HLT_Ele10_LW_EleId_L1RDQMZee/efficiency_hltL1NonIsoHLTNonIsoSingleElectronLWEt10EleIdHcalIsolFilter_vs_eta_MC_matched", 'description':"per-object (MC matched) for hltL1NonIsoHLTNonIsoSingleElectronLWEt10EleIdHcalIsolFilter in Ele10LWEleIdL1R_vs_eta"},
            {'path': "HLT/HLTEgammaValidation/HLT_Ele10_LW_EleId_L1RDQMZee/efficiency_hltL1NonIsoHLTNonIsoSingleElectronLWEt10EleIdHcalIsolFilter_vs_et_MC_matched",  'description':"per-object (MC matched) for hltL1NonIsoHLTNonIsoSingleElectronLWEt10EleIdHcalIsolFilter in Ele10LWEleIdL1R_vs_et"}])

trigvalegammaZ(dqmitems,"Ele10LWEleIdL1R/pixel match",
           [{'path': "HLT/HLTEgammaValidation/HLT_Ele10_LW_EleId_L1RDQMZee/efficiency_hltL1NonIsoHLTNonIsoSingleElectronLWEt10EleIdPixelMatchFilter_vs_eta_MC_matched", 'description':"per-object (MC matched) for hltL1NonIsoHLTNonIsoSingleElectronLWEt10EleIdPixelMatchFilter in Ele10LWEleIdL1R_vs_eta"},
            {'path': "HLT/HLTEgammaValidation/HLT_Ele10_LW_EleId_L1RDQMZee/efficiency_hltL1NonIsoHLTNonIsoSingleElectronLWEt10EleIdPixelMatchFilter_vs_et_MC_matched",  'description':"per-object (MC matched) for hltL1NonIsoHLTNonIsoSingleElectronLWEt10EleIdPixelMatchFilter in Ele10LWEleIdL1R_vs_et"}])

trigvalegammaZ(dqmitems,"Ele10LWEleIdL1R/ 1oE - 1op cut",
           [{'path': "HLT/HLTEgammaValidation/HLT_Ele10_LW_EleId_L1RDQMZee/efficiency_hltL1NonIsoHLTNonIsoSingleElectronLWEt10EleIdOneOEMinusOneOPFilter_vs_eta_MC_matched", 'description':"per-object (MC matched) for hltL1NonIsoHLTNonIsoSingleElectronLWEt10EleIdOneOEMinusOneOPFilter in Ele10LWEleIdL1R_vs_eta"},
            {'path': "HLT/HLTEgammaValidation/HLT_Ele10_LW_EleId_L1RDQMZee/efficiency_hltL1NonIsoHLTNonIsoSingleElectronLWEt10EleIdOneOEMinusOneOPFilter_vs_et_MC_matched", 'description':"per-object (MC matched) for hltL1NonIsoHLTNonIsoSingleElectronLWEt10EleIdOneOEMinusOneOPFilter in Ele10LWEleIdL1R_vs_et"}])

trigvalegammaZ(dqmitems,"Ele10LWEleIdL1R/ delta-eta cut",
           [{'path': "HLT/HLTEgammaValidation/HLT_Ele10_LW_EleId_L1RDQMZee/efficiency_hltL1NonIsoHLTNonIsoSingleElectronLWEt10EleIdDetaFilter_vs_eta_MC_matched", 'description':"per-object (MC matched) for hltL1NonIsoHLTNonIsoSingleElectronLWEt10EleIdDetaFilter in Ele10LWEleIdL1R_vs_eta"},
            {'path': "HLT/HLTEgammaValidation/HLT_Ele10_LW_EleId_L1RDQMZee/efficiency_hltL1NonIsoHLTNonIsoSingleElectronLWEt10EleIdDetaFilter_vs_et_MC_matched", 'description':"per-object (MC matched) for hltL1NonIsoHLTNonIsoSingleElectronLWEt10EleIdDetaFilter in Ele10LWEleIdL1R_vs_et"}])

trigvalegammaZ(dqmitems,"Ele10LWEleIdL1R/ delta-phi cut",
           [{'path': "HLT/HLTEgammaValidation/HLT_Ele10_LW_EleId_L1RDQMZee/efficiency_hltL1NonIsoHLTNonIsoSingleElectronLWEt10EleIdDphiFilter_vs_eta_MC_matched", 'description':"per-object (MC matched) for hltL1NonIsoHLTNonIsoSingleElectronLWEt10EleIdDphiFilter in Ele10LWEleIdL1R_vs_eta"},
            {'path': "HLT/HLTEgammaValidation/HLT_Ele10_LW_EleId_L1RDQMZee/efficiency_hltL1NonIsoHLTNonIsoSingleElectronLWEt10EleIdDphiFilter_vs_et_MC_matched", 'description':"per-object (MC matched) for hltL1NonIsoHLTNonIsoSingleElectronLWEt10EleIdDphiFilter in Ele10LWEleIdL1R_vs_et"}])



                            

def hltlayoutW(i, p, *rows): i["HLT/HLTEgammaValidation/Wenu Preselection/" + p] = DQMItem(layout=rows)

hltlayoutW(dqmitems,"Ele10LWL1R/total",
           [{'path': "HLT/HLTEgammaValidation/HLT_Ele10_LW_L1RDQMWenu/efficiency_by_step_MC_matched", 'description':"per-event efficiency (MC matched) for Ele10LWL1R"},
            {'path': "HLT/HLTEgammaValidation/HLT_Ele10_LW_L1RDQMWenu/efficiency_by_step", 'description':"per-event efficiency (MC matched) for Ele10LWL1R"}])

hltlayoutW(dqmitems,"Ele10LWL1R/kinematics",
           [{'path': "HLT/HLTEgammaValidation/HLT_Ele10_LW_L1RDQMWenu/gen_et", 'description':"per-event efficiency (MC matched) for Ele10LWL1R"},
            {'path': "HLT/HLTEgammaValidation/HLT_Ele10_LW_L1RDQMWenu/gen_eta", 'description':"per-event efficiency (MC matched) for Ele10LWL1R"}])

hltlayoutW(dqmitems,"Ele10LWL1R/L1 match",
           [{'path': "HLT/HLTEgammaValidation/HLT_Ele10_LW_L1RDQMWenu/efficiency_hltL1NonIsoHLTNonIsoSingleElectronLWEt10L1MatchFilterRegional_vs_eta_MC_matched", 'description':"per-object (MC matched) for hltL1NonIsoHLTNonIsoSingleElectronLWEt10L1MatchFilterRegional in Ele10LWL1R_vs_eta"},
            {'path': "HLT/HLTEgammaValidation/HLT_Ele10_LW_L1RDQMWenu/efficiency_hltL1NonIsoHLTNonIsoSingleElectronLWEt10L1MatchFilterRegional_vs_et_MC_matched", 'description':"per-object (MC matched) for hltL1NonIsoHLTNonIsoSingleElectronLWEt10L1MatchFilterRegional in Ele10LWL1R_vs_et"}])

hltlayoutW(dqmitems,"Ele10LWL1R/Et cut",
           [{'path': "HLT/HLTEgammaValidation/HLT_Ele10_LW_L1RDQMWenu/efficiency_hltL1NonIsoHLTNonIsoSingleElectronLWEt10EtFilter_vs_eta_MC_matched", 'description':"per-object (MC matched) for hltL1NonIsoHLTNonIsoSingleElectronLWEt10EtFilter in Ele10LWL1R_vs_eta"},
            {'path': "HLT/HLTEgammaValidation/HLT_Ele10_LW_L1RDQMWenu/efficiency_hltL1NonIsoHLTNonIsoSingleElectronLWEt10EtFilter_vs_et_MC_matched", 'description':"per-object (MC matched) for hltL1NonIsoHLTNonIsoSingleElectronLWEt10EtFilter in Ele10LWL1R_vs_et"}])

hltlayoutW(dqmitems,"Ele10LWL1R/Hcal isolation",
           [{'path': "HLT/HLTEgammaValidation/HLT_Ele10_LW_L1RDQMWenu/efficiency_hltL1NonIsoHLTNonIsoSingleElectronLWEt10HcalIsolFilter_vs_eta_MC_matched", 'description':"per-object (MC matched) for hltL1NonIsoHLTNonIsoSingleElectronLWEt10HcalIsolFilter in Ele10LWL1R_vs_eta"},
            {'path': "HLT/HLTEgammaValidation/HLT_Ele10_LW_L1RDQMWenu/efficiency_hltL1NonIsoHLTNonIsoSingleElectronLWEt10HcalIsolFilter_vs_et_MC_matched", 'description':"per-object (MC matched) for hltL1NonIsoHLTNonIsoSingleElectronLWEt10HcalIsolFilter in Ele10LWL1R_vs_et"}])

hltlayoutW(dqmitems,"Ele10LWL1R/pixel match",
           [{'path': "HLT/HLTEgammaValidation/HLT_Ele10_LW_L1RDQMWenu/efficiency_hltL1NonIsoHLTNonIsoSingleElectronLWEt10PixelMatchFilter_vs_eta_MC_matched", 'description':"per-object (MC matched) for hltL1NonIsoHLTNonIsoSingleElectronLWEt10PixelMatchFilter in Ele10LWL1R_vs_eta"},
            {'path': "HLT/HLTEgammaValidation/HLT_Ele10_LW_L1RDQMWenu/efficiency_hltL1NonIsoHLTNonIsoSingleElectronLWEt10PixelMatchFilter_vs_et_MC_matched", 'description':"per-object (MC matched) for hltL1NonIsoHLTNonIsoSingleElectronLWEt10PixelMatchFilter in Ele10LWL1R_vs_et"}])



hltlayoutW(dqmitems,"Ele10LWEleIdL1R/total",
           [{'path': "HLT/HLTEgammaValidation/HLT_Ele10_LW_EleId_L1RDQMWenu/efficiency_by_step_MC_matched", 'description':"per-event efficiency (MC matched) for Ele10LWEleIdL1R"},
            {'path': "HLT/HLTEgammaValidation/HLT_Ele10_LW_EleId_L1RDQMWenu/efficiency_by_step", 'description':"per-event efficiency (MC matched) for Ele10LWEleIdL1R"}])

hltlayoutW(dqmitems,"Ele10LWEleIdL1R/kinematics",
           [{'path': "HLT/HLTEgammaValidation/HLT_Ele10_LW_EleId_L1RDQMWenu/gen_et", 'description':"per-event efficiency (MC matched) for Ele10LWEleIdL1R"},
            {'path': "HLT/HLTEgammaValidation/HLT_Ele10_LW_EleId_L1RDQMWenu/gen_eta", 'description':"per-event efficiency (MC matched) for Ele10LWEleIdL1R"}])

hltlayoutW(dqmitems,"Ele10LWEleIdL1R/L1 match",
           [{'path': "HLT/HLTEgammaValidation/HLT_Ele10_LW_EleId_L1RDQMWenu/efficiency_hltL1NonIsoHLTNonIsoSingleElectronLWEt10EleIdL1MatchFilterRegional_vs_eta_MC_matched", 'description':"per-object (MC matched) for hltL1NonIsoHLTNonIsoSingleElectronLWEt10EleIdL1MatchFilterRegional in Ele10LWEleIdL1R_vs_eta"},
            {'path': "HLT/HLTEgammaValidation/HLT_Ele10_LW_EleId_L1RDQMWenu/efficiency_hltL1NonIsoHLTNonIsoSingleElectronLWEt10EleIdL1MatchFilterRegional_vs_et_MC_matched" , 'description':"per-object (MC matched) for hltL1NonIsoHLTNonIsoSingleElectronLWEt10EleIdL1MatchFilterRegional in Ele10LWEleIdL1R_vs_et"}])

hltlayoutW(dqmitems,"Ele10LWEleIdL1R/Et cut",
           [{'path': "HLT/HLTEgammaValidation/HLT_Ele10_LW_EleId_L1RDQMWenu/efficiency_hltL1NonIsoHLTNonIsoSingleElectronLWEt10EleIdEtFilter_vs_eta_MC_matched", 'description':"per-object (MC matched) for hltL1NonIsoHLTNonIsoSingleElectronLWEt10EleIdEtFilter in Ele10LWEleIdL1R_vs_eta"},
            {'path': "HLT/HLTEgammaValidation/HLT_Ele10_LW_EleId_L1RDQMWenu/efficiency_hltL1NonIsoHLTNonIsoSingleElectronLWEt10EleIdEtFilter_vs_et_MC_matched",  'description':"per-object (MC matched) for hltL1NonIsoHLTNonIsoSingleElectronLWEt10EleIdEtFilter in Ele10LWEleIdL1R_vs_et"}])

hltlayoutW(dqmitems,"Ele10LWEleIdL1R/cluster shape cut",
           [{'path': "HLT/HLTEgammaValidation/HLT_Ele10_LW_EleId_L1RDQMWenu/efficiency_hltL1NonIsoHLTNonIsoSingleElectronLWEt10EleIdClusterShapeFilter_vs_eta_MC_matched", 'description':"per-object (MC matched) for hltL1NonIsoHLTNonIsoSingleElectronLWEt10EleIdClusterShapeFilter in Ele10LWEleIdL1R_vs_eta"},
            {'path': "HLT/HLTEgammaValidation/HLT_Ele10_LW_EleId_L1RDQMWenu/efficiency_hltL1NonIsoHLTNonIsoSingleElectronLWEt10EleIdClusterShapeFilter_vs_et_MC_matched", 'description':"per-object (MC matched) for hltL1NonIsoHLTNonIsoSingleElectronLWEt10EleIdClusterShapeFilter in Ele10LWEleIdL1R_vs_et"}])

hltlayoutW(dqmitems,"Ele10LWEleIdL1R/Hcal isolation",
           [{'path': "HLT/HLTEgammaValidation/HLT_Ele10_LW_EleId_L1RDQMWenu/efficiency_hltL1NonIsoHLTNonIsoSingleElectronLWEt10EleIdHcalIsolFilter_vs_eta_MC_matched", 'description':"per-object (MC matched) for hltL1NonIsoHLTNonIsoSingleElectronLWEt10EleIdHcalIsolFilter in Ele10LWEleIdL1R_vs_eta"},
            {'path': "HLT/HLTEgammaValidation/HLT_Ele10_LW_EleId_L1RDQMWenu/efficiency_hltL1NonIsoHLTNonIsoSingleElectronLWEt10EleIdHcalIsolFilter_vs_et_MC_matched",  'description':"per-object (MC matched) for hltL1NonIsoHLTNonIsoSingleElectronLWEt10EleIdHcalIsolFilter in Ele10LWEleIdL1R_vs_et"}])

hltlayoutW(dqmitems,"Ele10LWEleIdL1R/pixel match",
           [{'path': "HLT/HLTEgammaValidation/HLT_Ele10_LW_EleId_L1RDQMWenu/efficiency_hltL1NonIsoHLTNonIsoSingleElectronLWEt10EleIdPixelMatchFilter_vs_eta_MC_matched", 'description':"per-object (MC matched) for hltL1NonIsoHLTNonIsoSingleElectronLWEt10EleIdPixelMatchFilter in Ele10LWEleIdL1R_vs_eta"},
            {'path': "HLT/HLTEgammaValidation/HLT_Ele10_LW_EleId_L1RDQMWenu/efficiency_hltL1NonIsoHLTNonIsoSingleElectronLWEt10EleIdPixelMatchFilter_vs_et_MC_matched",  'description':"per-object (MC matched) for hltL1NonIsoHLTNonIsoSingleElectronLWEt10EleIdPixelMatchFilter in Ele10LWEleIdL1R_vs_et"}])

hltlayoutW(dqmitems,"Ele10LWEleIdL1R/ 1oE - 1op cut",
           [{'path': "HLT/HLTEgammaValidation/HLT_Ele10_LW_EleId_L1RDQMWenu/efficiency_hltL1NonIsoHLTNonIsoSingleElectronLWEt10EleIdOneOEMinusOneOPFilter_vs_eta_MC_matched", 'description':"per-object (MC matched) for hltL1NonIsoHLTNonIsoSingleElectronLWEt10EleIdOneOEMinusOneOPFilter in Ele10LWEleIdL1R_vs_eta"},
            {'path': "HLT/HLTEgammaValidation/HLT_Ele10_LW_EleId_L1RDQMWenu/efficiency_hltL1NonIsoHLTNonIsoSingleElectronLWEt10EleIdOneOEMinusOneOPFilter_vs_et_MC_matched", 'description':"per-object (MC matched) for hltL1NonIsoHLTNonIsoSingleElectronLWEt10EleIdOneOEMinusOneOPFilter in Ele10LWEleIdL1R_vs_et"}])

hltlayoutW(dqmitems,"Ele10LWEleIdL1R/ delta-eta cut",
           [{'path': "HLT/HLTEgammaValidation/HLT_Ele10_LW_EleId_L1RDQMWenu/efficiency_hltL1NonIsoHLTNonIsoSingleElectronLWEt10EleIdDetaFilter_vs_eta_MC_matched", 'description':"per-object (MC matched) for hltL1NonIsoHLTNonIsoSingleElectronLWEt10EleIdDetaFilter in Ele10LWEleIdL1R_vs_eta"},
            {'path': "HLT/HLTEgammaValidation/HLT_Ele10_LW_EleId_L1RDQMWenu/efficiency_hltL1NonIsoHLTNonIsoSingleElectronLWEt10EleIdDetaFilter_vs_et_MC_matched", 'description':"per-object (MC matched) for hltL1NonIsoHLTNonIsoSingleElectronLWEt10EleIdDetaFilter in Ele10LWEleIdL1R_vs_et"}])

hltlayoutW(dqmitems,"Ele10LWEleIdL1R/ delta-phi cut",
           [{'path': "HLT/HLTEgammaValidation/HLT_Ele10_LW_EleId_L1RDQMWenu/efficiency_hltL1NonIsoHLTNonIsoSingleElectronLWEt10EleIdDphiFilter_vs_eta_MC_matched", 'description':"per-object (MC matched) for hltL1NonIsoHLTNonIsoSingleElectronLWEt10EleIdDphiFilter in Ele10LWEleIdL1R_vs_eta"},
            {'path': "HLT/HLTEgammaValidation/HLT_Ele10_LW_EleId_L1RDQMWenu/efficiency_hltL1NonIsoHLTNonIsoSingleElectronLWEt10EleIdDphiFilter_vs_et_MC_matched", 'description':"per-object (MC matched) for hltL1NonIsoHLTNonIsoSingleElectronLWEt10EleIdDphiFilter in Ele10LWEleIdL1R_vs_et"}])


def hltLayoutGammaJet(i, p, *rows): i["HLT/HLTEgammaValidation/Photon Summary" + p] = DQMItem(layout=rows)
hltLayoutGammaJet(dqmitems,"/HLT_Photon10_L1R Efficiency vs Et",
                  [{'path':"HLT/HLTEgammaValidation/HLT_Photon10_L1R_DQMGammaJet/final_eff_vs_et", 'description':"Efficiency of HLT_Photon10_L1R vs Et of generated photon"}])
hltLayoutGammaJet(dqmitems,"/HLT_Photon10_L1R Efficiency vs eta",
                  [{'path':"HLT/HLTEgammaValidation/HLT_Photon10_L1R_DQMGammaJet/final_eff_vs_eta", 'description':"Efficiency of HLT_Photon10_L1R vs eta of generated photon"}])
hltLayoutGammaJet(dqmitems,"/L1 EgammaEt5 Efficiency vs et",
                  [{'path':"HLT/HLTEgammaValidation/HLT_Photon10_L1R_DQMGammaJet/efficiency_hltL1sRelaxedSingleEgammaEt5_vs_et_MC_matched", 'description':"Efficiency of L1 EgammaEt5 vs et of generated photon"}])
hltLayoutGammaJet(dqmitems,"/L1 EgammaEt5 Efficiency vs eta",
                  [{'path':"HLT/HLTEgammaValidation/HLT_Photon10_L1R_DQMGammaJet/efficiency_hltL1sRelaxedSingleEgammaEt5_vs_eta_MC_matched", 'description':"Efficiency of L1 EgammaEt5 vs eta of generated photon"}])
hltLayoutGammaJet(dqmitems,"/HLT_Photon15_LooseEcalIso_L1R Efficiency vs Et",
                  [{'path':"HLT/HLTEgammaValidation/HLT_Photon15_LooseEcalIso_L1R_DQMGammaJet/final_eff_vs_et",'description':"Efficiency of HLT_Photon15_LooseEcalIso_L1R vs Et of generated photon"}])
hltLayoutGammaJet(dqmitems,"/HLT_Photon15_LooseEcalIso_L1R Efficiency vs eta",
                  [{'path':"HLT/HLTEgammaValidation/HLT_Photon15_LooseEcalIso_L1R_DQMGammaJet/final_eff_vs_eta",'description':"Efficiency of HLT_Photon15_LooseEcalIso_L1R vs eta of generated photon"}])
hltLayoutGammaJet(dqmitems,"/HLT_Photon15_TrackIso_L1R Efficiency vs Et",
                  [{'path':"HLT/HLTEgammaValidation/HLT_Photon15_TrackIso_L1R_DQMGammaJet/final_eff_vs_et",'description':"Efficiency of HLT_Photon15_TrackIso_L1R vs Et of generated photon"}])
hltLayoutGammaJet(dqmitems,"/HLT_Photon15_TrackIso_L1R Efficiency vs eta",
                  [{'path':"HLT/HLTEgammaValidation/HLT_Photon15_TrackIso_L1R_DQMGammaJet/final_eff_vs_eta",'description':"Efficiency of HLT_Photon15_TrackIso_L1R vs eta of generated photon"}])


###---- MUON selection goes here: ----

def trigvalmuon(i, p, *rows): i["HLT/Muon/Efficiency Summary for " + p] = DQMItem(layout=rows)

menus = ["8E29"      , "1E31"      ]
paths = ["HLT_IsoMu3", "HLT_IsoMu9"]

for menuNum in range(len(menus)):

    thisMenu  = menus[menuNum]
    thisDir   = "HLT/Muon/Distributions/" + paths[menuNum]
    docString = " (" + paths[menuNum] + " path) (<a href=\"https://twiki.cern.ch/twiki/bin/view/CMS/MuonHLTOfflinePerformance\">documentation</a>)"

    trigvalmuon(dqmitems, thisMenu + "/pT Turn-On for L1",
        [{'path': thisDir + "/genTurnOn_L1", 'description':"Efficiency to find an L1 muon associated to a generated muon vs. pT" + docString}])

    trigvalmuon(dqmitems, thisMenu + "/pT Turn-On for L2",
        [{'path': thisDir + "/genTurnOn_L2", 'description':"Efficiency to find an L2 muon associated to an L1 muon vs. pT" + docString}])

    trigvalmuon(dqmitems, thisMenu + "/pT Turn-On for L2 Isolation",
        [{'path': thisDir + "/genTurnOn_L2Iso", 'description':"Efficiency to find an isolated L2 muon associated to an L1 muon vs. pT" + docString}])

    trigvalmuon(dqmitems, thisMenu + "/pT Turn-On for L3",
        [{'path': thisDir + "/genTurnOn_L3", 'description':"Efficiency to find an L3 muon associated to an L1 muon vs. pT" + docString}])

    trigvalmuon(dqmitems, thisMenu + "/pT Turn-On for L3 Isolation",
        [{'path': thisDir + "/genTurnOn_L3Iso", 'description':"Efficiency to find an isolated L3 muon associated to an L1 muon vs. pT" + docString}])

    trigvalmuon(dqmitems, thisMenu + "/Efficiency of L1",
        [{'path': thisDir + "/genEffEta_L1", 'description':"Efficiency to find an L1 muon associated to a generated muon vs. eta" + docString}])

    trigvalmuon(dqmitems, thisMenu + "/Efficiency of L2",
        [{'path': thisDir + "/genEffEta_L2", 'description':"Efficiency to find an L2 muon associated to an L1 muon vs. eta" + docString}])

    trigvalmuon(dqmitems, thisMenu + "/Efficiency of L2 Isolation",
        [{'path': thisDir + "/genEffEta_L2Iso", 'description':"Efficiency to find an isolated L2 muon associated to an L1 muon vs. eta" + docString}])

    trigvalmuon(dqmitems, thisMenu + "/Efficiency of L3",
        [{'path': thisDir + "/genEffEta_L3", 'description':"Efficiency to find an L3 muon associated to an L1 muon vs. eta" + docString}])

    trigvalmuon(dqmitems, thisMenu + "/Efficiency of L3 Isolation",
        [{'path': thisDir + "/genEffEta_L3Iso", 'description':"Efficiency to find an isolated L3 muon associated to an L1 muon vs. eta" + docString}])

##     trigvalmuon(dqmitems, thisMenu + "/Number of Objects Per Step",
##         [{'path': thisDir + "/numObjects", 'description':"Number of objects found in generated and reconstructed muon collections, and at each step of the " + paths[menuNum] + " trigger path"}])

##     trigvalmuon(dqmitems, thisMenu + "/Number of Orphans per Step",
##         [{'path': thisDir + "/genNumOrphans", 'description':"Number of objects in each step of the " + paths[menuNum] + " trigger path which were not matched to a generated muon"}])


###---- TAU selection goes here: ----
def trigvaltau(i, p, *rows): i["HLT/TauRelVal/Summary For " + p] = DQMItem(layout=rows)

for lumi in ["Default", "8E29","1E31"]:
    trigvaltau(dqmitems,"MC_"+lumi+" Menu/Double Tau Path Performance",
               [{'path': "HLT/TauRelVal/MC_"+lumi+ "/DoubleTau/EfficiencyRefInput",
                 'description':"Efficiency of the Double Tau Path with ref to MC for "+lumi},
                {'path': "HLT/TauRelVal/MC_"+lumi+ "/DoubleTau/EfficiencyRefPrevious",
                 'description':"Efficiency of the Double Tau Path with ref to previous step( "+lumi+")"}

               ])
    trigvaltau(dqmitems,"MC_"+lumi+" Menu/Single Tau Path Performance",
               [
                {'path': "HLT/TauRelVal/MC_"+lumi+ "/SingleTau/EfficiencyRefInput",
                 'description':"Efficiency of the Single Tau Path with ref to MC for "+lumi},
                {'path': "HLT/TauRelVal/MC_"+lumi+ "/SingleTau/EfficiencyRefPrevious",
                 'description':"Efficiency of the Single Tau Path with ref to previous step( "+lumi+")"}
               ])
    trigvaltau(dqmitems,"MC_"+lumi+" Menu/L1 Efficency",
               [
                  {'path': "HLT/TauRelVal/MC_"+lumi+ "/L1/L1TauEtEff", 'description':"L1 Tau Efficiency vs pt with  ref to MC for "+lumi},
                  {'path': "HLT/TauRelVal/MC_"+lumi+ "/L1/L1TauEtaEff", 'description':"L1 Tau Efficiency vs pt with  ref to MC for "+lumi},
               ])

               
    trigvaltau(dqmitems,"MC_"+lumi+" Menu/L2 Efficency",
               [
                  {'path': "HLT/TauRelVal/MC_"+lumi+ "/L2/L2TauEtEff", 'description':"L2 Tau Efficiency vs pt with  ref to MC for "+lumi},
                  {'path': "HLT/TauRelVal/MC_"+lumi+ "/L2/L2TauEtaEff", 'description':"L2 Tau Efficiency vs pt with  ref to MC for "+lumi},
               ])

    trigvaltau(dqmitems,"MC_"+lumi+" Menu/L1 Resolution",
               [
                  {'path': "HLT/TauRelVal/MC_"+lumi+ "/L1/L1TauEtResol", 'description':"L1 Tau ET resolution with ref to MC  for "+lumi}
               ])

    trigvaltau(dqmitems,"MC_"+lumi+" Menu/L2 Resolution",
               [
                  {'path': "HLT/TauRelVal/MC_"+lumi+ "/L2/L2TauEtResol", 'description':"L2 Tau ET resolution with ref to MC  for "+lumi}
               ])
###---- JETMET selection goes here: ----
#def trigvaljetmet(i, p, *rows): i["HLT//Preselection" + p] = DQMItem(layout=rows)

###---- BJET selection goes here: ----
#def trigvalbjet(i, p, *rows): i["HLT//Preselection" + p] = DQMItem(layout=rows)

###---- ALCA selection goes here: ----
def trigvalalca(i, p, *rows): i["HLT/AlCaEcalPi0/Preselection" + p] = DQMItem(layout=rows)

###---- TOP selection goes here: ----
def trigvaltop(i, p, *rows): i["HLT/Top/Preselection" + p] = DQMItem(layout=rows)

###---- HEAVYFLAVOR selection goes here: ----
def trigvalbphys(i, p, *rows): i["HLT/HeavyFlavor/Preselection" + p] = DQMItem(layout=rows)

###---- SUSYEXO selection goes here: ----
def trigvalsusybsm(i, p, *rows): i["HLT/SusyExo/Preselection" + p] = DQMItem(layout=rows)

###---- HIGGS selection goes here: ----
#def trigvalhiggs(i, p, *rows): i["HLT//Preselection" + p] = DQMItem(layout=rows)
###---- QCD selection goes here: ----
#def trigvalqcd(i, p, *rows): i["HLT//Preselection" + p] = DQMItem(layout=rows)
