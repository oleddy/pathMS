import argparse
import numpy as np
import pandas as pd
from numpy import logical_and, logical_not, logical_or


def make_inclusion_list(automs_score_file, inf_psm_matches_file, outfile, min_intensity = 1e4, min_score = 0.3, min_snr = 1.5, min_rt = 25.*60, max_rt = 115.*60., window = 3.):
    peaks = pd.read_csv(automs_score_file)

    #import dataframes with column indicating whether a matching psm was found for mock or infected sample
    inf_matches = pd.read_csv(inf_psm_matches_file)

    #add this information to the AutoMS sccoring results 
    peaks['mtb_match'] = inf_matches['matching_psm']

    enough_intensity = peaks['intensity'] >= min_intensity
    after_loading = peaks['rt'] > min_rt
    before_washout = peaks['rt'] < max_rt
    inf_snr_threshold = logical_or(peaks['snr_inf'] >= min_snr, peaks['score_inf'] >= min_score)
    # mock_snr_threshold = peaks['snr_mock'] < max_mock_snr
    no_psm_match = logical_not(peaks['mtb_match'])


    passes_filters = np.all(np.array([enough_intensity, after_loading, before_washout, inf_snr_threshold, no_psm_match]), axis =0)
    filtered_peaks = peaks.iloc[passes_filters]

    inclusion_list = pd.DataFrame()
    inclusion_list['Compound'] = filtered_peaks['mz']
    inclusion_list['Formula'] = ['' for _ in range(filtered_peaks.shape[0])]
    inclusion_list['Adduct'] = ['' for _ in range(filtered_peaks.shape[0])]
    inclusion_list['m/z'] = filtered_peaks['mz']
    inclusion_list['z'] = filtered_peaks['z']
    inclusion_list['RT Time (min)'] = filtered_peaks['rt']/60.
    inclusion_list['Window (min)'] = window

    inclusion_list.to_csv(outfile, index = False)

#TODO: make this more flexible/less hard-coded – read in filter set from file
#and write a function that parses each line from the filter set file and returns a boolean
#series indicating whether each peak passes that filter
if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', help = 'autoMS scoring output', required = True)
    # parser.add_argument('-c', help = 'mock psm peak matches', required = True)
    parser.add_argument('-m', help = 'infected psm peak matches', required = True)
    parser.add_argument('-o', help = 'inclusion list output path', required = True)
    
    parser.add_argument('--min_intensity', help = 'minimum peak intensity threshold', type = float, required = False, default = 1e4)
    parser.add_argument('--min_score', help = 'AutoMS score threshold', required = False, type = float, default = 0.3)
    parser.add_argument('--min_snr', help = 'AutoMS signal/noise ratio threshold', required = False, type = float, default = 1.5)
    parser.add_argument('--min_rt', help = 'minimum retention time (exclude peaks before) in seconds', required = False, default = 25.*60., type = float)
    parser.add_argument('--max_rt', help = 'maximum retention time (exclude peaks after) in seconds', required = False, default = 115.*60., type = float)
    parser.add_argument('--window', help = 'retention time window width for inclusion list scheduling (in minutes)', required = False, default = 3., type = float)

    args = parser.parse_args()

    make_inclusion_list(args.i, args.m,args.o,
                        min_intensity = args.min_intensity,
                        min_score = args.min_score,
                        min_snr = args.min_snr,
                        min_rt = args.min_rt,
                        max_rt = args.max_rt,
                        window = args.window
                        )
    