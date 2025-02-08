import pyopenms as oms
import pandas as pd
import argparse
from matplotlib import pyplot as plt
import numpy as np
from os.path import join
from tqdm import tqdm


#plot XIC for infected and control sample for a given peptide
def plot_XIC(inf_data, ctrl_data, mz, output_dir):
    t_inf, i_inf = zip(*inf_data)
    t_ctrl, i_ctrl = zip(*ctrl_data)

    i_max = np.max(i_inf + i_ctrl)
    f, ax = plt.subplots(1, 2, figsize = (5, 10))

    
    ax[0].plot(t_inf, i_inf)
    ax[0].set_xlabel('RT (min)')
    ax[0].set_ylabel('intensity')
    ax[0].set_ylim([0, i_max])
    
    ax[1].plot(t_ctrl, i_ctrl)
    ax[1].set_xlabel('RT (min)')
    ax[1].set_ylabel('intensity')
    ax[1].set_ylim([0, i_max])
    f.savefig(join(output_dir, str(mz) + '.pdf'))

#get and plot paired XICs for a set of peaks
def get_XICs(inf_mzml, ctrl_mzml, output_dir, peaks : pd.DataFrame, ppm = 10., time_window = 2.5):
    if 'RT Time (min)' in peaks.columns:
        rt_field = 'RT Time (min)'
    elif 'rt' in peaks.columns:
        rt_field = 'rt'
        time_window = time_window*60. #in the automs format, rt is measured in seconds, not minutes
    else:
        raise ValueError('RT column not found')
    
    if 'm/z' in peaks.columns:
        mz_field = 'm/z'
    elif 'mz' in peaks.columns:
        mz_field = 'mz'
    else:
        raise ValueError('m/z column not found')

    inf_traces = [[] for _ in range(len(peaks))]

    inf_run = oms.MSExperiment()
    oms.MzMLFile().load(inf_mzml, inf_run)

    for spectrum in inf_run:
        rt = spectrum.getRT()
        for i, peak in peaks.iterrows():
            if (rt <= peak[rt_field] + time_window) and (rt >= peak[rt_field] - time_window):
                tolerance = peak[mz_field]*(ppm/1e6)
                index = spectrum.findHighestInWindow(peak[mz_field], tolerance, tolerance)
                if index == -1:
                    intensity = 0.
                else:
                    intensity = spectrum[index].getIntensity()
                inf_traces[i].append((rt, intensity))
    
    ctrl_traces = [[] for _ in range(len(peaks))]

    ctrl_run = oms.MSExperiment()
    oms.MzMLFile().load(ctrl_mzml, ctrl_run)

    for spectrum in ctrl_run:
        rt = spectrum.getRT()
        for i, peak in peaks.iterrows():
            if (rt <= peak[rt_field] + time_window) and (rt >= peak[rt_field] - time_window):
                tolerance = peak[mz_field]*(ppm/1e6)
                index = spectrum.findHighestInWindow(peak[mz_field], tolerance, tolerance)
                if index == -1:
                    intensity = 0.
                else:
                    intensity = spectrum[index].getIntensity()
                ctrl_traces[i].append((rt, intensity))
    for i in range(len(peaks)):
        plot_XIC(inf_traces[i], ctrl_traces[i], peaks[mz_field][i], output_dir)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', help = 'psm file', required = True)
    parser.add_argument('-i', help = 'infected mzML file', required = True)
    parser.add_argument('-c', help = 'control mzML file', required = True)
    parser.add_argument('-o', help = 'output directory', required = True)
    parser.add_argument('-w', help = 'time window', required = False, default = 2.5, type = float)

    args = parser.parse_args()

    peaks_data = pd.read_csv(args.p)
    get_XICs(args.i, args.c, args.o, peaks_data, time_window=args.w)



