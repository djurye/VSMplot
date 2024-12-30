import tkinter as tk
from tkinter import filedialog, messagebox, ttk, colorchooser
import sys, os, re
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from models.vsm_data import VsmData
from core.curve_correction import CurveCorrector

class FileFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        # Lista para armazenar os arquivos selecionados
        self.file_paths = []
        self.current_index = 0
        self.prefix_var = tk.StringVar(value="corrected_")
        self.create_widgets()
        
    def create_widgets(self):
        # File selection
        save_file_frame = tk.Frame(self)
        save_file_frame.grid(row=0, column=0, padx=10, pady=(5,0), sticky="ew")
        
        tk.Button(save_file_frame, text="Select Files", width=15, command=self.controller.select_files).pack(side=tk.LEFT, padx=(0,5))
        tk.Label(save_file_frame, text="Prefix for New Files:").pack(side=tk.LEFT, padx=(0,5))
        tk.Entry(save_file_frame, textvariable=self.prefix_var, width=15).pack(side=tk.LEFT, padx=5)
        tk.Button(save_file_frame, text="Save Corrected Files", command=self.save_files, width=20).pack(side=tk.RIGHT, padx=(5,0))

        # TreeView para múltiplos gráficos
        multi_graph_frame = tk.LabelFrame(self, text="Multiple Graphs", padx=5, pady=5)
        multi_graph_frame.grid(row=1, column=0, columnspan=4, sticky="nsew", padx=10, pady=10)
        multi_graph_frame.rowconfigure(0, weight=1)
        multi_graph_frame.columnconfigure(0, weight=1)
        
        self.tree = ttk.Treeview(multi_graph_frame, columns=("file", "color", "legend"), show="headings", height=6)
        self.tree.grid(row=0, column=0, sticky="nsew")
        self.tree.heading("file", text="File")
        self.tree.heading("color", text="Line Color")
        self.tree.heading("legend", text="Legend")
        self.tree.column("file", width=200, anchor="w")
        self.tree.column("color", width=100, anchor="center")
        self.tree.column("legend", width=150, anchor="center")
        self.tree.bind("<Button-1>", self.on_tree_click)
        
        scrollbar = ttk.Scrollbar(multi_graph_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky="ns")

        tk.Button(self, text="Plot Selected Graphs", command=self.controller.process_and_plot_selected_files).grid(row=2, column=0, columnspan=2)


    def on_tree_click(self, event):
        item_id = self.tree.identify_row(event.y)
        column_id = self.tree.identify_column(event.x)
        
        id = int(''.join(re.findall(r'\d+', item_id))) - 1

        if column_id == "#2":  # Color column
            # Obtém as coordenadas do item e a posição relativa ao widget pai
            bbox = self.tree.bbox(item_id, column_id)
            if bbox:  # Garante que a coluna e o item têm um bounding box válido
                 #caixa de cores
                color_code = colorchooser.askcolor(title="Escolha uma cor")[1]
                if color_code:
                    # Atualiza a cor de fundo do label com a cor escolhida
                    self.tree.tag_configure(item_id, background=color_code)
                    self.tree.item(self.tree.get_children()[id], tags=(item_id,))

                    values = list(self.tree.item(item_id, "values"))
                    values[1] = color_code  # Atualiza a coluna de cor com o código hexadecimal
                    self.tree.item(item_id, values=tuple(values)) 

        if column_id == "#3":  # Legend column
            # Obtém as coordenadas do item e a posição relativa ao widget pai
            bbox = self.tree.bbox(item_id, column_id)
            if bbox:  # Garante que a coluna e o item têm um bounding box válido
                # Ajusta as coordenadas para incluir o deslocamento da Treeview
                tree_x = self.tree.winfo_rootx()
                tree_y = self.tree.winfo_rooty()
                canvas_x = self.winfo_rootx()
                canvas_y = self.winfo_rooty()

                # Calcula as posições absolutas e ajusta ao container
                combobox_x = tree_x + bbox[0] - canvas_x
                combobox_y = tree_y + bbox[1] - canvas_y

                # Cria a Combobox
                legend_var = tk.StringVar()
                legend_entry = ttk.Entry(self, textvariable=legend_var)

                # Posiciona a Combobox em relação ao container
                legend_entry.place(x=combobox_x, y=combobox_y, width=bbox[2], height=bbox[3])
                legend_var.set(self.tree.item(item_id, "values")[2])


            def save_legend(event):
                new_legend = legend_var.get()
                current_values = list(self.tree.item(item_id, "values"))
                current_values[2] = new_legend
                self.tree.item(item_id, values=current_values)
                legend_entry.destroy()

            legend_entry.bind("<Return>", save_legend)
            legend_entry.bind("<FocusOut>", save_legend)
            legend_entry.focus_set()    

    def populate_tree(self, data):
        """Popula o Treeview com dados iniciais."""
        for item in data:
            self.tree.insert("", tk.END, values=item)

    def update_treeview(self,file_paths):
        self.file_paths = file_paths
        for item in self.tree.get_children():
            self.tree.delete(item)

        for file_path in self.file_paths:
            self.tree.insert("", tk.END, values=(os.path.basename(file_path), "", os.path.basename(file_path)))

    def process_file(self,file_path):
        columns = ["Magnetic Field (Oe)", "Moment (emu)"]
        vsm = VsmData(file_path)
        filtered_data = vsm.get_columns(columns)

        if filtered_data is not None:
            corrector = CurveCorrector(filtered_data["Magnetic Field (Oe)"], filtered_data["Moment (emu)"])
            corrected_moment = corrector.remove_inclination()
            regression_line = corrector.get_regression_line()
            # Normaliza os dados
            moment, corrected_moment = corrector.normalize_data()
            # excluir Salva os dados corrigidos temporariamente
 
            return {
                "file_name": os.path.basename(file_path),
                "magnetic_field": filtered_data["Magnetic Field (Oe)"],
                "corrected_moment": corrected_moment,
                "original_moment": moment,
                "regression_line_magnetic_field": regression_line[0],
                "regression_line_moment": regression_line[1]
            }
        
        return None

    def process_selected_files(self):
        data = []
        if not self.file_paths:
            return None

        selected_items = self.tree.selection()
        
        for item_id in selected_items:
            file, color, legend = self.tree.item(item_id, "values")
            file_path = next((f for f in self.file_paths if os.path.basename(f) == file), None)
            if file_path:
                data.append(self.process_file(file_path))
                data[-1]["color"] = color
                data[-1]["legend"] = legend

        return data

    def save_files(self):
        if not self.file_paths:
            messagebox.showerror("Error", "No files to save.")
            return

        output_folder = filedialog.askdirectory(title="Select Output Folder")
        if not output_folder:
            return

        prefix = self.prefix_var.get()

        for index, file_path in enumerate(self.file_paths):
            # Processa cada arquivo novamente
            vsm = VsmData(file_path)
            columns = ["Magnetic Field (Oe)", "Moment (emu)"]
            filtered_data = vsm.get_columns(columns)

            if filtered_data is not None:
                magnetic_field = filtered_data["Magnetic Field (Oe)"]
                moment = filtered_data["Moment (emu)"]

                corrector = CurveCorrector(magnetic_field, moment)
                corrector.remove_inclination()

                # Salva o arquivo corrigido
                filename = os.path.basename(file_path)
                output_file = os.path.join(output_folder, f"{prefix}{filename}")
                corrector.save_corrected_data(output_file)

        messagebox.showinfo("Success", "Files saved successfully!")

    def select_files(self):
        # Abre um diálogo para selecionar arquivos
        files = filedialog.askopenfilenames(title="Select VSM Files", filetypes=[("DAT Files", "*.dat")])
        if files:
            file_paths = list(files)
            self.current_index = 0
            self.update_treeview(file_paths)
            self.controller.process_and_plot_current_file()


    def get_frame(self):
        return self
    
    def get_current_index(self):
        """Retorna o índice atual."""
        return self.current_index

    def set_current_index(self, new_index): 
        """Atualiza o índice atual."""
        if 0 <= new_index < len(self.file_paths):
            self.current_index = new_index
            print(f"Current Index Updated: {self.current_index}")
        else:
            print("Invalid index!")

    def get_file_paths(self):
        """Retorna o índice atual."""
        return self.file_paths
