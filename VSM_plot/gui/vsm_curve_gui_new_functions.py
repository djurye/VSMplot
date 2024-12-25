import tkinter as tk
from tkinter import filedialog, messagebox, ttk, colorchooser
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from random import choice
import re

import os
import sys, os, re
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from models.vsm_data import VsmData
from core.curve_correction import CurveCorrector

class VsmCurveApp:
    def __init__(self, root):
        self.root = root
        self.root.title("VSM Curve Correction Tool")

        # Lista para armazenar os arquivos selecionados
        self.file_paths = []
        self.current_index = 0
        self.corrected_data = None
        self.prefix_var = tk.StringVar(value="corrected_")

        # Layout
        self.figure, self.ax = plt.subplots(figsize=(5, 4))

        self._create_widgets()

        self.colors = [
            "blue", "green", "red", "yellow", "orange", "pink", "purple", "brown", 
            "cyan", "gray", "violet", "teal", "maroon", "indigo", "goldenrod", 
            "turquoise", "peachpuff", "seashell", "chocolate", "salmon", "slategray",
            "azure", "beige", "black", "white", "lavender", "mintcream", "coral",
            "orchid", "khaki", "turquoise", "peru", "sienna", "mediumslateblue", 
            "mediumvioletred", "mediumseagreen", "mediumpurple", "lightcoral"
        ]
        self.color_options = self.colors[:]

    def pick_random_color(self):
        if not self.color_options:
            self.color_options = self.colors[1::3]
        
        # Escolhe uma cor aleatória das cores principais
        chosen_color = choice(self.color_options)
        
        # Remove a cor escolhida da lista de cores principais e da lista de cores disponíveis
        self.color_options.remove(chosen_color)
        
        return chosen_color

    def _create_widgets(self):

        self.mainframe = tk.Frame(root, bg="lightgray", bd=2, relief="solid")
        self.mainframe.pack(padx=20, pady=20, fill="both", expand=True)  # Margens de 20px ao redor

        # Configura o layout da raiz
        self.mainframe.rowconfigure(0, weight=1)  # Para o canvas e o TreeView
        self.mainframe.rowconfigure(1, weight=12)  # Para o canvas e o TreeView
        self.mainframe.rowconfigure(2, weight=1)  # Para o canvas e o TreeView
        self.mainframe.columnconfigure(0, weight=3)  # Para o canvas
        self.mainframe.columnconfigure(1, weight=7)  # Para o TreeView
        self.mainframe.pack(padx=10, pady=10, fill="both", expand=True)

        # File selection
        file_frame = tk.Frame(self.mainframe)
        file_frame.grid(row=0, column=0, padx=(10,10), pady=(5,0), sticky="ew")
        tk.Button(file_frame, text="Select Files", command=self.select_files, width=15).pack(side=tk.LEFT, padx=(0,5))
        tk.Label(file_frame, text="Prefix for New Files:").pack(side=tk.LEFT, padx=(5,5))
        tk.Entry(file_frame, textvariable=self.prefix_var, width=15).pack(side=tk.LEFT, padx=5)
        tk.Button(file_frame, text="Save Corrected Files", command=self.save_files, width=20).pack(side=tk.RIGHT, padx=(5,0))

        # save graph selection
        save_graph_frame = tk.Frame(self.mainframe)
        save_graph_frame.grid(row=0, column=1, padx=10, pady=(5,0), sticky="ew")
        tk.Label(save_graph_frame, text="Name for graph:").pack(side=tk.LEFT, padx=(0,5))
        tk.Entry(save_graph_frame, textvariable=self.prefix_var, width=20).pack(side=tk.LEFT, padx=5)
        tk.Button(save_graph_frame, text="Save Graph", command=self.save_graph, width=20).pack(side=tk.RIGHT, padx=(5,0))

        # Matplotlib canvas
        canvas_frame = tk.Frame(self.mainframe)
        canvas_frame.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)
        canvas_frame.rowconfigure(0, weight=1)
        canvas_frame.columnconfigure(0, weight=1)
        self.canvas = FigureCanvasTkAgg(self.figure, canvas_frame)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")

        # TreeView para múltiplos gráficos
        multi_graph_frame = tk.LabelFrame(self.mainframe, text="Multiple Graphs", padx=5, pady=5)
        multi_graph_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
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

        # Navigation buttons
        nav_frame = tk.Frame(self.mainframe)
        nav_frame.grid(row=2, column=1,  pady=5)
        tk.Button(nav_frame, text="Previous", command=self.show_previous_file, width=12).grid(row=0, column=0, padx=5)
        tk.Button(nav_frame, text="Next", command=self.show_next_file, width=12).grid(row=0, column=1, padx=5)

        # Plot Selected Graphs button
        tk.Button(self.mainframe, text="Plot Selected Graphs", command=self.plot_selected_files, width=20).grid(row=2, column=0, pady=10)

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
                canvas_x = self.root.winfo_rootx()
                canvas_y = self.root.winfo_rooty()

                # Calcula as posições absolutas e ajusta ao container
                combobox_x = tree_x + bbox[0] - canvas_x
                combobox_y = tree_y + bbox[1] - canvas_y

                # Cria a Combobox
                legend_var = tk.StringVar()
                legend_entry = ttk.Entry(self.root, textvariable=legend_var)

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

    def process_and_plot_current_file(self):
        if not self.file_paths:
            return
        file_path = self.file_paths[self.current_index]
        data = self.process_file(file_path)
        if data:
            self.plot_data(data)

    def plot_data(self, data):
        self.ax.clear()
        self.configure_hysteresis_curve_graph(data["file_name"])
        self.ax.plot(data["magnetic_field"], data["corrected_moment"], label="Curve", color="green")
        self.axins.plot(data["magnetic_field"], data["corrected_moment"], color="green")

        self.ax.legend()
        self.canvas.draw()

    def plot_selected_files(self):
        selected_items = self.tree.selection()
        self.ax.clear()
        self.configure_hysteresis_curve_graph("MxH")
        for item_id in selected_items:
            file, color, legend = self.tree.item(item_id, "values")
            if color == "":
                color = self.pick_random_color()
            file_path = next((f for f in self.file_paths if os.path.basename(f) == file), None)
            if file_path:
                data = self.process_file(file_path)
                if data:
                    self.ax.plot(data["magnetic_field"], data["corrected_moment"], label=legend, color=color)
                    self.axins.plot(data["magnetic_field"], data["corrected_moment"], color=color)

        self.ax.legend(loc='upper left', fontsize=6)

        self.canvas.draw()

    def process_and_plot_selected_files(self):
        data = self.process_selected_files()
        self.plot_selected_files(data)  

    def select_files(self):
        # Abre um diálogo para selecionar arquivos
        files = filedialog.askopenfilenames(title="Select VSM Files", filetypes=[("DAT Files", "*.dat")])
        if files:
            self.file_paths = list(files)
            self.current_index = 0
            self.update_treeview()
            self.process_and_plot_current_file()

    def update_treeview(self):
        self.tree.delete(*self.tree.get_children())
        for file_path in self.file_paths:
            self.tree.insert("", tk.END, values=(os.path.basename(file_path), "", os.path.basename(file_path)))

    def process_file(self,file_path):
        columns = ["Magnetic Field (Oe)", "Moment (emu)"]
        vsm = VsmData(file_path)
        filtered_data = vsm.get_columns(columns)

        if filtered_data is not None:
            corrector = CurveCorrector(filtered_data["Magnetic Field (Oe)"], filtered_data["Moment (emu)"])
            corrected_moment = corrector.remove_inclination()
            # Normaliza os dados
            corrected_moment = corrector.normalize_data()[1]
            # excluir Salva os dados corrigidos temporariamente
            self.corrected_data = corrector.get_inclination_corrected_data()

            return {
                "file_name": os.path.basename(file_path),
                "magnetic_field": filtered_data["Magnetic Field (Oe)"],
                "corrected_moment": corrected_moment,
            }
        
        return None
    
    def process_current_file(self):
        """Processa o arquivo atual e retorna os dados necessários para plotagem."""
        if not self.file_paths:
            return None

        # Processa o arquivo atual
        file_path = self.file_paths[self.current_index]

        data = self.process_file(file_path)
        magnetic_field = data["magnetic_field"]
        corrected_moment = data["corrected_moment"]

        # Retorna os dados processados
        return {
            "file_name": os.path.basename(file_path),
            "magnetic_field": magnetic_field,
            "corrected_moment": corrected_moment,
        }
    
    def process_selected_files(self):
        if not self.file_paths:
            return None

        selected_items = self.tree.selection()
        self.ax.clear()
        data_list = []
        
        for item_id in selected_items:
            file, color, legend = self.tree.item(item_id, "values")
            file_path = next((f for f in self.file_paths if os.path.basename(f) == file), None)
            if file_path:
                data = self.process_file(file_path)
                if data:
                    self.ax.plot(data["magnetic_field"], data["corrected_moment"], label=legend, color=color)
        self.ax.legend()
        self.canvas.draw()

    def show_previous_file(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.process_and_plot_current_file()

    def show_next_file(self):
        if self.current_index < len(self.file_paths) - 1:
            self.current_index += 1
            self.process_and_plot_current_file()

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

    def save_graph(self):
        output_folder = filedialog.askdirectory(title="Select Output Folder")
        if not output_folder:
            return
        
        filename = self.graph_name_var.get()
        if not filename:
            filename="graph.png"

        base, extension = os.path.splitext(filename)
        counter = 1

        while os.path.exists(filename):
            filename = f"{base}_{counter}{extension}"
            counter += 1

        # Salva o arquivo corrigido
        output_file = os.path.join(output_folder, filename)

        self.figure.savefig(output_file,dpi=300)
        plt.show()

    def configure_hysteresis_curve_graph(self, file_name):
        # Configurações dos eixos
        self.ax.axhline(0, color='black', linewidth=0.8)  # Eixo X no centro
        self.ax.axvline(0, color='black', linewidth=0.8)  # Eixo Y no centro
        self.ax.get_yaxis().set_visible(True)
        self.ax.get_xaxis().set_visible(True)
        self.ax.tick_params(axis='x', labelbottom=False)
        self.ax.tick_params(axis='y', labelleft=False)

        # Configurações da região de zoom
        x1, x2, y1, y2 = -500, 500, -0.1, 0.1  # subregion of the original image
        self.axins = self.ax.inset_axes(
            [0.63, 0.04, 0.35, 0.35],
            xlim=(x1, x2), ylim=(y1, y2), xticklabels=[], yticklabels=[])
        self.axins.axhline(0, color='black', linewidth=0.6)  # Eixo X no centro
        self.axins.axvline(0, color='black', linewidth=0.6)  # Eixo Y no centro
        
        self.ax.indicate_inset_zoom(self.axins, edgecolor="black")

        # Adiciona título dos eixos
        self.ax.set_xlabel("Magnetic Field (Oe)", labelpad=10)
        self.ax.set_ylabel("Moment (emu)", labelpad=10)

        # Adiciona título e legendas
        self.ax.set_title(file_name, fontsize=10)
        self.ax.legend(fontsize=6)

  
# Executa o aplicativo
if __name__ == "__main__":
    root = tk.Tk()
    app = VsmCurveApp(root)
    root.mainloop()
