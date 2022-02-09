import numpy as np
import pandas as pd
import uproot3 as uproot
from math import sqrt, log
import math
import ROOT
# from config import *

years = [2016, 2017, 2018]
eos_path = '/eos/cms/store/group/phys_higgs/cmshzz4l/cjlst/RunIILegacy/200205_CutBased/' #it is used for FR
branches_ZX = ['ZZMass', 'Z1Flav', 'Z2Flav', 'LepLepId', 'LepEta', 'LepPt', 'Z1Mass', 'Z2Mass', 'ZZPt', 'ZZEta',
               'helcosthetaZ1','helcosthetaZ2', 'helphi', 'costhetastar', 'phistarZ1', 'ZZPhi',
               'pTj1', 'pTj2', 'absdetajj',
               'JetPt_JESUp','JetPt_JESDown','JetEta','JetPhi','JetMass',
               'pTHj', 'pTHjj', 'mHj', 'mHjj', 'detajj', 'dphijj', 'mjj', 'njets_pt30_eta2p5', 'ZZy',
               'D0m', 'Dcp', 'D0hp', 'Dint', 'DL1', 'DL1int', 'DL1Zg', 'DL1Zgint', 'TCjmax', 'TBjmax']

def add_leadjet(pt,eta,phi,mass):
	_pTj1 = 0.0
	_mj1 = 0.0
	_etaj1 = 0.0
	_phij1 = 0.0
	index = -1
	_j = ROOT.TLorentzVector()
	if len(pt) == 0:
		_j.SetPtEtaPhiM(0,0,0,0)
	else:
	    for i in range(len(pt)):
	        if (pt[i]>30 and abs(eta[i])<4.7 and pt[i] > _pTj1):
	        	_pTj1 = pt[i]
	        	index = i
	    _j.SetPtEtaPhiM(_pTj1,eta[index],phi[index],mass[index])
	return _j


def add_subleadjet(pt,eta,phi,mass,leadJet):
    _pTj2 = 0.0
    _mj2 = 0.0
    _etaj2 = 0.0
    _phij2 = 0.0
    _j = ROOT.TLorentzVector()
    for i in range(len(pt)):
        if (pt[i]>30 and abs(eta[i])<4.7 and pt[i] > _pTj2 and leadJet.Pt()-pt[i] > 0.00001):
            _pTj2 = pt[i]
            _mj2 = mass[i]
            _etaj2 = eta[i]
            _phij2 = phi[i]
    _j.SetPtEtaPhiM(_pTj2,_etaj2,_phij2,_mj2)
    return _j


def FindFinalState(z1_flav, z2_flav):
    if(z1_flav == -121):
        if(z2_flav == +121): return 0 # 4e
        if(z2_flav == +169): return 2 # 2e2mu
    if(z1_flav == -169):
        if(z2_flav == +121): return 3 # 2mu2e
        if(z2_flav == +169): return 1 # 4mu

def FindFinalState_reco(flav):
    if flav == 0: return '4e'
    elif flav == 1: return '4mu'
    else: return '2e2mu'

def tc(pt,eta,phi,mass,H):
    _TCjmax = 0
    for i in range(len(pt)):
        theJet = ROOT.TLorentzVector()
        theJet.SetPtEtaPhiM(pt[i],eta[i],phi[i],mass[i]);
        _TCj = sqrt(theJet.Pt()**2 + theJet.M()**2)/(2*math.cosh(theJet.Rapidity() - H.Rapidity()))
        if _TCj > _TCjmax: _TCjmax = _TCj
    return _TCjmax

def tb(pt,eta,phi,mass,H):
    _TBjmax = 0
    for i in range(len(pt)):
        theJet = ROOT.TLorentzVector()
        theJet.SetPtEtaPhiM(pt[i],eta[i],phi[i],mass[i]);
        _TBj = sqrt(theJet.Pt()**2 + theJet.M()**2)*math.exp(-1*(theJet.Rapidity() - H.Rapidity()));
        if _TBj > _TBjmax: _TBjmax = _TBj
    return _TBjmax

