import argparse
# import os
from os.path import basename
import pandas as pd

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', help = 'input infected file (Dinosaur feature output)', required = True)
    parser.add_argument('-c', help = 'input control file path (Dinosaur feature output)', required = True)
    parser.add_argument('-o', help = 'output file path', required = True)
    
    args = parser.parse_args()

    #TO DO: Add support for fractionated samples – check if the inputs are directories rather than files and if so add each file in the directory as a separate fraction
    #generate sample table in appropriate format for input to deeprtalign
    sample_table = pd.DataFrame([[basename(args.i), 'A1', 'F1'], [basename(args.c), 'A2', 'F1']], columns = ['file', 'sample', 'fraction'])
    sample_table.to_excel(args.o, index = False)