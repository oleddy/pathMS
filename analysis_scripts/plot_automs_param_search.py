from matplotlib import pyplot as plt
import pandas as pd
import argparse
from numpy import logical_and, logical_or, logical_not

lengths = [10, 20, 40, 60, 100]
ppms = [10, 20, 40]

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', help = 'input csv', required = True)
    parser.add_argument('-p', help = 'peak-psm pairs', required = True)
    parser.add_argument('-o', help = 'figure output path/prefix', required = True)
    parser.add_argument('-t', help = 'retention time tolerance', required = False, default = 0.5)

    args = parser.parse_args()

    automs_scores = pd.read_csv(args.i)
    peak_psm_pairs = pd.read_csv(args.p)

    data = pd.merge(automs_scores, peak_psm_pairs, on = ['mz', 'rt'], how = 'inner')
    no_psm = logical_or(data['Annotated Sequence'].isna(), (data['RT in min'] - data['rt']) > args.t)
    self_psm = logical_and(data['TB-derived'] == False, (data['RT in min'] - data['rt']) < args.t)
    bac_psm = logical_and(data['TB-derived'] == True, (data['RT in min'] - data['rt']) < args.t)

    print(data.columns)

    for ppm in ppms:
        for length in lengths:
            scores = data['score_len' + str(length) + '_' + str(ppm) + 'ppm']
            snrs = data['snr_len' + str(length) + '_' + str(ppm) + 'ppm']
            plt.figure()
            for predicate, color in zip([no_psm, self_psm, bac_psm], ['gray', 'yellow', 'green']):
                plt.plot(scores.loc[predicate], snrs.loc[predicate], 'o', color = color, alpha = 0.2)
            plt.xlabel('score')
            plt.ylabel('SNR')
            plt.legend(['No PSM', 'Self PSM', 'Bacterial PSM'])
            plt.xlim([-0.25, 4.])
            plt.ylim([-1., 18.])
            plt.savefig(args.o + '_len' + str(length) + '_' + str(ppm) + 'ppm.jpeg')
            plt.figure()
            for predicate, name in zip([no_psm, self_psm, bac_psm], ['none', 'self', 'bac']):
                score_filtered = scores.loc[predicate]
                snr_filtered = snrs.loc[predicate]
                not_na = logical_and(logical_not(score_filtered.isna()), logical_not(snr_filtered.isna()))

                plt.hist2d(score_filtered[not_na], snr_filtered[not_na], bins = 40, range = [[0., 4.], [0., 20.]])
                plt.xlabel('score')
                plt.ylabel('SNR')
                plt.savefig(args.o + '_len' + str(length) + '_' + str(ppm) + 'ppm_hist_' + name + '.jpeg', range = [[0., 4.], [0., 20.]])
