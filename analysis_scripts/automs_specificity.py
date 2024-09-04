import pandas as pd
import argparse
from matplotlib import pyplot as plt
import seaborn as sn
import numpy as np

from os.path import join

from SIL_plot_automs_param_search import has_matches

lengths = [10, 20, 40, 60, 100]
ppms = [10, 20, 40]

'''
Measure sensitivity and specificity of AutoMS (at a given set of score threhsold values)
at distinguishing a set of target peaks (known real peptide precursors of interest) from all other peaks, 
as a function of m/z tolerance (ppms) and XIC length (lenghts). 
'''

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', help = 'input csv (automs parameter search results)', required = True)
    parser.add_argument('-o', help = 'output file path', required = True)
    parser.add_argument('-s', help = 'score threshold' ,required = False, default = 0.3)
    parser.add_argument('-n', help = 'snr threshold', required = False, default = 1.)
    parser.add_argument('-t', help = 'target list', required = True)
    parser.add_argument('-m', help = 'mass tolerance (ppm)', required = False, default = 10)
    args = parser.parse_args()

    search_results = pd.read_csv(args.i)
    target_list = pd.read_csv(args.t)

    mass_tol_proportion = float(args.m)/1e6
    search_results['target'] = [has_matches(mz, target_list['m/z'], tolerance = mass_tol_proportion) for mz in search_results['mz']]


    sensitivities = np.zeros((len(lengths), len(ppms)))
    specificities = np.zeros((len(lengths), len(ppms)))

    min_intensity = 2e5

    min_score = float(args.s)
    min_snr = float(args.n)

    for i, length in enumerate(lengths):
        for j, ppm in enumerate(ppms):
            scores = search_results['score_len' + str(length) + '_' + str(ppm) + 'ppm']
            snrs = search_results['snr_len' + str(length) + '_' + str(ppm) + 'ppm']
            passes_thresholds = np.logical_and(np.logical_or(scores >= min_score, snrs >= min_snr), search_results['intensity'] >= min_intensity)
            specificities[i, j] = sum(np.logical_and(passes_thresholds, search_results['target']))/sum(passes_thresholds)
            sensitivities[i, j] = sum(np.logical_and(passes_thresholds, search_results['target']))/sum(search_results['target'])
            
    print(sum(search_results['target']))
    print(len(search_results))
    plt.figure()
    plt.title('AutoMS Sensitivity')
    sn.heatmap(sensitivities)
    plt.xlabel('ppm')
    plt.ylabel('length')
    plt.xticks(ticks = np.array(range(len(ppms))) + 0.5, labels = ppms)
    plt.yticks(ticks = np.array(range(len(lengths))) + 0.5, labels = lengths)
    plt.savefig(join(args.o, 'sensitivity.jpeg'))

    plt.figure()
    plt.title('AutoMS Specificity')
    sn.heatmap(specificities)
    plt.xlabel('ppm')
    plt.ylabel('length')
    plt.xticks(ticks = np.array(range(len(ppms))) + 0.5, labels = ppms)
    plt.yticks(ticks = np.array(range(len(lengths))) + 0.5, labels = lengths)
    plt.savefig(join(args.o, 'specificity.jpeg'))
            
