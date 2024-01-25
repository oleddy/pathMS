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

def find_unpaired_peaks(grouping_dir, inf_features_file, outfile, charge_states = [2,3]):
    #get all features obtained from infected sample by Dinosaur
    infected_data = pd.read_csv(inf_features_file, delim_whitespace = True)

    #initially, consider all peaks potentially unmatched. Only consider peaks with charge states we care about. 
    unmatched_peaks = infected_data.loc[infected_data['charge'].isin(charge_states)]

    #deeprtalign potentially outputs multiple files of grouping information, so we need to check each of them
    #on each iteration, more peaks will be matched and eliminated
    #fortunately, get_unmatched is composable with itself, so we can just do this iteratively
    for file in listdir(grouping_dir):

        #get grouping data output by deeprtalign
        group_data = pd.read_csv(join(grouping_dir, file))
        paired_groups = [sum(group == group_data['group']) > 1 for group in group_data['group']] #predicate that identifies rows that are in groups with >1 member. 
        paired_data = group_data.loc[paired_groups]

        #find peaks in the infected sample data that are not part of any grouping (i.e., not paired with any sample in mock data)
        unmatched_peaks = get_unmatched(unmatched_peaks, paired_data, cols = ['mz', 'charge', 'rtApex'])

        print('Completed file ' + file)
        print('Remaining unmatched peaks: ' + str(unmatched_peaks.shape[0]))
    #write output file
    unmatched_peaks.to_csv(outfile)

# charge_states = [2,3]

if __name__ == '__main__':
    #read in command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-g', help = 'grouping information path', required = True)
    parser.add_argument('-i', help = 'infected peaks file', required = True)
    parser.add_argument('-c', help = 'comma-separated list of charge states', required = False, default = '2,3')
    parser.add_argument('-o', help = 'output file path', required = True)
    args = parser.parse_args()
    
    charge_states = [int(charge) for charge in args.c.split(',')]

    find_unpaired_peaks(args.g, args.i, args.o, charge_states = charge_states)
