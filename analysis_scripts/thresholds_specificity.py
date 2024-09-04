import argparse
import pandas as pd
from numpy import logical_and, logical_not, logical_or
import numpy as np
from SIL_plot_automs_param_search import has_matches



min_intensity = 1e4
min_rt = 25.*60.
max_rt = 115.*60.
min_inf_snr = 4.
min_inf_score = 0.3
max_mock_snr = 0.5

#TODO: make this more flexible/less hard-coded – read in filter set from file
#and write a function that parses each line from the filter set file and returns a boolean
#series indicating whether each peak passes that filter
if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', help = 'autoMS scoring output', required = True)
    # parser.add_argument('-c', help = 'mock psm peak matches', required = True)
    parser.add_argument('-t', help = 'intended targets', required = True)


    args = parser.parse_args()

    peaks = pd.read_csv(args.i)
    mass_tol_proportion = 10./1e6
    #import dataframes with column indicating whether a matching psm was found for mock or infected sample
    # mock_matches = pd.read_csv(args.c)
    target_list = pd.read_csv(args.t)

    #add this information to the AutoMS sccoring results 
    # peaks['mock_match'] = mock_matches['matching_psm']
    peaks['target'] = [has_matches(mz, target_list['m/z'], tolerance = mass_tol_proportion) for mz in peaks['mz']]

    enough_intensity = peaks['intensity'] >= min_intensity
    after_loading = peaks['rt'] > min_rt
    before_washout = peaks['rt'] < max_rt
    inf_snr_threshold = logical_or(peaks['snr_inf'] >= min_inf_snr, peaks['score_inf'] >= min_inf_score)
    mock_snr_threshold = peaks['snr_mock'] < max_mock_snr

    print('total targets: ', sum(peaks['target']))

    passes_filters = np.all(np.array([enough_intensity, after_loading, before_washout, inf_snr_threshold, mock_snr_threshold]), axis =0)
    specificity = sum(logical_and(peaks['target'], passes_filters))/sum(passes_filters)
    print('specificity = ', specificity)
    sensitivity = sum(logical_and(peaks['target'], passes_filters))/sum(peaks['target'])
    print('sensitivity = ', sensitivity)
