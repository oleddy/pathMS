from matplotlib import pyplot as plt
import pandas as pd
import argparse
from os.path import join

#Plots a 2D histogram of quality score and signal/noise ratio (SNR) scores in an AutoMS output file

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', help = 'input csv', required = True)
    parser.add_argument('-o', help = 'figure output path/prefix', required = True)

    args = parser.parse_args()
    automs_scores = pd.read_csv(args.i)
    plt.figure()
    plt.hist2d(automs_scores['score_inf'], automs_scores['snr_inf'], bins = 40, range = [[0., 4.], [0., 20.]])
    plt.xlabel('score')
    plt.ylabel('SNR')
    plt.savefig(join(args.o, 'AutoMS_score_plot.pdf'))