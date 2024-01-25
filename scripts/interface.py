import tkinter as tk
from tkinter import filedialog

from os.path import join

class PathMS_App:
    def __init__(self, master):
        self.master = master
        self.master.title("pathMS")

        #infected/perturbed condition mzML file
        self.create_file_entry("Disease/treatment condition mzML file:", 0, 0, filetypes = [('mzML files', '*.mzML')])

        #control condition mzML file
        self.create_file_entry("Control condition mzML file:", 1, 0, filetypes = [('mzML files', '*.mzML')])

        #quality filters csv file
        self.create_file_entry("Quality filters table", 2, 0, filetypes = [('CSV files', '*.csv')])
        
        #working directory (where output and intermediate files will be generated)
        self.wd_label = tk.Label(master, text="Working directory:")
        self.wd_label.grid(row=3, column=0, padx=10, pady=10, sticky=tk.W)

        self.wd_entry = tk.Entry(master, width=50)
        self.wd_entry.grid(row=3, column=1, padx=10, pady=10)

        self.wd_browse_button = tk.Button(master, text="Browse", command=self.browse_working_directory)
        self.wd_browse_button.grid(row=3, column=2, padx=10, pady=10)

        #


    def create_file_entry(self, label_text, row, column, filetypes = [('mzML files', '*.mzML')]):
        label = tk.Label(self.master, text=label_text)
        label.grid(row=row, column=column, padx=10, pady=10, sticky=tk.W)

        entry = tk.Entry(self.master, width=50)
        entry.grid(row=row, column=column + 1, padx=10, pady=10)

        browse_button = tk.Button(self.master, text="Browse", command=lambda: self.browse_file(entry, filetypes))
        browse_button.grid(row=row, column=column + 2, padx=10, pady=10)

    def browse_file(self, file_entry, filetypes):
        file_path = filedialog.askopenfilename(filetypes = filetypes)
        file_entry.delete(0, tk.END)
        file_entry.insert(0, file_path)

    def browse_working_directory(self):
        directory_path = filedialog.askdirectory()
        self.output_entry.delete(0, tk.END)
        self.output_entry.insert(0, directory_path)

    def start_processing(self):
        # run the program
        file1_path = self.file1_entry.get()
        file2_path = self.file2_entry.get()
        ppm_value = self.ppm_entry.get()
        length_value = self.length_entry.get()
        output_directory = self.output_entry.get()

if __name__ == '__main__':
    root = tk.Tk()
    app = PathMS_App(root)
    root.mainloop()