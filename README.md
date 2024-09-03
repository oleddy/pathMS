# pathMS
PathMS is a computational pipeline that enables selective targeting of pathogen-specific peptides in mixed host-pathogen proteomic samples by mass spectrometry (MS), helping to identify the "needle in a haystack" of pathogen-derived peptides in a host-dominated sample. By analyzing LC-MS data, pathMS identifies precursor ion peaks that are unique to infected cells and absent in uninfected controls and generates an inclusion list of these peaks that can be targeted in a subsequent targeted MS analysis (for example, using parallel reaction monitoring). 

PathMS is the computational pipeline used in our PathMHC immunopeptidomics workflow for vaccine target discovery, enabling more efficient detection of pathogen-derived peptides presented on MHCs for recognition by T cells. 

PathMS has three main steps:
1. Dinosaur (https://github.com/fickludd/dinosaur) is used to identify precursor ion peaks. 
2. Precursor ion peaks in the sample from infected cells and uninfected cells are aligned using DeepRTalign (). Precursor ions in the infected sample that do not match with any precursor in the uninfected sample are selected for further analysis. 
3. Precursor ion peaks are quality scored using AutoMS (https://github.com/oleddy/AutoMS, forked from https://github.com/hcji/AutoMS) using a denoising autoencoder and a signal/noise ratio calculation based on a continuous wavelet transform. 

## Installation

Run the following in the command line to download the code: 
~~~
git clone -- recurse-submodules https://github.com/oleddy/pathMS.git
~~~

Please note that you must use the `--recurse-submodules` flag or AutoMS will not be correctly installed. 

Install Python dependencies as follows:
~~~
pip install -r requirements.txt
~~~
Using a virtual environment to install dependencies and run the code is recommended. 

In addition, Dinosaur requires that you have Java installed. PathMS was tested with Java version 1.8.0_411. 

PathMS uses R dependencies via `rpy2`. Download and install R version 4.4.0 ("Puppy Cup") from https://www.r-project.org/. Install the R dependencies of AutoMS as follows:
~~~
install.packages("BiocManager")
BiocManager::install("xcms")
BiocManager::install("MSnbase")
~~~

If you are using MacOS, you may need to add the following to your .bash_profile to get `rpy2` (and therefore AutoMS) to work:
~~~
export DYLD_LIBRARY_PATH="/Library/Frameworks/R.framework/Libraries:$DYLD_LIBRARY_PATH"
export PKG_CONFIG_PATH="/usr/X11/lib/pkgconfig:$PKG_CONFIG_PATH"
~~~

PathMS was tested on MacOS 12.0.1 with Python 3.12.3. 

## Input files

MS data should be in .mzml format. Only MS1 data will be directly analyzed, so MS2 data (that is, MS/MS spectra) can be excluded when exporting files. One .mzml file for the infected sample and one for the uninfected sample are required. Additionally, a spreadsheet of peptide-spectrum matches from a database search of your MS run of the infected sample is needed, so that peptides already identified in the initial untargeted MS run are not added to the inclusion list for the targeted MS run. An example can be found under `/examples`. Other parameters are discussed below. 

## Expected output
The output will be a .csv file called `inclusion_list.csv` specifying the list of putative infection-specific precursor ions to be targeted for MS analysis, generated in the specified working directory (see parameters below). This file is formatted so it can be imported directly as an inclusion list in the "Targeted Mass" node of a Thermo mass spec instrument method. The list may need to be reformatted for other instruments. 

In addition, the following outputs will be automatically generated in the working directory at intermediate steps in the pipeline:

|File|Description|
|:---|:---|
|`/features/inf.features.tsv`|Precursor ion peaks detected by Dinosaur for the infected sample|
|`/features/mock.features.tsv`|Precursor ion peaks detected by Dinosaur for the uninfected (control) sample|
|`sample_file.xlsx`|Spreadsheet of Dinosaur output files (used as input for DeepRTalign)|
|`mass_align_all_information`|Output from DeepRTalign, mapping precursor ion peaks in the infected sample to matching peaks in the uninfected sample.|
|`unpaired_peaks.csv`|Precursor ion peaks in the infected sample that were not matched with any peak in the uninfected sample (i.e., are putatively infection-specific)|
|`unpaired_peaks_AutoMS_z.csv`|Unpaired peaks csv file, converted to a format that can be used as input for AutoMS|
|`AutoMS_scores.csv`|Unpaired peaks csv file with AutoMS scores added|
|`inf_psms_match.csv`|Unpaired peaks with boolean field added indicating whether an ID for this peak was already found in the intiial MS run (from the provided PSM file)|

These outputs may be useful in diagnosing and troubleshooting problems, or analyzing why specific precursor ions were included or excluded in the final list of targets. 

## Use pathMS via the GUI
To launch the graphical interface for pathMS, run
~~~
python interface.py
~~~
in the `/scripts` directory. To set the default parameters for analysis of MHC class I peptides, click "Set MHC-I defaults." To set the default parameters for analysis of MHC class II peptides, click "Set MHC-II defaults." Otherwise, set parameters manually (see below for parameter descriptions). 

## Use pathMS via the command line
To run pathMS from the command line, run the
~~~
python pathms_cli.py
~~~
and specify the following arguments: 
|Argument |Definition|Required? (Y/N)|Default value|
|:--- |:--- |:---|:---|
|`-w`|Working directory (directory where intermediate and final outputs will be stored)|Y|N/A|
|`-d`|Path to .mzml file for infected (disease) condition sample|Y|N/A|
|`-c`|Path to .mzml file for uninfected (control) sample|Y|N/A|
|`-p`|Path to peptide-spectrum match file from database search of infected sample|Y|N/A|
|`--cores`|Number of CPU cores to allocate for multithreading|N|`1`|
|`--ppm`|m/z tolerance window to use when generating extracted ion chromatograms for AutoMS scoring, in parts per million (ppm)|N|`40`|
|`--len`|Width of time window to use when generating extracted ion chromatograms for AutoMS scoring, in seconds|N|`40`|
|`--min_intensity`|Minimum integrated peak intensity threshold|N|`1e4`|
|`--min_score`|Minimum AutoMS score threshold|N|`0.3`|
|`--min_snr`|Minimum AutoMS signal/noise ratio|N|`1.5`|
|`--min_rt`|Minimum retention time, in seconds (set to exclude sample loading period)|N|`25*60`|
|`--max_rt`|Maximum retention time, in seconds (set to exclude organic washout/equilibration at the end of the LC gradient)|N|`115*60`|
|`--window`|Retention time window width for inclusion list, in minutes (for scheduled PRM)|N|`3`|
|`-z`|Comma-separated list of charge states to include|N|`2,3`|
|`--regenerate`|Re-generate all intermediate outputs, even if they already exist. If set to `False`, resume from last saved intermediate output in the working directory, if one already exists.|N|`False`|
|`--chunksize`|Batch size for AutoMS scoring (used to avoid running out of memory by scoring too many precursor ions at once).|N|`4096`|

## Analysis scripts
In addition to the code for the pathMS pipeline itself, we provide additional scripts for analyzing your MS data and evaluating the performance of the pipeline. These can be useful in tuning parameters to meet the needs of your specific dataset and application area. 

For additional questions or support, please contact owenkleddy \[at\] gmail \[dot\] com or owenl \[at\] mit \[dot\] edu. 