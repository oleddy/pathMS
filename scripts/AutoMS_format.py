import pandas as pd
import argparse

'''
This script takes a csv file in the format output by Dinosaur (specifying LC-MS features) and converts it to XCMS format. 
The output table can then be used as an input to the AutoMS_External() function of AutoMS to generate quality scores for these features
using a denoising autoencoder. 

'''

#TODO: save a version with and without charge state (z)
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', help = 'input file (Dinosaur feature format)', required = True)
    parser.add_argument('-o', help = 'output file path (XCMS format)', required = True)

    args = parser.parse_args()

    #dictionary mapping columns of Dinosaur feature table format to XCMS format
    column_dict = {
        'mz' : 'mz',
        'rtApex' : 'rt',
        'rtStart' : 'rt1',
        'rtEnd' : 'rt2',
        'intensityApex' : 'intensity'
    }

    column_dict = {
        'mz' : 'mz',
        'rtApex' : 'rt',
        'rtStart' : 'rt1',
        'rtEnd' : 'rt2',
        'intensityApex' : 'intensity',
        'charge' : 'z'
    }

    output_columns = list(column_dict.values()) #we are only going to take the columns relevant to the XCMS format (i.e., the same ones we're renaming)

    input_table = pd.read_csv(args.i) #get the input data
    input_table.rename(mapper = column_dict, axis = 1, inplace = True) #rename columns in place

    #XCMS counts RT in seconds, so we need to convert our RTs from minutes to seconds. 
    input_table['rt'] =  input_table['rt']*60.
    input_table['rt1'] =  input_table['rt1']*60.
    input_table['rt2'] =  input_table['rt2']*60.

    #generate output path for the version of the file with z (charge state) included
    output_dir_split = args.o.split('.')
    output_dir_2 = '.'.join(output_dir_split[:-1]) + '_z.' + output_dir_split[-1] #insert '_z' before the file extension

    output_table = input_table[output_columns] #take only the columns relevant for the XCMS format
    output_table.to_csv(output_dir_2, index = False) #output the reformatted table

    #remove 'z' from list of columns and output this as a separate version of the table
    output_columns.remove('z')
    output_table_2 = input_table[output_columns]
    output_table_2.to_csv(args.o, index = False)

   



