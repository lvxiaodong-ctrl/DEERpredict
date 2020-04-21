import pytest
import MDAnalysis
import os
import sys
import numpy as np
from DEERpredict.PRE import PREpredict
import pandas as pd

@pytest.fixture
def load_expPREs(path,labels,tau_c):
    data = {}
    for label in labels:
        resnums, data[label] = np.loadtxt(path+'/PRE_1nti_{:g}-{:d}_CB.dat'.format(tau_c,label),unpack=True)
    df = pd.DataFrame(data,index=resnums)
    df.rename_axis('residue', inplace=True)
    df.rename_axis('label', axis='columns',inplace=True)
    return resnums, df

@pytest.fixture
def load_calcPREs(path,labels):
    data = {}
    for label in labels:
        resnums, data[label], _ = np.loadtxt(path+'/res-{:d}.dat'.format(label),unpack=True)
    df = pd.DataFrame(data, index=resnums)
    df.rename_axis('residue', inplace=True)
    df.rename_axis('label', axis='columns',inplace=True)
    return resnums, df

@pytest.fixture
def calcIratio(path,tau_c,args):
    u, label, tau_t, r_2, Cbeta = args
    PRE = PREpredict(u, label, output_prefix = path+'/calcPREs/res', weights = False,
          load_file = False, tau_t = tau_t*1e-9, log_file = path+'/calcPREs/log', delay = 10e-3,
          tau_c = tau_c*1e-09, k = 1.23e16, r_2 = r_2, temperature = 298, Z_cutoff = 0.2, Cbeta = Cbeta,
          atom_selection = 'H', wh = 750)
    PRE.run()

def test_PRE(load_expPREs,load_calcPREs,calcIratio):
    u = MDAnalysis.Universe('data/ACBP/1nti.pdb')
    labels = [17,36,46,65,86]
    for tau_c in [0.1,1]: 
        tau_t = tau_c if tau_c < 0.5 else 0.5
        for label in labels:
            calcIratio('data/ACBP',tau_c,[u, label, tau_t, 12.6, True])
        resnums, precalcPREs = load_precalcPREs('data/ACBP/precalcPREs',labels,tau_c)
        resnums, calcPREs = load_calcPREs('data/ACBP/calcPREs',labels)
        assert np.power(precalcPREs-calcPREs,2).sum().sum() < 0.2
