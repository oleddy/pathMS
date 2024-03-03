import argparse
import numpy as np
import pandas as pd
from numpy import logical_and, logical_not, logical_or

#TODO: make this more flexible/less hard-coded – read in filter set from file
#and write a function that parses each line from the filter set file and returns a boolean
#series indicating whether each peak passes that filter
if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', help = 'Minora peak input file path', required = True)
    parser.add_argument('-o', help = 'inclusion list output path', required = True)


    args = parser.parse_args()

    peaks = pd.read_csv(args.i, delim_whitespace=True)
    filtered_peaks = peaks.loc[(peaks['Charge'] >= 2) & (peaks['Charge'] < 4)]

    inclusion_list = pd.DataFrame()
    inclusion_list['Compound'] = filtered_peaks['Avg mz in Da']
    inclusion_list['Formula'] = ['' for _ in range(filtered_peaks.shape[0])]
    inclusion_list['Adduct'] = ['' for _ in range(filtered_peaks.shape[0])]
    inclusion_list['m/z'] = filtered_peaks['Avg mz in Da']
    inclusion_list['z'] = filtered_peaks['Charge']
    inclusion_list['RT Time (min)'] = filtered_peaks['Avg Apex RT in min']
    inclusion_list['Window (min)'] = 3.

    inclusion_list.to_csv(args.o, index = False)