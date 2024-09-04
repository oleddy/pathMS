import pandas as pd
import argparse
from pyteomics import mass
import numpy as np
from numpy import logical_and
from uniprot_id_map import uniprot_ids_to_names

mz_tol_ppm = 10.
mz_tol = mz_tol_ppm/1e6
rt_tol = 1.5

def has_match(precursor, psms, ppm = 10):
    tolerance = precursor['m/z']*ppm/1e6
    in_mz_range = np.abs(psms['mz_' + str(int(precursor['z']))] - precursor['m/z']) <= tolerance
    return np.any(in_mz_range)

def get_match(psm_data, peak):
    in_rt_range = logical_and(psm_data['retentionTimeMin'] >= (peak['RT Time (min)'] - rt_tol), psm_data['retentionTimeMin'] <= (peak['RT Time (min)'] + rt_tol))
    in_mz_range = logical_and(psm_data['parent_m_over_z']*(1 + mz_tol) >= peak['m/z'], psm_data['parent_m_over_z']*(1. - mz_tol) <= peak['m/z'])
    matches = psm_data.loc[logical_and(in_rt_range, in_mz_range)]
    if not matches.empty:
        return matches.iloc[0]
    else:
        return pd.Series({key : pd.NA for key in matches.columns})

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', help = 'all peptide data', required = True)
    # parser.add_argument('-l', help = 'listeria high confidence peptides', required = True)
    parser.add_argument('-i', help = 'inclusion list', required = True)
    parser.add_argument('-o', help = 'output path', required = True)

    args = parser.parse_args()

    all_peptides = pd.read_csv(args.p)
    # listeria_peptides = pd.read_csv(args.l)
    inclusion_list = pd.read_csv(args.i)

    gene_name_map = uniprot_ids_to_names(all_peptides['Protein accession(s)'])
    all_peptides = all_peptides.join([all_peptides, gene_name_map])
    print(all_peptides.head())

    all_peptides['PTM'] = all_peptides['PTM'].astype(str)

    human_peptides = all_peptides.loc[all_peptides['Species of origin'].str.contains('human')]
    # listeria_peptides = all_peptides.loc[all_peptides['Peptide'].isin(listeria_peptides['Peptide sequence'])]

    # DDA_ratio = len(listeria_peptides)/(len(human_peptides) + len(listeria_peptides))

    mz_2s = []
    mz_3s = []
    mz_4s = []

    for _, peptide in human_peptides.iterrows():
        mz_2 = mass.calculate_mass(sequence = peptide['Peptide'], ion_type = 'M', charge = 2)
        mz_3 = mass.calculate_mass(sequence = peptide['Peptide'], ion_type = 'M', charge = 3)
        mz_4 = mass.calculate_mass(sequence = peptide['Peptide'], ion_type = 'M', charge = 4)

        if 'Oxidation' in peptide['PTM']:
            mz_2 += 15.994915/2.
            mz_3 += 15.994915/3.
            mz_4 += 15.994915/4.
        
        if 'Acetylation' in peptide['PTM']:
            mz_2 += 42.010565/2.
            mz_3 += 42.010565/3.
            mz_4 += 42.010565/4.

        mz_2s.append(mz_2)
        mz_3s.append(mz_3)
        mz_4s.append(mz_4)

    human_peptides['mz_2'] = mz_2s
    human_peptides['mz_3'] = mz_3s
    human_peptides['mz_4'] = mz_4s
    
    

    output_df = all_peptides.copy()
    output_df.columns = output_df.columns + all_peptides.columns


    for i, peak in inclusion_list.iterrows():
        output_df.loc[i, all_peptides.columns] = get_match(all_peptides, peak)
    
    output_df.to_csv(args.o)

