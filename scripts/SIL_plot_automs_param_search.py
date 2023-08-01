from matplotlib import pyplot as plt
import pandas as pd
import argparse
from numpy import logical_and, logical_or, logical_not

lengths = [10, 20, 40, 60, 100]
ppms = [10, 20, 40]

def has_matches(mz, mz_list, tolerance):#returns True if mz matches any m/z value in mz_list within tolerance 
    match_list = ((mz_list - mz).abs() < mz*tolerance).any()
    return match_list

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', help = 'input csv (autoMS parameter search results)', required = True)
    parser.add_argument('-l', help = 'list of expected targets', required = True)
    parser.add_argument('-o', help = 'figure output path/prefix', required = True)
    parser.add_argument('-t', help = 'mass tolerance (ppm)', required = False, default = 10)

    args = parser.parse_args()

    data = pd.read_csv(args.i)
    targets_list = pd.read_csv(args.l)

    mass_tol_proportion = float(args.t)/1e6


    target = [has_matches(mz, targets_list['m/z'], tolerance = mass_tol_proportion) for mz in data['mz']]
    non_target = logical_not(target)


    for ppm in ppms:
        for length in lengths:
            scores = data['score_len' + str(length) + '_' + str(ppm) + 'ppm']
            snrs = data['snr_len' + str(length) + '_' + str(ppm) + 'ppm']
            plt.figure()
            for predicate, color in zip([non_target, target], ['gray', 'green']):
                plt.plot(scores.loc[predicate], snrs.loc[predicate], 'o', color = color, alpha = 0.2)
            plt.xlabel('score')
            plt.ylabel('SNR')
            plt.legend(['Non-target', 'Target'])
            plt.xlim([-0.25, 4.])
            plt.ylim([-1., 18.])
            plt.savefig(args.o + '_len' + str(length) + '_' + str(ppm) + 'ppm.jpeg')
            plt.figure()
            for predicate, name in zip([non_target, target], ['non_target', 'target']):
                score_filtered = scores.loc[predicate]
                snr_filtered = snrs.loc[predicate]
                not_na = logical_and(logical_not(score_filtered.isna()), logical_not(snr_filtered.isna()))

                plt.hist2d(score_filtered[not_na], snr_filtered[not_na], bins = 40, range = [[0., 4.], [0., 20.]])
                plt.xlabel('score')
                plt.ylabel('SNR')
                plt.savefig(args.o + '_len' + str(length) + '_' + str(ppm) + 'ppm_hist_' + name + '.jpeg', range = [[0., 4.], [0., 20.]])
