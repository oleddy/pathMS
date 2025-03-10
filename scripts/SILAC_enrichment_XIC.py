import argparse
import pandas as pd
from xic import get_XICs
import os

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', help = 'psm-matched inclusion list', required = True)
    # parser.add_argument('-a', help = 'all psms', required = True)
    parser.add_argument('-q', help = 'percolator q-value threshold', required = False, default = 0.05, type = float)
    parser.add_argument('-o', help = 'xic output directory', required = True)
    parser.add_argument('-d', help = 'disease condition mzml file', required = True)
    parser.add_argument('-c', help = 'control mzml file', required = True)
    args = parser.parse_args()

    # psm_file = args.a
    # if psm_file.split('.')[-1] == 'txt': #if raw tsv file (unfiltered PSMs, e.g.)
    #     all_data = pd.read_csv(psm_file, delim_whitespace = True)
    # elif psm_file.split('.')[-1] == 'csv': #if csv file (filtered PSMs, e.g.)
    #     all_data = pd.read_csv(psm_file)
    
    # all_data = all_data.loc[all_data['Percolator q-Value'] <= args.q]
    # all_data = all_data.drop_duplicates(subset = ['Annotated Sequence'])
    # all_data['Modifications'] = all_data['Modifications'].fillna('')
    
    # all_labeled_frac = sum(all_data['Modifications'].str.contains('Label'))/len(all_data)

    all_data = pd.read_csv(args.i)
    matched_data = all_data.dropna(subset = ['Annotated Sequence'])
    matched_data = matched_data.drop_duplicates(subset = ['Annotated Sequence'])
    matched_data['Modifications'] = matched_data['Modifications'].fillna('')

    matched_labeled = matched_data[matched_data['Modifications'].str.contains('Label')].reset_index()
    matched_unlabeled = matched_data[~matched_data['Modifications'].str.contains('Label')].reset_index()
    inclusion_list_random_selection = all_data.sample(n = 100)[['m/z', 'RT Time (min)']].reset_index()

    if not os.path.isdir(os.path.join(args.o, 'matched_labeled')):
        os.mkdir(os.path.join(args.o, 'matched_labeled'))
    if not os.path.isdir(os.path.join(args.o, 'matched_unlabeled')):
        os.mkdir(os.path.join(args.o, 'matched_unlabeled'))
    if not os.path.isdir(os.path.join(args.o, 'unmatched')):
        os.mkdir(os.path.join(args.o, 'unmatched'))

    get_XICs(args.d, args.c, os.path.join(args.o, 'matched_labeled'), matched_labeled)
    get_XICs(args.d, args.c, os.path.join(args.o, 'matched_unlabeled'), matched_unlabeled)
    get_XICs(args.d, args.c, os.path.join(args.o, 'unmatched'), inclusion_list_random_selection)
    
    # selected_labeled_frac = sum(matched_data['Modifications'].str.contains('Label'))/len(matched_data)

    # fold_enrichment = selected_labeled_frac/all_labeled_frac

    # print('All peptides percent labeled: ' + str(all_labeled_frac*100.))
    # print('Selected precursors percent labeled: ' + str(selected_labeled_frac*100.))
    # print('Fold enrichment: ' + str(fold_enrichment))

