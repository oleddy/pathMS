#!/bin/bash
#SBATCH -n 12
#SBATCH -N 4
#SBATCH -C centos7 #Request only Centos7 nodes
#SBATCH -p sched_mit_hill #Run on sched_engaging_default partition
#SBATCH --mem-per-cpu=4000 #Request 4G of memory per CPU
#SBATCH -o ../output/output_%j.txt #redirect output to output_JOBID.txt
#SBATCH -e ../output/error_%j.txt #redirect errors to error_JOBID.txt
#SBATCH --mail-type=BEGIN,END #Mail when job starts and ends
#SBATCH --mail-user=owenl@mit.edu #email recipient

RUNPATH=/home/owenl/pathms/pathMS/
cd $RUNPATH
module add python/3.8
source ./venv/bin/activate

python3 -m deeprtalign -bw 0.02 -bp 2 -pn 12 -m Dinosaur -f ./hMoDC_fractions/hMoDC_fraction_features -s ./hMoDC_fractions/sample_file.xlsx