import argparse
import numpy as np
import pandas as pd

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
    parser.add_argument('-i', help = 'unpaired peaks file input', required = True)
    parser.add_argument('-o', help = 'filtered peak output path', required = True)
    args = parser.parse_args()

    peaks = pd.read_csv(args.i)

    enough_intensity = peaks['intensity'] >= min_intensity
    after_loading = peaks['rt'] > min_rt
    before_washout = peaks['rt'] < max_rt
    inf_snr_threshold = peaks['snr_inf'] >= min_inf_snr
    mock_snr_threshold = peaks['snr_mock'] < max_mock_snr


    passes_filters = np.all(np.array([enough_intensity, after_loading, before_washout, inf_snr_threshold, mock_snr_threshold]), axis =0)
    filtered_peaks = peaks.iloc[passes_filters]

    filtered_peaks.to_csv(args.o, index = False)