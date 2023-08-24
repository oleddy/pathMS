import os
import subprocess
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', help = 'input infected file (Dinosaur feature output)', required = True)
    parser.add_argument('-c', help = 'input control file path (Dinosaur feature output)', required = True)
    parser.add_argument('-o', help = 'output directory', required = True)

    args = parser.parse_args()

    inf_files = os.listdir(args.i)

    try: #remove .DS_Store
        inf_files.remove('.DS_Store')
    except ValueError:
        pass

    ctrl_files = os.listdir(args.c)

    try:
        ctrl_files.remove('.DS_Store')
    except ValueError:
        pass

    for file in inf_files:

        file_split = file.split('.')
        feature_file = '.'.join(file_split[:-1] + ['features.tsv']) #derive output file name from input file name

        os.system('java -jar ../dinosaur/Dinosaur-1.2.0.free.jar --verbose --profiling --concurrency=4 ' + os.path.join(args.i, file))
        os.system('mv ' + os.path.join(args.i, feature_file) + ' ' + os.path.join(args.o, feature_file)) #move output file to desired output path
    
    for file in ctrl_files:

        file_split = file.split('.')
        feature_file = '.'.join(file_split[:-1] + ['features.tsv']) #derive output file name from input file name

        os.system('java -jar ../dinosaur/Dinosaur-1.2.0.free.jar --verbose --profiling --concurrency=4 ' + os.path.join(args.c, file))
        os.system('mv ' + os.path.join(args.c, feature_file) + ' ' + os.path.join(args.o, feature_file)) #move output file to desired output path
    