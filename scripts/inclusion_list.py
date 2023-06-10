import argparse
import numpy as np
import pandas as pd
from numpy import logical_and, logical_not

min_intensity = 5e5
min_rt = 25.*60.
max_rt = 90.*60.
min_inf_snr = 4.
max_mock_snr = 2.

#TODO: make this more flexible/less hard-coded – read in filter set from file
#and write a function that parses each line from the filter set file and returns a boolean
#series indicating whether each peak passes that filter
if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', help = 'autoMS scoring output', required = True)
    parser.add_argument('-c', help = 'mock psm peak matches', required = True)
    parser.add_argument('-m', help = 'infected psm peak matches', required = True)
    parser.add_argument('-o', help = 'inclusion list output path', required = True)


    args = parser.parse_args()

    peaks = pd.read_csv(args.i)

    #import dataframes with column indicating whether a matching psm was found for mock or infected sample
    mock_matches = pd.read_csv(args.c)
    inf_matches = pd.read_csv(args.m)

    #add this information to the AutoMS sccoring results 
    peaks['mock_match'] = mock_matches['matching_psm']
    peaks['mtb_match'] = inf_matches['matching_psm']

    enough_intensity = peaks['intensity'] >= min_intensity
    after_loading = peaks['rt'] > min_rt
    before_washout = peaks['rt'] < max_rt
    inf_snr_threshold = peaks['snr_inf'] >= min_inf_snr
    mock_snr_threshold = peaks['snr_mock'] < max_mock_snr
    no_psm_match = logical_and(logical_not(peaks['mtb_match']), logical_not(peaks['mock_match']))


    passes_filters = np.all(np.array([enough_intensity, after_loading, before_washout, inf_snr_threshold, mock_snr_threshold, no_psm_match]), axis =0)
    filtered_peaks = peaks.iloc[passes_filters]

    inclusion_list = pd.DataFrame()
    inclusion_list['Compound'] = filtered_peaks['mz']
    inclusion_list['Formula'] = ['' for _ in range(filtered_peaks.shape[0])]
    inclusion_list['Adduct'] = ['' for _ in range(filtered_peaks.shape[0])]
    inclusion_list['m/z'] = filtered_peaks['mz']
    inclusion_list['z'] = filtered_peaks['z']

    inclusion_list.to_csv(args.o, index = False)