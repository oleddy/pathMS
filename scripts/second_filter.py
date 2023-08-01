import pandas as pd
import argparse
from numpy import logical_and

def has_matches(row, list, mz_tol, rt_tol):
    mz_tol_frac = float(mz_tol)/1e6
    mz_match = (list['mz'] - row['mz']).abs() <= mz_tol_frac*row['mz']
    rt_match = (list['rtApex'] - row['rtApex']).abs() <= rt_tol
    charge_match = list['charge'] == row['charge']
    return any(mz_match & rt_match & charge_match)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', help = 'unpaired peak list', required = True)
    parser.add_argument('-m', help = 'mock peak list', required = True)
    parser.add_argument('-t', help = 'mass tolerance (ppm)', required = False, default = 10)
    parser.add_argument('-r', help = 'retention time tolerance', required = False, default = 1.)
    parser.add_argument('-o', help = 'output file path', required = True)

    args = parser.parse_args()

    unpaired = pd.read_csv(args.u)
    mock = pd.read_csv(args.m, delim_whitespace=True)
    
    unpaired_filter = [not has_matches(row, mock, float(args.t), float(args.r)) for _, row in unpaired.iterrows()]
    filtered_peaks = unpaired.loc[unpaired_filter]
    filtered_peaks.to_csv(args.o)
