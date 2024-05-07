import pandas as pd
import argparse
from numpy import logical_and

mz_tol_ppm = 10.
mz_tol = mz_tol_ppm/1e6
rt_tol = 1.5

def get_match(psm_data, peak):
    in_rt_range = logical_and(psm_data['retentionTimeMin'] >= (peak['RT Time (min)'] - rt_tol), psm_data['retentionTimeMin'] <= (peak['RT Time (min)'] + rt_tol))
    in_mz_range = logical_and(psm_data['parent_m_over_z']*(1 + mz_tol) >= peak['m/z'], psm_data['parent_m_over_z']*(1. - mz_tol) <= peak['m/z'])
    matches = psm_data.loc[logical_and(in_rt_range, in_mz_range)]
    if not matches.empty:
        return matches.iloc[0]
    else:
        return pd.Series({key : pd.NA for key in matches.columns})

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', help = 'input psm file', required = True)
    parser.add_argument('-u', help = 'unmatched peaks file', required = True)
    parser.add_argument('-o', help = 'output path', required = True)

    args = parser.parse_args()

    extension = args.p.split('.')[-1]

    if extension == 'txt': #if raw tsv file (unfiltered PSMs, e.g.)
        psm_data = pd.read_csv(args.p, delim_whitespace = True)
    elif extension == 'csv': #if csv file (filtered PSMs, e.g.)
        psm_data = pd.read_csv(args.p)
    elif extension == 'ssv': #if ssv file
        psm_data = pd.read_csv(args.p, sep = ';')
    

    peaks_data = pd.read_csv(args.u)
    peaks_data[psm_data.columns] = pd.NA
    
    for i, peak in peaks_data.iterrows():
        peaks_data.loc[i, psm_data.columns] = get_match(psm_data, peak)

    peaks_data.to_csv(args.o)
    