import pandas as pd
import argparse
from pyteomics import mass
import numpy as np

def has_match(precursor, psms, ppm = 10):
    tolerance = precursor['m/z']*ppm/1e6
    in_mz_range = np.abs(psms['mz_' + str(int(precursor['z']))] - precursor['m/z']) <= tolerance
    return np.any(in_mz_range)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', help = 'all peptide data', required = True)
    parser.add_argument('-l', help = 'listeria high confidence peptides', required = True)
    parser.add_argument('-i', help = 'inclusion list', required = True)

    args = parser.parse_args()

    all_peptides = pd.read_csv(args.p)
    listeria_peptides = pd.read_csv(args.l)
    inclusion_list = pd.read_csv(args.i)

    all_peptides['PTM'] = all_peptides['PTM'].astype(str)

    human_peptides = all_peptides.loc[all_peptides['Species of origin'].str.contains('human')]
    listeria_peptides = all_peptides.loc[all_peptides['Peptide'].isin(listeria_peptides['Peptide sequence'])]

    DDA_ratio = len(listeria_peptides)/(len(human_peptides) + len(listeria_peptides))

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
    
    mz_2s = []
    mz_3s = []
    mz_4s = []

    for _, peptide in listeria_peptides.iterrows():
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

    listeria_peptides['mz_2'] = mz_2s
    listeria_peptides['mz_3'] = mz_3s
    listeria_peptides['mz_4'] = mz_4s

    human_matches = sum([has_match(precursor, human_peptides, ppm = 10) for _, precursor in inclusion_list.iterrows()])
    listeria_matches = sum([has_match(precursor, listeria_peptides, ppm = 10) for _, precursor in inclusion_list.iterrows()])

    enriched_ratio = listeria_matches/(listeria_matches + human_matches)

    print('DDA percentage: ' + str(100.*DDA_ratio))
    print('enriched percentage: ' + str(100.*enriched_ratio))
    print('fold enrichment: ' + str(enriched_ratio/DDA_ratio))