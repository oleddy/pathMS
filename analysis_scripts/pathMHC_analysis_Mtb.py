import pandas as pd
import argparse

'''
Takes in spreadsheets of PSMs (for DDA and PRM runs) with a boolean field (TB-derived) indicating whether they are
self-derived or pathogen-derived and analyzes the number and proportion of unique peptides in each that are pathogen-derived,
as well as the number of pathogen-derived peptides that are unique to the PRM run and were not found by DDA. 
'''

def get_unique_pathogen_peptides(psms):
    psms_unique = psms.drop_duplicates(subset = ['Annotated Sequence'])
    psms_path = psms_unique.loc[psms_unique['TB-derived']]
    percent_path = 100.*(psms_path/psms_unique)
    return percent_path, psms_path['Annotated Sequence']

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', help = 'DDA filtered PSMs file', required = True)
    parser.add_argument('-p', help = 'PRM filtered PSMs file', required = True)

    args = parser.parse_args()

    dda_data = pd.read_csv(args.d)
    prm_data = pd.read_csv(args.p)

    dda_percent, dda_path = get_unique_pathogen_peptides(dda_data)
    prm_percent, prm_path = get_unique_pathogen_peptides(prm_data)

    prm_not_in_dda = sum([peptide not in dda_path for peptide in prm_path])

    print('DDA % pathogen: ' + str(dda_percent))
    print('PRM % pathogen: ' + str(prm_percent))

    print('DDA number pathogen: ' + str(len(dda_path)))
    print('PRM number pathogen: ' + str(len(prm_path)))

    print('PRM unique pathogen: ' + str(prm_not_in_dda))


