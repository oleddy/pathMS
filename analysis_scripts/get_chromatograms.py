import argparse
import pymzml
import pandas as pd
from numpy import zeros
from os.path import join

#retrieve extracted ion chromatogram (XIC) for a given set of m/z values from a pymzml reader object
def xic(mzml_reader, mzs):
    #round mz values to get coarse-grained bins we can easily add chromatographic peaks into
    mzs = [round(mz, 2) for mz in mzs]
    mzs = list(set(mzs))
    chromatograms = pd.DataFrame(columns = mzs + ['RT'])

    for spectrum in mzml_reader:
        #only consider MS1 spectra
        if spectrum.ms_level == 1:
            
            #initialize a new row for our chromatogram dataframe
            row = pd.Series(data = zeros((len(mzs) + 1,)), index = mzs + ['RT'], dtype = 'float32')

            #get retention time of the current scan
            row['RT'] = spectrum.scan_time_in_minutes()
            print('reading scan at RT = ' + str(spectrum.scan_time_in_minutes()))

            #retrieve intensities for each peak of interest
            for peak in spectrum.peaks('centroided'):
                rounded_mz = round(peak[0], 2)
                try:
                    row[rounded_mz] += peak[1]
                except KeyError:
                    pass
            chromatograms = pd.concat([chromatograms, pd.DataFrame(row).T])

    #return results as a dataframe with a column for retention time (RT) and column for corresponding intensities for each m/z of interest
    return chromatograms

n = 100
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', help = 'input file of peaks to xic (in Dinosaur output format)', required = True)
    parser.add_argument('-i', help = 'infected mzML file', required = True)
    parser.add_argument('-c', help = 'control mzML file', required = True)
    parser.add_argument('-o', help = 'output directory', required = True)

    args = parser.parse_args()

    peaks = pd.read_csv(args.p).sample(frac = 1.).iloc[0:n] #pick n random peaks to plot

    #read in raw mass spec data
    inf_mzml = pymzml.run.Reader(args.i)
    mock_mzml = pymzml.run.Reader(args.c)

    #get chromatograms for infected and mock data
    inf_chromatogram_data = xic(inf_mzml, peaks['mz'])
    inf_chromatogram_data.to_csv(join(args.o, 'infected_chromatograms.csv'))

    mock_chromatogram_data = xic(mock_mzml, peaks['mz'])
    mock_chromatogram_data.to_csv(join(args.o, 'mock_chromatograms.csv'))