def GetFakeRate(lep_Pt, lep_eta, lep_ID, g_FR_mu_EB, g_FR_mu_EE, g_FR_e_EB, g_FR_e_EE):

    if(lep_Pt >= 80.):
        my_lep_Pt = 79.
    else:
        my_lep_Pt = lep_Pt

    my_lep_ID = abs(lep_ID)

    if((my_lep_Pt > 5) & (my_lep_Pt <= 7)): bin = 0
    if((my_lep_Pt >  7) & (my_lep_Pt <= 10)): bin = 1
    if((my_lep_Pt > 10) & (my_lep_Pt <= 20)): bin = 2
    if((my_lep_Pt > 20) & (my_lep_Pt <= 30)): bin = 3
    if((my_lep_Pt > 30) & (my_lep_Pt <= 40)): bin = 4
    if((my_lep_Pt > 40) & (my_lep_Pt <= 50)): bin = 5
    if((my_lep_Pt > 50) & (my_lep_Pt <= 80)): bin = 6

    if(abs(my_lep_ID) == 11): bin = bin-1 # There is no [5, 7] bin in the electron fake rate

    if(my_lep_ID == 11):
        if(abs(lep_eta) < 1.479): return g_FR_e_EB.GetY()[bin]
        else: return g_FR_e_EE.GetY()[bin]

    if(my_lep_ID == 13):
        if(abs(lep_eta) < 1.2): return g_FR_mu_EB.GetY()[bin]
        else: return g_FR_mu_EE.GetY()[bin]


# Open Fake Rates files
def openFR(year):
    fnameFR = eos_path + 'FRfiles/FakeRates_SS_%i.root' %year
    file = uproot.open(fnameFR)

    # Retrieve FR from TGraphErrors
    input_file_FR = ROOT.TFile(fnameFR)

    g_FR_mu_EB = input_file_FR.Get("FR_SS_muon_EB")
    g_FR_mu_EE = input_file_FR.Get("FR_SS_muon_EE")
    g_FR_e_EB  = input_file_FR.Get("FR_SS_electron_EB")
    g_FR_e_EE  = input_file_FR.Get("FR_SS_electron_EE")

    return g_FR_mu_EB, g_FR_mu_EE, g_FR_e_EB, g_FR_e_EE


# Find final state
def findFSZX(df):
    df['FinState'] = [FindFinalState(x,y) for x,y in zip(df['Z1Flav'], df['Z2Flav'])]
    df['FinState_reco'] = [FindFinalState_reco(x) for x in df['FinState']]
    return df


# Define combination coefficients
def comb(year):
    if year == 2016:
        cb_SS = np.array([
            1.23628,   # 4e
            0.95433,   # 4mu
            1.0726,    # 2e2mu
            1.0726,    # 2mu2e
        ])
    elif year == 2017:
        cb_SS = np.array([
            1.1934,   # 4e
            0.99669,   # 4mu
            1.0569,    # 2e2mu
            1.0569,    # 2mu2e
        ])
    else:
        cb_SS = np.array([
            1.2087,   # 4e
            0.9878,   # 4mu
            1.0552,    # 2e2mu
            1.0552,    # 2mu2e
        ])

    return cb_SS


# Define ration OppositeSign/SameSign
def ratio(year):
    if year == 2016:
        fs_ROS_SS = np.array([
            1.00245,   # 4e
            0.998863,  # 4mu
            1.03338,   # 2e2mu
            0.998852,  # 2mu2e
            ])
    elif year == 2017:
        fs_ROS_SS = np.array([
            1.01198,   # 4e
            1.03949,  # 4mu
            1.013128,   # 2e2mu
            1.00257,  # 2mu2e
            ])
    else:
        fs_ROS_SS = np.array([
            1.00568,   # 4e
            1.02926,  # 4mu
            1.03226,   # 2e2mu
            1.00432,  # 2mu2e
            ])

    return fs_ROS_SS

def count_jets(pt,eta,phi,mass):
    n = 0
    for i in range(len(pt)):
        if pt[i]>30 and abs(eta[i])<4.7: n = n + 1
    return n

