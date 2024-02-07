import pandas as pd
import argparse
from numpy import logical_and

mz_tol_ppm = 10.
mz_tol = mz_tol_ppm/1e6

def has_match(psm_data, peak):
    in_rt_range = logical_and(psm_data['RT in min']*60. >= peak['rt1'], psm_data['RT in min']*60. <= peak['rt2'])
    in_mz_range = logical_and(psm_data['mz in Da']*(1 + mz_tol) >= peak['mz'], psm_data['mz in Da']*(1. - mz_tol) <= peak['mz'])
    match = logical_and(in_rt_range, in_mz_range)
    return any(match)

def match_psms(psm_file, unmatched_peaks_file, outfile):
    if psm_file.split('.')[-1] == 'txt': #if raw tsv file (unfiltered PSMs, e.g.)
        psm_data = pd.read_csv(psm_file, delim_whitespace = True)
    elif psm_file.split('.')[-1] == 'csv': #if csv file (filtered PSMs, e.g.)
        psm_data = pd.read_csv(psm_file)

    peaks_data = pd.read_csv(unmatched_peaks_file)

    peaks_data['matching_psm'] = [has_match(psm_data, peak) for _, peak in peaks_data.iterrows()]
    peaks_data.to_csv(outfile)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', help = 'input psm file', required = True)
    parser.add_argument('-u', help = 'unmatched peaks file', required = True)
    parser.add_argument('-o', help = 'output path', required = True)

    args = parser.parse_args()
    match_psms(args.p, args.u, args.o)
    