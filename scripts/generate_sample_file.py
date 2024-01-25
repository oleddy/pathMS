import argparse
# import os
from os.path import basename
import pandas as pd

def generate_sample_file(inf_features, mock_features, outfile):
    #TO DO: Add support for fractionated samples – check if the inputs are directories rather than files and if so add each file in the directory as a separate fraction
    #generate sample table in appropriate format for input to deeprtalign
    sample_table = pd.DataFrame([[basename(inf_features), 'A1', 'F1'], [basename(mock_features), 'A2', 'F1']], columns = ['file', 'sample', 'fraction'])
    sample_table.to_excel(outfile, index = False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', help = 'input infected file (Dinosaur feature output)', required = True)
    parser.add_argument('-c', help = 'input control file path (Dinosaur feature output)', required = True)
    parser.add_argument('-o', help = 'output file path', required = True)
    
    args = parser.parse_args()

    generate_sample_file(args.i, args.c, args.o)