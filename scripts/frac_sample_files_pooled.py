import pandas
import argparse
from os import listdir
from os.path import basename, join
import pandas as pd

##This script generates a sample file (.xlsx file) for a set of fraction comparisons

def features_file(file):
    file_split = file.split('.')
    feature_file = '.'.join(file_split[:-1] + ['features.tsv']) #derive output file name from input file name
    return feature_file

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', help = 'infected feature file directory', required = True)
    parser.add_argument('-c', help = 'control feature file directory', required = True)
    parser.add_argument('-o', help = 'output sample table file path', required = True)
    args = parser.parse_args()

    inf_folder = args.i.split('/')[-1]
    # inf_files = [join(inf_folder, basename(file)) for file in listdir(args.i)]
    inf_files = [features_file(basename(file)) for file in listdir(args.i)]

    try: #remove .DS_Store
        inf_files.remove('.DS_Store')
    except ValueError:
        pass

    ctrl_folder = args.c.split('/')[-1]
    # ctrl_files = [join(ctrl_folder, basename(file)) for file in listdir(args.c)]
    ctrl_files = [features_file(basename(file)) for file in listdir(args.c)]

    try:
        ctrl_files.remove('.DS_Store')
    except ValueError:
        pass
    inf_files = [file for file in inf_files if file[0] != '.']
    ctrl_files = [file for file in ctrl_files if file[0] != '.']
    n_frac = len(inf_files)
    print(inf_files)
    print(len(inf_files))
    print(ctrl_files)
    print(len(ctrl_files))
    assert len(inf_files) == len(ctrl_files)
    for i in range(n_frac):

        sample_table = pd.DataFrame(columns = ['file', 'sample', 'fraction'])

        sample_table['file'] = [inf_files[(i-1) % n_frac], inf_files[i], inf_files[(i+1) % n_frac], ctrl_files[(i-1) % n_frac], ctrl_files[i], ctrl_files[(i+1) % n_frac]]
        sample_table['sample'] = ['A' + str(i + 1) for i in range(6)]
        sample_table['fraction'] = ['F1']*6
        sample_table.to_excel(join(args.o,'F'+str(i+1)+'_sample_file.xlsx'), index = False)
    