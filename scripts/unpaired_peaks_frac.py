import argparse
import pandas as pd
import numpy as np
from os import listdir
from os.path import join

#function that returns rows of df1 that do not match any row in df2 at all specified columns cols
def get_unmatched(df1, df2, cols):

    has_matches = [any((df2[cols] == row[cols]).all(axis = 1)) for _, row in df1.iterrows()]
    unmatched = df1.iloc[np.logical_not(has_matches)]
    
    return unmatched

charge_states = [2,3]
mock_samples = ['A4', 'A5', 'A6']

if __name__ == '__main__':
    #read in command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-g', help = 'grouping information path', required = True)
    parser.add_argument('-i', help = 'infected peaks file', required = True)
    parser.add_argument('-o', help = 'output file path', required = True)
    args = parser.parse_args()
    
    #get all features obtained from infected sample by Dinosaur
    infected_data = pd.read_csv(args.i, delim_whitespace = True)

    #initially, consider all peaks potentially unmatched. Only consider peaks with charge states we care about. 
    unmatched_peaks = infected_data.loc[infected_data['charge'].isin(charge_states)]

    #deeprtalign potentially outputs multiple files of grouping information, so we need to check each of them
    #on each iteration, more peaks will be matched and eliminated
    #fortunately, get_unmatched is composable with itself, so we can just do this iteratively
    files = [file for file in listdir(args.g) if file[0] != '.']
    
    for file in files:
        print('Started file ' + file)
        #get grouping data output by deeprtalign
        group_data = pd.read_csv(join(args.g, file))
        mock_filter = []
        for group in group_data['group']:
            group_subset = group_data.loc[group_data['group'] == group] #get the rows that are in the current group
            contains_mock = any([group_subset['sample'].str.contains(mock_sample).any() for mock_sample in mock_samples]) #check if the group contains any control samples
            mock_filter.append(contains_mock)

        #apply predicate that identifies rows that are in groups that contain at least one mock-infected fraction. 
        paired_data = group_data.loc[mock_filter]

        #find peaks in the infected sample data that are not part of any grouping (i.e., not paired with any sample in mock data)
        unmatched_peaks = get_unmatched(unmatched_peaks, paired_data, cols = ['mz', 'charge', 'rtApex'])

        print('Completed file ' + file)
        print('Remaining unmatched peaks: ' + str(unmatched_peaks.shape[0]))
    #write output file
    unmatched_peaks.to_csv(args.o)
