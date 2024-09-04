import argparse
import os
import pandas as pd
from numpy import abs
from matplotlib import pyplot as plt
from os.path import join

'''
Plot a histogram of the retention time differences between peaks that were matched with one another by
DeepRTalign. -i should be the output folder for DeepRTalign (my_working_directory/mass_align_all_information).
'''

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', help = 'input directory', required = True)
    parser.add_argument('-o', help = 'output figure path', required = True)

    args = parser.parse_args()

    filelist = os.listdir(args.i)

    diffs = []
    for file in filelist:
        data = pd.read_csv(join(args.i, file))
        allgroups = list(set(data['group']))
        for group in allgroups:
            groupdata = data.loc[data['group'] == group]
            if len(groupdata) > 1:
                rt1 = groupdata.iloc[0]['rtApex']
                rt2 = groupdata.iloc[1]['rtApex']
            diffs.append(rt1 - rt2)
    # diffs = abs(diffs)

    plt.figure()
    plt.hist(diffs, bins = 200)
    plt.xlabel('RT offset (minutes)')
    plt.ylabel('Count')
    plt.xlim([-20.,20.])
    plt.savefig(args.o)
