import pandas as pd
import argparse
from numpy import logical_and, logical_not

import numpy as np

mz_tol_ppm = 10.
mz_tol = mz_tol_ppm/1e6

def get_mz_match(psm_data, peak):
    in_mz_range = (psm_data['mz in Da'] - peak['mz']).abs() <= peak['mz']*mz_tol #logical_and(psm_data['mz in Da']*(1 + mz_tol) >= peak['mz'], psm_data['mz in Da']*(1. - mz_tol) <= peak['mz'])
    matches = psm_data.loc[in_mz_range]
    if not matches.empty:
        closest_rt_match = np.argmin(np.abs(matches['RT in min'] - (peak['rt']/60.)))
        return matches.iloc[closest_rt_match]
    else:
        return pd.Series({key : pd.NA for key in matches.columns})


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', help = 'input psm file', required = True)
    parser.add_argument('-u', help = 'unmatched peaks file', required = True)
    parser.add_argument('-o', help = 'output path', required = True)

    args = parser.parse_args()

    if args.p.split('.')[-1] == 'txt': #if raw tsv file (unfiltered PSMs, e.g.)
        psm_data = pd.read_csv(args.p, delim_whitespace = True)
    elif args.p.split('.')[-1] == 'csv': #if csv file (filtered PSMs, e.g.)
        psm_data = pd.read_csv(args.p)

    peaks_data = pd.read_csv(args.u)
    peaks_data[psm_data.columns] = pd.NA
    
    for i, peak in peaks_data.iterrows():
        peaks_data.loc[i, psm_data.columns] = get_mz_match(psm_data, peak)
    print(sum(logical_not(peaks_data['Annotated Sequence'].isna())))
    peaks_data.to_csv(args.o)
    