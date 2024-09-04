import pymzml
import argparse
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt

'''
1. Plot the proportion of precursors that have at least one MS2 scan within a given retention time window, as a function of retention time window size. 
(To assess what proportion of your inclusion list was actually scanned during a PRM run.)
2. Plot the number of MS2 scans per MS1 scan as a function of retention time. 
(To assess whether your PRM run is instrument cycle time limited.)
'''

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', help = 'input inclusion list', required = True)
    parser.add_argument('-m', help = 'input mzml file', required = True)
    parser.add_argument('-t', help = 'mass tolerance (in ppm)', required = False, default = 10)
    parser.add_argument('-f', help = 'figure export directory', required = True)
    parser.add_argument('-o', help = 'data output path', required = True)
    
    args = parser.parse_args()

    mzml_reader = pymzml.run.Reader(args.m)
    inclusion_list = pd.read_csv(args.i)
    inclusion_list['MS2 RT diff'] = 1000. #initialize default value for RT difference between nearest MS2 and target's expected RT

    mz_tol = float(args.t)/1e6

    mzs = [] #we will keep track of each time an MS2 was taken that matched a given m/z and at what RT
    rts = [] 

    ms1_rts = [] #for each MS1, we will keep track of how many MS2s were taken
    ms2_counts = [] 

    current_spectrum_count = 0
    current_rt = 0.

    unmatched_ms2s = 0
    total_ms2s = 0
    for spectrum in mzml_reader:
        if spectrum.ms_level == 1:
            ms1_rts.append(current_rt)
            ms2_counts.append(current_spectrum_count)
            current_rt = spectrum.scan_time_in_minutes()
            current_spectrum_count = 0
        else:
            total_ms2s += 1
            # print(spectrum.ms_level)
            precursors = spectrum.selected_precursors
            # print(precursors)
            precursor_mz = precursors[0]['mz']
            # print(precursor_mz)
            current_rt = spectrum.scan_time_in_minutes()
            mzs.append(precursor_mz)
            rts.append(current_rt)
            current_spectrum_count += 1

            matching_rows = np.array(np.logical_and(((inclusion_list['m/z'] - precursor_mz).abs() % (1./inclusion_list['z'])) < mz_tol*inclusion_list['m/z'], ((inclusion_list['m/z'] - precursor_mz).abs() / (1./inclusion_list['z'])) < 5.)) #find matching targets within mass tolerance
            # matching_rows_1_up = np.array((inclusion_list['mz'] + 1./inclusion_list['z'] - precursor_mz).abs() < mz_tol*inclusion_list['mz'])
            # matching_rows_1_down = np.array((inclusion_list['mz'] - 1./inclusion_list['z'] - precursor_mz).abs() < mz_tol*inclusion_list['mz'])
            # matching_rows = matching_rows | matching_rows_1_down | matching_rows_1_up
            if sum(matching_rows) == 0.:
                unmatched_ms2s += 1
                # print(current_rt)
                # print(precursors)
                # print(spectrum.precursors)
            replace_rows = np.logical_and(matching_rows, ((inclusion_list['RT Time (min)'] - current_rt).abs() < inclusion_list['MS2 RT diff'].abs())) #get rows where new RT is closer to the target RT than the previous best match
            inclusion_list['MS2 RT diff'].loc[replace_rows] = inclusion_list.loc[replace_rows]['RT Time (min)'] - current_rt #update delta for the closest matching RT for each target
            # print('existing RT diff: ' + str(inclusion_list['MS2 RT diff'].loc[matching_rows]))
            # print('new RT diff: ' + str(inclusion_list.loc[matching_rows]['rt']/60. - current_rt))

            
    
    RT_tols = [130., 20., 10., 5., 1., 0.5]
    percent_ms2_coverage = []

    print(inclusion_list['MS2 RT diff'])
    print('MS2s not matched: ' + str(unmatched_ms2s))
    print('total MS2s: ' + str(total_ms2s))
    ms2_data = pd.DataFrame({'mz' : mzs, 'rt' : rts})
    for RT_tol in RT_tols:
        detections = sum(inclusion_list['MS2 RT diff'] < RT_tol)
        percent_ms2_coverage.append(100.*detections/inclusion_list.shape[0])
    print(percent_ms2_coverage)

    plt.figure()
    plt.plot(ms1_rts, ms2_counts)
    plt.xlabel('RT (minutes)')
    plt.ylabel('MS2 scans per MS1 scan')
    plt.savefig(args.f)

    inclusion_list.to_csv(args.o)