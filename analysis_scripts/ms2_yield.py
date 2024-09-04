import argparse
import pandas as pd
import pymzml
from numpy import logical_not
from matplotlib import pyplot as plt
import numpy as np

'''
Plot a histogram of integrated precursor ion intensity for:
1. All precursors that got an MS2 scan in a PRM run
2. Precursors that got an MS2 scan but no ID (PSM that passed filters)
3. Precursors that were identified as a self peptide
4. Precursors that were identified as a bacterial/pathogen peptide

Useful for setting minimum intensity thresholds. 
'''

def get_ms2s_and_intensities(peak_list, rt_tolerance, run, mz_tol_ppm = 10):
    output_list = peak_list.copy()
    mz_tol = mz_tol_ppm/1e6
    output_list['precursor intensity'] = 0.
    for spectrum in run:
        if spectrum.ms_level == 2:
            precursors = spectrum.selected_precursors
            precursor_mz = precursors[0]['mz']
            precursor_intensity = precursors[0]['i']
            
            match_or_isotope = ((peak_list['mz'] - precursor_mz).abs() % (1./peak_list['z'])) < mz_tol*peak_list['mz'] #check that m/z either matches within tolerance or the difference is within tolerance of a multiple of 1/z (i.e., is an isotope)
            within_envelope = ((peak_list['mz'] - precursor_mz).abs() / (1./peak_list['z'])) <= 3. #check that this multiple of 1/z is not very large (i.e., is actually in isotope envelope, not another random spurious match elsewhere in the spectrum)
            
            matching_mz = np.array(np.logical_and(match_or_isotope, within_envelope)) #find matching targets
            matching_rt = (peak_list['rt']/60. - spectrum.scan_time_in_minutes()) <= rt_tolerance
            matching_charge = peak_list['z'] == precursors[0]['charge']
            matching_rows = np.logical_and(np.logical_and(matching_rt, matching_mz), matching_charge)
            
            output_list.loc[matching_rows, 'precursor intensity'] = precursor_intensity

    return output_list


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', help = 'peak-psm matches', required = True)
    parser.add_argument('-m', help = 'mzml file', required = True)
    parser.add_argument('-t', help = 'RT tolerance', required = False, default = 1.)
    parser.add_argument('-f', help = 'figure save path', required = True)

    args = parser.parse_args()

    peak_psm_matches = pd.read_csv(args.p) #file containing peak information and PSMs matched by m/z
    
    run = pymzml.run.Reader(args.m)
    data = get_ms2s_and_intensities(peak_psm_matches, args.t, run)

    data['has PSM'] = logical_not(data['Annotated Sequence'].isna())
    data['log precursor intensity'] = np.log10(data['precursor intensity'])
    data_with_ms2 = data.loc[data['precursor intensity'] > 0.]
    data_with_ms2 = data_with_ms2.sort_values(by = 'log precursor intensity', ascending = False)
    data_with_ms2['intensity order'] = range(data_with_ms2.shape[0])

    ms2_no_psm = data_with_ms2.loc[data_with_ms2['Annotated Sequence'].isna()]
    ms2_with_psm = data_with_ms2.loc[logical_not(data_with_ms2['Annotated Sequence'].isna())]

    ms2_self_psm = ms2_with_psm.loc[logical_not(ms2_with_psm['TB-derived'])]
    ms2_bac_psm = ms2_with_psm.loc[ms2_with_psm['TB-derived']]

    plt.figure()
    plt.plot(ms2_no_psm['intensity order'], ms2_no_psm['log precursor intensity'], 'o', color = 'gray')
    plt.plot(ms2_self_psm['intensity order'], ms2_self_psm['log precursor intensity'], 'o', color = 'yellow')
    plt.plot(ms2_bac_psm['intensity order'], ms2_bac_psm['log precursor intensity'], 'o', color = 'green')
    plt.ylim([min(data_with_ms2['log precursor intensity']), max(data_with_ms2['log precursor intensity'])])
    plt.ylabel('log(precursor intensity)')
    plt.xlabel('rank')
    plt.legend(['MS2, no PSM', 'Self PSM', 'Bacterial PSM'])
    plt.savefig(args.f)


