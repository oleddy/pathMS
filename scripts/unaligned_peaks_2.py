import pandas as pd
import os
import argparse
from multiprocessing import Pool, cpu_count

charges = [2,3]

def find_unaligned_peaks(file):
    data = pd.read_csv(file)
    groups = list(set(data['group']))
    unique_peaks = pd.DataFrame(columns = data.columns)
    for group in groups:
        group_data = data.loc[data['group'] == group]
        if ('A2' not in list(group_data['sample'])) and (group_data.iloc[0]['charge'] in charges): #infected sample will be A1, mock is A2
            unique_peaks = pd.concat([unique_peaks, group_data])
    return unique_peaks

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', help = 'input directory (alignment files location)', required = True)
    parser.add_argument('-o', help = 'output path', required = True)
    
    args = parser.parse_args()

    files = os.listdir(args.i)
    files = [os.path.join(args.i, file) for file in files]
    with Pool(processes = cpu_count() - 1) as p:
        results = p.map(find_unaligned_peaks, files)
    results = pd.concat(results)
    results.to_csv(args.o)