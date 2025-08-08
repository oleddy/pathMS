import tkinter as tk
from tkinter import filedialog
from multiprocessing import cpu_count
import threading

from pathms_cli import run_pathms

from os.path import join


#TO DO: add mz and RT column names in PSM file as arguments?
class PathMS_App:
    def __init__(self, master):
        self.master = master
        self.master.title("pathMS")

        #infected/perturbed condition mzML file
        self.inf_mzml_entry = self.create_file_entry("Disease/treatment condition mzML file:", 0, 0, filetypes = [('mzML files', '*.mzML')])

        #control condition mzML file
        self.ctrl_mzml_entry = self.create_file_entry("Control condition mzML file:", 1, 0, filetypes = [('mzML files', '*.mzML')])

        #PSMs csv file
        #must be csv with columns 'RT in min' and 'mz in Da'
        self.psms_entry = self.create_file_entry("PSMs table", 2, 0, filetypes = [('CSV files', '*.csv')])

        #working directory (where output and intermediate files will be generated)
        self.wd_label = tk.Label(master, text="Working/output directory:")
        self.wd_label.grid(row=3, column=0, padx=10, pady=10, sticky=tk.W)

        self.wd_entry = tk.Entry(master, width=50)
        self.wd_entry.grid(row=3, column=1, padx=10, pady=10)

        self.wd_browse_button = tk.Button(master, text="Browse", command=self.browse_working_directory)
        self.wd_browse_button.grid(row=3, column=2, padx=10, pady=10)

        #numerical parameters
        self.ppm_entry = self.create_parameter_entry("XIC mass tolerance (ppm):", 4, 0)
        self.length_entry = self.create_parameter_entry("XIC duration (seconds):", 5, 0)
        self.charge_entry = self.create_parameter_entry("List of charge states (comma-separated):", 6, 0)
        self.window_entry = self.create_parameter_entry("PRM scheduling time window (minutes):", 7, 0)
        self.n_cores_entry = self.create_parameter_entry("Number of cores:", 8, 0)
        self.min_score_entry = self.create_parameter_entry("Minimum AutoMS score:", 9, 0)
        self.min_snr_entry = self.create_parameter_entry("Minimum signal/noise ratio:", 10, 0)
        self.min_intensity_entry = self.create_parameter_entry("Minimum intensity:", 11, 0)
        self.min_rt_entry = self.create_parameter_entry("Minimum retention time (minutes):", 12, 0)
        self.max_rt_entry = self.create_parameter_entry("Maximum retention time (minutes):", 13, 0)
        self.chunksize_entry = self.create_parameter_entry("AutoMS batch size: ", 14, 0)

        #set MHC-I default parameters
        self.set_defaults_I_button = tk.Button(master, text="Set MHC-I defaults", command=self.set_defaults_MHC_I)
        self.set_defaults_I_button.grid(row=15, column=0, pady=20)

        #set MHC-II default parameters
        self.set_defaults_I_button = tk.Button(master, text="Set MHC-II defaults", command=self.set_defaults_MHC_II)
        self.set_defaults_I_button.grid(row=15, column=1, pady=20)

        #start button
        self.start_button = tk.Button(master, text="Start", command=self.start_processing)
        self.start_button.grid(row=15, column=2, pady=20)


    def create_file_entry(self, label_text: str, row: int, column: int, filetypes = [('mzML files', '*.mzML')]):
        label = tk.Label(self.master, text=label_text)
        label.grid(row=row, column=column, padx=10, pady=10, sticky=tk.W)

        entry = tk.Entry(self.master, width=50)
        entry.grid(row=row, column=column + 1, padx=10, pady=10)

        browse_button = tk.Button(self.master, text="Browse", command=lambda: self.browse_file(entry, filetypes))
        browse_button.grid(row=row, column=column + 2, padx=10, pady=10)

        return entry

    def create_parameter_entry(self, label_text: str, row: int, column: int):
        label = tk.Label(self.master, text = label_text)
        label.grid(row = row, column = column, padx = 10, pady = 10, sticky = tk.W)

        entry = tk.Entry(self.master)
        entry.grid(row = row, column = column+1, padx = 10, pady = 10)

        return entry


    def browse_file(self, file_entry, filetypes):
        file_path = filedialog.askopenfilename(filetypes = filetypes)
        file_entry.delete(0, tk.END)
        file_entry.insert(0, file_path)

    def browse_working_directory(self):
        directory_path = filedialog.askdirectory()
        self.wd_entry.delete(0, tk.END)
        self.wd_entry.insert(0, directory_path)

    def set_entry_default(self, entry, value):
        entry.delete(0, tk.END)
        entry.insert(0, value)

    def set_defaults_MHC_I(self):
        self.set_entry_default(self.ppm_entry, "10")
        self.set_entry_default(self.length_entry, '40')
        self.set_entry_default(self.n_cores_entry, cpu_count() - 1)
        self.set_entry_default(self.min_intensity_entry, "1e4")
        self.set_entry_default(self.min_score_entry, '0.2')
        self.set_entry_default(self.min_snr_entry, '1')
        self.set_entry_default(self.min_rt_entry, '25')
        self.set_entry_default(self.max_rt_entry, '115')
        self.set_entry_default(self.window_entry, '3')
        self.set_entry_default(self.charge_entry, '2,3,4')
        self.set_entry_default(self.chunksize_entry, '4096')

    def set_defaults_MHC_II(self):
        self.set_entry_default(self.ppm_entry, "40")
        self.set_entry_default(self.length_entry, '40')
        self.set_entry_default(self.n_cores_entry, cpu_count() - 1)
        self.set_entry_default(self.min_intensity_entry, "1e4")
        self.set_entry_default(self.min_score_entry, '0.3')
        self.set_entry_default(self.min_snr_entry, '1.5')
        self.set_entry_default(self.min_rt_entry, '25')
        self.set_entry_default(self.max_rt_entry, '115')
        self.set_entry_default(self.window_entry, '3')
        self.set_entry_default(self.charge_entry, '2,3,4')
        self.set_entry_default(self.chunksize_entry, '4096')

    def start_processing(self):
        # run the program
        inf_path = self.inf_mzml_entry.get()
        ctrl_path = self.ctrl_mzml_entry.get()
        psm_path = self.psms_entry.get()
        wd = self.wd_entry.get()
        
        ppm_value = self.ppm_entry.get()
        length_value = self.length_entry.get()
        charge_value = self.charge_entry.get()
        window_value = self.window_entry.get()
        n_cores_value = self.n_cores_entry.get()
        min_score_value = self.min_score_entry.get()
        min_snr_value = self.min_snr_entry.get()
        min_intensity_value = self.min_intensity_entry.get()
        min_rt_value = self.min_rt_entry.get()
        max_rt_value = self.max_rt_entry.get()
        chunksize_value = self.chunksize_entry.get()

        self.status_label = tk.Label(self.master, text = 'Running... (this may take up to 3 hours)')
        self.status_label.grid(row = 16, column = 0, pady = 10)

        args = (inf_path,
                   ctrl_path,
                   psm_path,
                   wd
                )
        
        kwargs = {
            'n_cores' : int(n_cores_value),
            'ppm' : int(ppm_value),
            'length' : float(length_value),
            'min_score' : float(min_score_value),
            'min_snr' : float(min_snr_value),
            'min_intensity':float(min_intensity_value),
            'charge_state_list':charge_value,
            'min_rt' : float(min_rt_value)*60.,
            'max_rt':float(max_rt_value)*60.,
            'window':float(window_value),
            'regenerate' : False,
            'chunksize':int(chunksize_value)
        }

        pathms_thread = threading.Thread(target = self.start_pathms, args = args, kwargs = kwargs)
        pathms_thread.start() 

    def start_pathms(self, *args, **kwargs):
        run_pathms(*args, **kwargs)
        self.master.after(0, lambda: self.update_status_label('Complete – see inclusion_list.csv for output'))
    
    def update_status_label(self, text):
        self.status_label.config(text = text)

if __name__ == '__main__':
    root = tk.Tk()
    app = PathMS_App(root)
    root.mainloop()