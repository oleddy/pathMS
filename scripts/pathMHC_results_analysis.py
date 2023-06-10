import pandas as pd
import argparse
import numpy as np
from matplotlib import pyplot as plt

def unique(input):
    return list(set(input))

def self_bacterial_split(data):
    return data.loc[data['TB-derived']], data.loc[np.logical_not(data['TB-derived'])]

def unique_pep_and_prot(data):
    all_proteins = []
    for accessions in data['Protein Accessions']:
        all_proteins += accessions.split(';')
    return unique(data['Annotated Sequence']), unique(all_proteins)

def n_new(baseline, new):
    return len(unique(baseline + new)) - len(baseline)

def percent(part, whole):
    return 100.*part/(part + whole)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', help = 'DDA run 1 filtered_psms_organism.csv file', required = True)
    parser.add_argument('-b', help = 'DDA run 2 filetered_psms_organism.csv file', required = True)
    parser.add_argument('-c', help = 'PRM run filtered_psms_organism.csv file', required = True)

    args = parser.parse_args()

    data_dfs = [pd.read_csv(file) for file in [args.a, args.b, args.c]] #read in data from all 3 bacteria-containing runs
    dda1_data, dda2_data, prm_data = data_dfs #give the dfs distinct names
    (dda1_bac, dda1_self), (dda2_bac, dda2_self), (prm_bac, prm_self) = [self_bacterial_split(data) for data in data_dfs] #separate out bacterial and self PSM data
    
    (dda1_bac_pep, dda1_bac_prot), (dda2_bac_pep, dda2_bac_prot), (prm_bac_pep, prm_bac_prot) = [unique_pep_and_prot(bac_data) for bac_data in [dda1_bac, dda2_bac, prm_bac]] #unpack unique bacterial peptides and proteins
    (dda1_self_pep, dda1_self_prot), (dda2_self_pep, dda2_self_prot), (prm_self_pep, prm_self_prot) = [unique_pep_and_prot(self_data) for self_data in [dda1_self, dda2_self, prm_self]] #unpqck unique self peptides and proteins

    print(dda1_bac_pep)
    print(len(dda1_bac_pep))
    print(dda2_bac_pep)
    print(prm_bac_pep)
    
    #determine number of unique new peptides and proteins in PRM run
    prm_new_bac_pep = n_new(dda1_bac_pep, prm_bac_pep)
    print('PRM new bacterial peptides: ' + str(prm_new_bac_pep))
    prm_new_bac_prot = n_new(dda1_bac_prot, prm_bac_prot)
    print('PRM new bacterial proteins: ' + str(prm_new_bac_prot))

    #determine number of unique new p
    dda2_new_bac_pep = n_new(dda1_bac_pep, dda2_bac_pep)
    print('DDA2 new bacterial peptides: ' + str(dda2_new_bac_pep))
    dda2_new_bac_prot = n_new(dda1_bac_prot, dda2_bac_prot)
    print('DDA2 new bacterial proteins: ' + str(dda2_new_bac_prot))

    #determine % bacterial peptides and % bacterial proteins for each run

    #DDA1
    dda1_bac_frac_pep = percent(len(dda1_bac_pep), len(dda1_self_pep))
    print('dda1 bacterial peptide fraction: ' + str(dda1_bac_frac_pep))
    dda1_bac_frac_prot = percent(len(dda1_bac_prot), len(dda1_self_prot))
    print('dda1 bacterial protein fraction: ' + str(dda1_bac_frac_prot))

    #DDA2
    dda2_bac_frac_pep = percent(len(dda2_bac_pep), len(dda2_self_pep))
    print('dda2 bacterial peptide fraction: ' + str(dda2_bac_frac_pep))
    dda2_bac_frac_prot = percent(len(dda2_bac_prot), len(dda2_self_prot))
    print('dda2 bacterial protein fraction: ' + str(dda2_bac_frac_prot))

    #PRM
    prm_bac_frac_pep = percent(len(prm_bac_pep), len(prm_self_pep))
    print('prm bacterial peptide fraction: ' + str(prm_bac_frac_pep))
    prm_bac_frac_prot = percent(len(prm_bac_prot), len(prm_self_prot))
    print('prm bacterial protein fraction: ' + str(prm_bac_frac_prot))