def tetra_Higgs(mass,eta,phi,pt):
    h = ROOT.TLorentzVector()
    h.SetPtEtaPhiM(pt,eta,phi,mass)
    return h

# Calculate yield for Z+X (data in CRZLL control region are scaled in signal region through yields)
def ZXYield(df, year, g_FR_mu_EB, g_FR_mu_EE, g_FR_e_EB, g_FR_e_EE):
    cb_SS = comb(year)
    fs_ROS_SS = ratio(year)

    vec = df.to_numpy()
    Yield = np.zeros(len(vec), float)
    for i in range(len(vec)):
        finSt  = vec[i][len(branches_ZX)] #Final state information is in the last column which is added afterthe last column of branches_ZX
        lepPt  = vec[i][5]
        lepEta = vec[i][4]
        lepID  = vec[i][3]
        Yield[i] = cb_SS[finSt] * fs_ROS_SS[finSt] * GetFakeRate(lepPt[2], lepEta[2], lepID[2], g_FR_mu_EB, g_FR_mu_EE, g_FR_e_EB, g_FR_e_EE) * GetFakeRate(lepPt[3], lepEta[3], lepID[3], g_FR_mu_EB, g_FR_mu_EE, g_FR_e_EB, g_FR_e_EE)

    return Yield


def doZX(year, g_FR_mu_EB, g_FR_mu_EE, g_FR_e_EB, g_FR_e_EE):
    keyZX = 'CRZLL'

    data = '/eos/user/a/atarabin/Data/reducedTree_AllData_%i.root' %year
    ttreeZX = uproot.open(data)[keyZX]

    dfZX = ttreeZX.pandas.df(branches_ZX, flatten = False)
    dfZX = dfZX[dfZX.Z2Flav > 0] #Keep just same-sign events
    dfZX = findFSZX(dfZX)

    dfZX['yield_SR'] = ZXYield(dfZX, year, g_FR_mu_EB, g_FR_mu_EE, g_FR_e_EB, g_FR_e_EE)

    # Leading jets
    dfZX['j1_jesup'] = [add_leadjet(row[0],row[1],row[2],row[3]) for row in dfZX[['JetPt_JESUp','JetEta','JetPhi','JetMass']].values]
    dfZX['j1_jesdn'] = [add_leadjet(row[0],row[1],row[2],row[3]) for row in dfZX[['JetPt_JESDown','JetEta','JetPhi','JetMass']].values]
    # Subleading jets
    dfZX['j2_jesup'] = [add_subleadjet(row[0],row[1],row[2],row[3],row[4]) for row in dfZX[['JetPt_JESUp','JetEta','JetPhi','JetMass','j1_jesup']].values]
    dfZX['j2_jesdn'] = [add_subleadjet(row[0],row[1],row[2],row[3],row[4]) for row in dfZX[['JetPt_JESDown','JetEta','JetPhi','JetMass','j1_jesdn']].values]

    dfZX['Higgs'] = [tetra_Higgs(row[0],row[1],row[2],row[3]) for row in dfZX[['ZZMass', 'ZZEta', 'ZZPhi', 'ZZPt']].values]

    dfZX['pTj1_jesup'] = [x.Pt() for x in dfZX['j1_jesup']]
    dfZX['pTj1_jesdn'] = [x.Pt() for x in dfZX['j1_jesdn']]
    dfZX['pTj2_jesup'] = [x.Pt() for x in dfZX['j2_jesup']]
    dfZX['pTj2_jesdn'] = [x.Pt() for x in dfZX['j2_jesdn']]
    dfZX['njets_pt30_eta2p5_jesup'] = [count_jets(row[0],row[1],row[2],row[3]) for row in dfZX[['JetPt_JESUp','JetEta','JetPhi','JetMass']].values]
    dfZX['njets_pt30_eta2p5_jesdn'] = [count_jets(row[0],row[1],row[2],row[3]) for row in dfZX[['JetPt_JESDown','JetEta','JetPhi','JetMass']].values]
    dfZX['mjj_jesup'] = [(j1+j2).M() if j2.Pt()>0 else -1 for j1,j2 in zip(dfZX['j1_jesup'],dfZX['j2_jesup'])]
    dfZX['mjj_jesdn'] = [(j1+j2).M() if j2.Pt()>0 else -1 for j1,j2 in zip(dfZX['j1_jesdn'],dfZX['j2_jesdn'])]
    dfZX['pTHj_jesup'] = [(H+j1).Pt() if j1.Pt()>0 else -1 for H,j1 in zip(dfZX['Higgs'],dfZX['j1_jesup'])]
    dfZX['pTHj_jesdn'] = [(H+j1).Pt() if j1.Pt()>0 else -1 for H,j1 in zip(dfZX['Higgs'],dfZX['j1_jesdn'])]
    dfZX['pTHjj_jesup'] = [(row[0]+row[1]+row[2]).Pt() if row[2].Pt()>0 else -1 for row in dfZX[['Higgs','j1_jesup','j2_jesup']].values]
    dfZX['pTHjj_jesdn'] = [(row[0]+row[1]+row[2]).Pt() if row[2].Pt()>0 else -1 for row in dfZX[['Higgs','j1_jesdn','j2_jesdn']].values]
    dfZX['mHj_jesup'] = [(H+j1).M() if j1.Pt()>0 else -1 for H,j1 in zip(dfZX['Higgs'],dfZX['j1_jesup'])]
    dfZX['mHj_jesdn'] = [(H+j1).M() if j1.Pt()>0 else -1 for H,j1 in zip(dfZX['Higgs'],dfZX['j1_jesdn'])]
    dfZX['mHjj_jesup'] = [(row[0]+row[1]+row[2]).M() if row[2].Pt()>0 else -1 for row in dfZX[['Higgs','j1_jesup','j2_jesup']].values]
    dfZX['mHjj_jesdn'] = [(row[0]+row[1]+row[2]).M() if row[2].Pt()>0 else -1 for row in dfZX[['Higgs','j1_jesdn','j2_jesdn']].values]
    dfZX['TCjmax_jesup'] = [tc(row[0],row[1],row[2],row[3],row[4]) for row in dfZX[['JetPt_JESUp','JetEta','JetPhi','JetMass','Higgs']].values]
    dfZX['TCjmax_jesdn'] = [tc(row[0],row[1],row[2],row[3],row[4]) for row in dfZX[['JetPt_JESDown','JetEta','JetPhi','JetMass','Higgs']].values]
    dfZX['TBjmax_jesup'] = [tb(row[0],row[1],row[2],row[3],row[4]) for row in dfZX[['JetPt_JESUp','JetEta','JetPhi','JetMass','Higgs']].values]
    dfZX['TBjmax_jesdn'] = [tb(row[0],row[1],row[2],row[3],row[4]) for row in dfZX[['JetPt_JESDown','JetEta','JetPhi','JetMass','Higgs']].values]
    dfZX['absdetajj_jesup'] = [abs(j1.Eta()-j2.Eta()) if j2.Pt()>0 else -1 for j1,j2 in zip(dfZX['j1_jesup'],dfZX['j2_jesup'])]
    dfZX['absdetajj_jesdn'] = [abs(j1.Eta()-j2.Eta()) if j2.Pt()>0 else -1 for j1,j2 in zip(dfZX['j1_jesdn'],dfZX['j2_jesdn'])]

    dfZX['ZZPt_jesup'] = dfZX['ZZPt']
    dfZX['ZZPt_jesdn'] = dfZX['ZZPt']

    return dfZX

#------------------------- Main -------------------------
def zx():
    d_ZX = {}
    for year in years:
        g_FR_mu_EB, g_FR_mu_EE, g_FR_e_EB, g_FR_e_EE = openFR(year)
        d_ZX[year] = doZX(year, g_FR_mu_EB, g_FR_mu_EE, g_FR_e_EB, g_FR_e_EE)
#         d_ZX[year] = add_lead_lep(d_ZX[year])
#         d_ZX[year] = add_rapidity(d_ZX[year])
        print(year, 'done')
    return d_ZX