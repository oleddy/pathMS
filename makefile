./features/mock.features.tsv: ./data/inf.mzML ./data/mock.mzML
	java -jar ../dinosaur/Dinosaur-1.2.0.free.jar --verbose --profiling --concurrency=4 ./data/mock.mzML
	mkdir features
	mv ./data/mock.features.tsv ./features/mock.features.tsv

./features/inf.features.tsv:
	java -jar ../dinosaur/Dinosaur-1.2.0.free.jar --verbose --profiling --concurrency=4 ./data/inf.mzML
	mv ./data/inf.features.tsv ./features/inf.features.tsv

sample_file.xlsx: ./features/inf.features.tsv ./features/mock.features.tsv
	python3 ../scripts/generate_sample_file.py -i ./features/inf.features.tsv -c ./features/mock.features.tsv -o sample_file.xlsx

./mass_align_all_information/: ./features/mock.features.tsv ./features/inf.features.tsv sample_file.xlsx
	python3 -m deeprtalign -bw 0.012 -bp 2 -m Dinosaur -f ./features -s sample_file.xlsx

unpaired_peaks.csv: ./mass_align_all_information/ ./features/inf.features.tsv
	python3 ../scripts/unpaired_peaks.py -g ./mass_align_all_information/ -i ./features/inf.features.tsv -o unpaired_peaks.csv

unpaired_peaks_AutoMS_z.csv: unpaired_peaks.csv
	python3 ../scripts/AutoMS_format.py -i unpaired_peaks.csv -o unpaired_peaks_AutoMS.csv

AutoMS_scores.csv: unpaired_peaks_AutoMS_z.csv ./data/inf.mzML
	python3 ../AutoMS/AutoMS_score_inf_only.py -u unpaired_peaks_AutoMS_z.csv -i ./data/inf.mzML -o AutoMS_scores.csv

inclusion_list.csv: AutoMS_scores.csv
	python3 ../scripts/inclusion_list_inf_only_no_psm.py -i AutoMS_scores.csv -o inclusion_list.csv