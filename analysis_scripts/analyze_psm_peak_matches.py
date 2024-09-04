from matplotlib import pyplot as plt
from numpy import logical_not, logical_and
import pandas as pd
import argparse

#checks whether any m/z values in mz_list match "mz" to within tolerance "tol" (in ppm)
def any_match_within_tol(mz, mz_list, tol):
    return any((mz_list - mz).abs() < mz*tol/1e6)

def plot_RT_correlation(peaks_data, inclusion_list, output_path):
    prm_targets = peaks_data.loc[[any_match_within_tol(mz, inclusion_list['m/z'], 10) for mz in peaks_data['mz']]]
    print(prm_targets.shape[0])

    peaks_with_match = prm_targets.loc[logical_not(prm_targets['Annotated Sequence'].isna())] #find peaks that have matching PSMs

    RT_tols = [20., 10., 5., 1., 0.5]
    
    peaks_sorted_by_closest = peaks_with_match.loc[(peaks_with_match['RT in min'] - peaks_with_match['rt']/60.).abs().sort_values().index] #sort so that all the peaks with lower distance between target RT and PSM RT are first
    deduplicated_peaks = peaks_sorted_by_closest.drop_duplicates(subset = ['Annotated Sequence'])  #drop duplicates by PSM data – ensures that for any given PSM, there will only be one peak. Sorting in prev line ensures it will be the one that is the closest match in terms of RT
   
   
    #find percentage of targets that have a PSM at any point
    print('Percentage of targets with PSM: ' + str(100.*deduplicated_peaks.shape[0]/inclusion_list.shape[0]))

    try:
        matched_self = deduplicated_peaks.loc[logical_not(deduplicated_peaks['TB-derived'])] #separate bacterial and self peaks
        matched_bac = deduplicated_peaks.loc[deduplicated_peaks['TB-derived']]
    except KeyError:
        deduplicated_peaks['TB-derived'] = [accession_string[0] == '0' for accession_string in deduplicated_peaks['Protein Accessions']] #infer whether peptide is bacterial from the accession number(s) – will begin with 0 for bacterial, 1 for self
        matched_self = deduplicated_peaks.loc[logical_not(deduplicated_peaks['TB-derived'])] #separate bacterial and self peaks
        matched_bac = deduplicated_peaks.loc[deduplicated_peaks['TB-derived']]

    print(matched_self.shape[0])
    print(matched_bac.shape[0])
    print(deduplicated_peaks.shape[0])
    bac_percents = []
    bac_totals = []
    percents_overall = []
    
    for RT_tol in RT_tols:
        n_bac_in_tol = sum((matched_bac['RT in min'] - matched_bac['rt']/60.).abs() < RT_tol)
        n_self_in_tol = sum((matched_self['RT in min'] - matched_self['rt']/60.).abs() < RT_tol)
        
        bac_percents.append(100.*n_bac_in_tol/(n_bac_in_tol + n_self_in_tol))
        bac_totals.append(n_bac_in_tol)
        percents_overall.append(100.*(n_bac_in_tol + n_self_in_tol)/inclusion_list.shape[0])

    print(bac_percents)
    print(bac_totals)
    print(percents_overall)
    

    plt.figure()
    plt.plot(matched_self['RT in min'], matched_self['rt']/60., 'o', color = 'gray', alpha = 0.2) #plot self peaks in gray
    plt.plot(matched_bac['RT in min'], matched_bac['rt']/60., 'o', color = 'green', alpha = 0.2) #plot bacterial peaks in green
    plt.plot([0, max(matched_self['RT in min'])], [0, max(matched_self['RT in min'])], 'k--')   #plot dotted y = x line 
    plt.xlabel('PSM RT')
    plt.ylabel('Target RT')
    plt.legend(['Self peptide', 'Bacterial peptide'])
    plt.savefig(output_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', help = 'inclusion list', required = True)
    parser.add_argument('-p', help = 'input peak/psm match file', required = True)
    parser.add_argument('-f', help = 'figure output path', required = True)

    args = parser.parse_args()

    inclusion_list = pd.read_csv(args.i)
    peaks_data = pd.read_csv(args.p)

    plot_RT_correlation(peaks_data, inclusion_list, args.f)