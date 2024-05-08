import argparse
import os
from os.path import join, abspath
import sys

from generate_sample_file import generate_sample_file
from unpaired_peaks import find_unpaired_peaks
from AutoMS_format import AutoMS_format
from match_psms import match_psms
from inclusion_list_inf_only import make_inclusion_list

sys.path.insert(0, '') #always include the current working directory in PYTHONPATH so that modules in the working directory can be imported after a working directory change

script_directory = os.path.dirname(os.path.abspath(sys.argv[0])) #directory where this script itself is located

def run_pathms(inf_mzml, mock_mzml, psms_file, working_dir, n_cores = 1, ppm = 40, length = 40, min_score = 0.3, min_snr = 1.5, min_intensity = 1e4, charge_state_list = '2,3', min_rt = 25.*60., max_rt = 115.*60., window = 3., regenerate = False, chunksize = 4096):
    
    #run Dinosaur to find MS1 peaks
    os.chdir(script_directory) #go to script directory to find the jar directory in relative terms
    dinosaur_jar_dir = abspath('../dinosaur/Dinosaur-1.2.0.free.jar') #find Dinosaur jar file
    os.chdir(working_dir) #go to working directory
    
    if not os.path.isdir('features'):
        os.mkdir('features') #make a folder to put the extracted features in
    
    mock_file_prefix = mock_mzml.split('/')[-1].split('.')[0]
    mock_features_path = abspath(mock_mzml)[:-5] + '.features.tsv'

    inf_file_prefix = inf_mzml.split('/')[-1].split('.')[0]
    inf_features_path = abspath(inf_mzml)[:-5] + '.features.tsv'
    
    #the "regenerate" variable indicates: has any file in the stack been re-generated? If so, re-generate all downstream files even if they already exist. Can also pass as argument to force regenerating all files. 

    print('Step 1: peak calling with Dinosaur')
    
    if (not os.path.isfile('./features/%s.features.tsv' % mock_file_prefix)) or (not os.path.isfile('./features/%s.features.tsv' % inf_file_prefix)) or regenerate:
        #run Dinosaur on mock/control mzML file
        os.system('java -Xmx8G -jar %s --verbose --profiling  --concurrency=%d %s' % (dinosaur_jar_dir, n_cores, abspath(mock_mzml))) 
        os.system('mv %s ./features/%s.features.tsv' % (mock_features_path, mock_file_prefix)) #move results to the features directory

        #run Dinosaur on infection/disease mzML file
        os.system('java -Xmx8G -jar %s --verbose --profiling --concurrency=%d %s' % (dinosaur_jar_dir, n_cores, abspath(inf_mzml))) 
        os.system('mv %s ./features/%s.features.tsv' % (inf_features_path, inf_file_prefix)) #move results to the features directory
    
        regenerate = True
    else:
        print('Using existing Dinosaur feature files')
    
    print('Step 2: generating sample file')

    #generate sample file
    if not os.path.isfile('sample_file.xlsx') or regenerate:
        generate_sample_file('./features/%s.features.tsv' % inf_file_prefix, './features/%s.features.tsv' % mock_file_prefix, 'sample_file.xlsx')
        regenerate = True
    else:
        print('Using existing sample file')
    
    print('Step 3: chromatographic alignment with deepRTalign')

    #run deeprtalign
    if not os.path.isdir('./mass_align_all_information') or regenerate:
        os.system('python3 -m deeprtalign -m Dinosaur -pn %d -f ./features -s sample_file.xlsx' % n_cores)
        regenerate = True
    else:
        print('Using existing chromatographic alignment')

    print('Step 4: finding unpaired peaks')

    #find unpaired peaks
    charge_states = [int(charge) for charge in charge_state_list.split(',')]
    if not os.path.isfile('unpaired_peaks.csv') or regenerate:
        find_unpaired_peaks(join(working_dir, 'mass_align_all_information'), join(working_dir,'features/%s.features.tsv') % inf_file_prefix, 'unpaired_peaks.csv', charge_states = charge_states)
        regenerate = True
    else:
        print('Using existing unpaired peaks file')

    print('Step 5: converting unpaired peaks to AutoMS input format')

    #convert unpaired peaks file to AutoMS-compatible format
    if not os.path.isfile('unpaired_peaks_AutoMS_z.csv') or regenerate:
        AutoMS_format('unpaired_peaks.csv', 'unpaired_peaks_AutoMS.csv')
        regenerate = True
    else:
        print('Using existing AutoMS input file')

    print('Step 6: running AutoMS')

    if not os.path.isfile(join(working_dir,'AutoMS_scores.csv')) or regenerate:
        #get absolute paths of mzML file so we can still find it after working directory change
        inf_mzml_abs = abspath(inf_mzml)

        #change to autoMS directory so autoMS will run properly
        os.chdir(script_directory)
        os.chdir('../AutoMS')

        #run AutoMS
        from AutoMS_score_inf_only import AutoMS_score
        AutoMS_score(join(working_dir, 'unpaired_peaks_AutoMS_z.csv'), inf_mzml_abs, join(working_dir, 'AutoMS_scores.csv'), length = length, ppm = ppm, n_cores = n_cores, chunksize = chunksize)

        #change back to working directory
        os.chdir(working_dir)

        regenerate = True
    else:
        print('Using existing AutoMS scores')

    print('Step 7: pairing MS1 peaks with PSMs')

    #match peaks with PSMs to eliminate peaks that have already been ID'ed in DDA run
    if not os.path.isfile('inf_psms_match.csv') or regenerate:
        match_psms(psms_file, 'unpaired_peaks_AutoMS_z.csv', 'inf_psms_match.csv')
    else:
        print('Using existing peak-PSM matches')

    print('Step 8: selecting final inclusion list')

    #make final inclusion list
    if not os.path.isfile('inclusion_list.csv') or regenerate:
        make_inclusion_list('AutoMS_scores.csv', 'inf_psms_match.csv', 'inclusion_list.csv', 
                            min_intensity = min_intensity,
                            min_score = min_score,
                            min_snr = min_snr,
                            min_rt = min_rt,
                            max_rt = max_rt,
                            window = window
                            )
    else:
        print('Inclusion list is already up to date!')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-w', help = 'working directory', required = True)
    parser.add_argument('-d', help = 'path to infection or disease condition mzML file (relative to working directory, or absolute)', required = True)
    parser.add_argument('-c', help = 'path to control condition mzML file (relative to working directory, or absolute)', required = True)
    parser.add_argument('-p', help = 'PSMs file', required = True)
    parser.add_argument('--cores', help = 'number of CPU cores to allocate for multithreading (default = 1)', required = False, default = 1, type = int)
    parser.add_argument('--ppm', help = 'm/z window for AutoMS XIC in ppm', type = float, required = False, default = 40)
    parser.add_argument('--len', help = 'length of AutoMS XIC', type = float, required = False, default = 40)
    parser.add_argument('--min_intensity', help = 'minimum peak intensity threshold', type = float, required = False, default = 1e4)
    parser.add_argument('--min_score', help = 'AutoMS score threshold', required = False, type = float, default = 0.3)
    parser.add_argument('--min_snr', help = 'AutoMS signal/noise ratio threshold', required = False, type = float, default = 1.5)
    parser.add_argument('--min_rt', help = 'minimum retention time (exclude peaks before) in seconds', required = False, default = 25.*60., type = float)
    parser.add_argument('--max_rt', help = 'maximum retention time (exclude peaks after) in seconds', required = False, default = 115.*60., type = float)
    parser.add_argument('--window', help = 'retention time window width for inclusion list scheduling (in minutes)', required = False, default = 3., type = float)
    parser.add_argument('-z', '--charges', help = 'comma separated list of charge states', required = False, default = '2,3')
    parser.add_argument('--regenerate', help = 're-generate all intermediate outputs, even if they already exist', required = False, default = False)
    parser.add_argument('--chunksize', help = 'batch size for AutoMS scoring', required = False, type = int, default = 4096)

    args = parser.parse_args()

    run_pathms(args.d, args.c, args.p, args.w, 
               n_cores = args.cores, 
               ppm = args.ppm, 
               length = args.len, 
               min_intensity=args.min_intensity, 
               min_score = args.min_score, 
               min_snr = args.min_snr,
               charge_state_list = args.charges,
               min_rt = args.min_rt,
               max_rt = args.max_rt,
               window = args.window,
               regenerate = args.regenerate,
               chunksize = args.chunksize
               )