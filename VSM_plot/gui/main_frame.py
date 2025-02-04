import tkinter as tk
from tkinter import filedialog
from VSM_plot.gui.file_frame import FileFrame
from VSM_plot.gui.graph_frame import GraphFrame



class MainFrame(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("VSM Curve Correction Tool")
        self.create_widgets()

    def create_widgets(self):

        self.mainframe = tk.Frame(self, bg="lightgray", bd=2, relief="solid")
        self.mainframe.pack(padx=20, pady=20, fill="both", expand=True)  # Margens de 20px ao redor
        
        #self.menu_frame = tk.Frame(self.mainframe, bg="pink")
        #self.menu_frame.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=10)
        #tk.Button(self.menu_frame, text="Select Files", command=self.select_files, width=15).pack(side=tk.LEFT, padx=(0,5))
        #tk.Button(self.menu_frame, text="Plot Selected Graphs", command=self.process_and_plot_selected_files).pack(side=tk.LEFT, padx=(0,5))

        self.file_frame = FileFrame(self.mainframe, self)
        self.file_frame.get_frame().grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.graph_frame = GraphFrame(self.mainframe, self)
        self.graph_frame.get_frame().grid(row=1, column=1, sticky="nsew", padx=10, pady=10)


        # Configura o layout da raiz
        self.mainframe.rowconfigure(0, weight=1)  # Para o canvas e o TreeView
        self.mainframe.rowconfigure(1, weight=12)  # Para o canvas e o TreeView
        self.mainframe.rowconfigure(2, weight=1)  # Para o canvas e o TreeView
        self.mainframe.columnconfigure(0, weight=3)  # Para o canvas
        self.mainframe.columnconfigure(1, weight=7)  # Para o TreeView
        #self.mainframe.pack(padx=10, pady=10, fill="both", expand=True)

    def process_and_plot_current_file(self):
        if not self.file_frame.file_paths:
            return
        file_path = self.file_frame.file_paths[self.file_frame.current_index]
        data = self.file_frame.process_file(file_path)
        if data:
            self.graph_frame.plot_data(data)

    def process_and_plot_selected_files(self):
        data = self.file_frame.process_selected_files()
        self.graph_frame.plot_selected_files(data)  

    def select_files(self):
        # Abre um diálogo para selecionar arquivos
        files = filedialog.askopenfilenames(title="Select VSM Files", filetypes=[("DAT Files", "*.dat")])
        if files:
            file_paths = list(files)
            self.file_frame.current_index = 0
            self.file_frame.update_treeview(file_paths)
            self.process_and_plot_current_file()

# Executa o aplicativo
if __name__ == "__main__":
    app = MainFrame()
    app.mainloop()