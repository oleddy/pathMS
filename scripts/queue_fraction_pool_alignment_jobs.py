import argparse
import os
from os import listdir
from os.path import basename, join

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', help = 'features file path', required = True)
    parser.add_argument('-s', help = 'sample files directory', required = True)
    parser.add_argument('-o', help = 'output directory', required = True)

    args = parser.parse_args()

    sample_files = [basename(file) for file in listdir(args.s)]

    try:
        sample_files.remove('.DS_Store')
    except ValueError:
        pass

    for i in range(len(sample_files)):
        sample_file_path = join(args.s, 'F' + str(i+1) + '_sample_file.xlsx')
        output_dir = join(args.o, 'F' + str(i+1) + '_alignment_information')
        os.system('sbatch fraction_pool_alignment_sbatch.sh -s ' + sample_file_path + ' -f ' + args.f + ' -o ' + output_dir)