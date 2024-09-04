import argparse
from matplotlib import pyplot as plt
import pandas as pd
from numpy import logical_and
from os.path import join

crop_window = 10. #width (in minutes) of window of retention times to plot

'''
Plot XICs (obtained using get_chromatograms.py)
'''

#retrieve XIC for ion and crop it to a specified window around the apex of the putative peak
def get_cropped_xic(peak, chromatogram_data):

    rounded_mz = str(round(peak['mz'], 2))
    #get the xic data for given peak's m/z value
    xic_data = chromatogram_data[[rounded_mz, 'RT']]

    #set upper and lower limits of RT range to plot
    rt_max = peak['rtApex'] + crop_window/2.
    rt_min = peak['rtApex'] - crop_window/2.

    #boolean series indicating whether RT is in range for a given chromatogram timepoint
    rt_in_range = logical_and(xic_data['RT'] <= rt_max, xic_data['RT'] >= rt_min) 

    #crop xic data to specified range
    cropped_xic = xic_data.loc[rt_in_range]

    #rename the intensity column to 'intensity'
    cropped_xic = cropped_xic.rename({rounded_mz : 'intensity'}, axis = 1)

    return cropped_xic



#make side-by-side plots of chromatograms for infected and mock samples for a given peak and save to 
def plot_peak_comparison(peak, inf_chromatogram_data, mock_chromatogram_data, output_dir):
    fig, (ax1, ax2) = plt.subplots(1, 2, sharey = True)

    inf_xic = get_cropped_xic(peak, inf_chromatogram_data)
    mock_xic = get_cropped_xic(peak, mock_chromatogram_data)

    overall_max = max(list(mock_xic['intensity']) + list(inf_xic['intensity']))

    ax1.set_ylim(0., overall_max)
    ax2.set_ylim(0., overall_max)

    ax1.plot(mock_xic['RT'], mock_xic['intensity'])
    ax2.plot(inf_xic['RT'], inf_xic['intensity'])

    ax1.set_title('Mock')
    ax2.set_title('Infected')

    plt.xlabel('RT (min)')
    plt.ylabel('Intensity')

    plt.savefig(join(output_dir, str(peak['mz']) + '_xic.jpeg'))
    print('plotted ' + str(peak['mz']))


if __name__ == '__main__':
    #read in commmand line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', help = 'input file of peaks to plot (in Dinosaur output format)', required = True)
    parser.add_argument('-i', help = 'infected chromatogram file', required = True)
    parser.add_argument('-c', help = 'control chromatogram file', required = True)
    parser.add_argument('-o', help = 'output directory', required = True)

    args = parser.parse_args()

    peaks = pd.read_csv(args.p)

    inf_chromatogram_data = pd.read_csv(args.i)
    mock_chromatogram_data = pd.read_csv(args.c)

    for _, peak in peaks.iterrows():
        if str(round(peak['mz'], 2)) in inf_chromatogram_data.columns:
            plot_peak_comparison(peak, inf_chromatogram_data, mock_chromatogram_data, args.o)


