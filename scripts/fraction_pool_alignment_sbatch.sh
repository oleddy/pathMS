#!/bin/bash
#SBATCH -n 6
#SBATCH -N 1
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

while getopts s:f:o: flag
do
    case "${flag}" in
        s) samplepath=${OPTARG};;
        f) featurepath=${OPTARG};;
        o) outputpath=${OPTARG};;
    esac
done

cd $outputpath
python3 -m deeprtalign -bp 2 -pn 4 -m Dinosaur -f $featurepath -s $samplepath