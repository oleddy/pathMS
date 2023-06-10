import argparse
import pandas as pd

# charges = [2, 3] #charges of interest for peptides (i.e., omit peaks that don't have a charge in this range)
threshold_ratio = 0.01 #set intensity threshold for PRM at 1% of previously observed maximum intensity

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', help = 'input unmatched peaks path')
    parser.add_argument('-o', help = 'output file path', required = True)
    args = parser.parse_args()

    peaks_data = pd.read_csv(args.i)

    # charge_peaks = peaks_data.loc[peaks_data['charge'].isin(charges)]

    # charge_peaks = charge_peaks.reset_index(drop = True)

    ms_table = pd.DataFrame()
    
    ms_table['m/z'] = peaks_data['mz']

    ms_table['Intensity Threshold'] = peaks_data['intensityApex']*threshold_ratio

    #set compound name to "peak_i" where i is the index of each peak
    ms_table['Compound'] = ['peak_' + str(i) for i in range(ms_table.shape[0])]

    ms_table.to_csv(args.o)