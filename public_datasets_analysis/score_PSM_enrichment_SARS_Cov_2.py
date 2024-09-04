import pandas as pd
import argparse

if __name__ =='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', help = 'input file (PSM-peak matches)', required = True)
    parser.add_argument('-r', help = 'reference PSM file', required = True)
    parser.add_argument('-f', help = 'filename', required = False, default = 'fxn01')
    args = parser.parse_args()

    data = pd.read_csv(args.i)
    species = data['species']
    total_matched_psms = sum([not pd.isna(psm_species) for psm_species in species])
    cov_peptides = sum([psm_species == 'SARSCOV2_NC_045512.2' for psm_species in species])
    enriched_fraction = cov_peptides/total_matched_psms

    reference_data = pd.read_csv(args.r, sep = ';')
    reference_data = reference_data.drop_duplicates(subset = ['sequence','parent_m_over_z'])
    reference_data = reference_data.loc[reference_data['filename'].str.contains(args.f)]
    total_psms = len(reference_data)
    cov_peptides = sum([species == 'SARSCOV2_NC_045512.2' for species in reference_data['species']])

    unenriched_fraction = cov_peptides/total_psms

    print('% Viral in enriched: ' + str(100.*enriched_fraction))
    print('% viral unenriched: ' +  str(100.*unenriched_fraction))
    print('fold enrichment: ' + str(enriched_fraction/unenriched_fraction))