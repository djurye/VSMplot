import tkinter as tk
from tkinter import filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from random import choice
import os


class GraphFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        # Layout
        self.prefix_var = tk.StringVar(value="corrected_")
        self.figure, self.ax = plt.subplots(figsize=(5, 4))

        self.colors = [
            "blue", "green", "red", "yellow", "orange", "pink", "purple", "brown", 
            "cyan", "gray", "violet", "teal", "maroon", "indigo", "goldenrod", 
            "turquoise", "peachpuff", "seashell", "chocolate", "salmon", "slategray",
            "azure", "beige", "black", "white", "lavender", "mintcream", "coral",
            "orchid", "khaki", "turquoise", "peru", "sienna", "mediumslateblue", 
            "mediumvioletred", "mediumseagreen", "mediumpurple", "lightcoral"
        ]
        self.color_options = self.colors[:]
        
        self.create_widgets()

    def create_widgets(self):
        # save graph selection
        save_graph_frame = tk.Frame(self)
        save_graph_frame.grid(row=0, column=1, padx=10, pady=(5,0), sticky="ew")
        tk.Label(save_graph_frame, text="Name for graph:").pack(side=tk.LEFT, padx=(0,5))
        tk.Entry(save_graph_frame, textvariable=self.prefix_var, width=20).pack(side=tk.LEFT, padx=5)
        tk.Button(save_graph_frame, text="Save Graph", command=self.save_graph, width=20).pack(side=tk.RIGHT, padx=(5,0))

        # Matplotlib canvas
        canvas_frame = tk.Frame(self)
        canvas_frame.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)
        canvas_frame.rowconfigure(0, weight=1, minsize=400)
        canvas_frame.columnconfigure(0, weight=1)
        self.canvas = FigureCanvasTkAgg(self.figure, canvas_frame)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")

        # Navigation buttons
        nav_frame = tk.Frame(self)
        nav_frame.grid(row=2, column=1,  pady=5)
        tk.Button(nav_frame, text="Previous", command=self.show_previous_file, width=12).grid(row=0, column=0, padx=5)
        tk.Button(nav_frame, text="Next", command=self.show_next_file, width=12).grid(row=0, column=1, padx=5)

    def pick_random_color(self):
        if not self.color_options:
            self.color_options = self.colors[1::3]
        
        # Escolhe uma cor aleatória das cores principais
        chosen_color = choice(self.color_options)
        
        # Remove a cor escolhida da lista de cores principais e da lista de cores disponíveis
        self.color_options.remove(chosen_color)
        
        return chosen_color

    def plot_data(self, data):
        self.ax.clear()
        self.configure_hysteresis_curve_graph(data["file_name"])
        self.ax.plot(data["regression_line_magnetic_field"], data["regression_line_moment"], label="Regression Line", color="blue", linewidth = 0.8)
        self.ax.plot(data["magnetic_field"], data["original_moment"], label="Original Curve", color="red", linewidth = 0.6, linestyle=":")
        self.axins.plot(data["magnetic_field"], data["original_moment"], color="red", linewidth = 0.6, linestyle=":")
        self.ax.plot(data["magnetic_field"], data["corrected_moment"], label="Modified Curve", color="black")
        self.axins.plot(data["magnetic_field"], data["corrected_moment"], color="black")

        self.ax.legend()
        self.canvas.draw()

    def plot_selected_files(self, data):
        self.ax.clear()
        self.configure_hysteresis_curve_graph("MxH")
        if data:
            for curve in data:
                if curve["color"] == "":
                    curve["color"] = self.pick_random_color()

                self.ax.plot(curve["magnetic_field"], curve["corrected_moment"], label=curve["legend"], color=curve["color"])
                self.axins.plot(curve["magnetic_field"], curve["corrected_moment"], color=curve["color"])

        self.ax.legend(loc='upper left', fontsize=6)
        self.canvas.draw()

    def show_previous_file(self):
        #recupere o current_index da classe fileframe
        file_frame = self.controller.file_frame  # Acessa FileFrame via controlador
        current_index = file_frame.get_current_index()  # Obtém índice atual 
        
        if current_index > 0:
            file_frame.set_current_index(current_index - 1)

        elif current_index == 0:
            file_paths = file_frame.get_file_paths()
            file_frame.set_current_index(len(file_paths) - 1)

        self.controller.process_and_plot_current_file()
        #self.process_and_plot_current_file()

    def show_next_file(self):
        file_frame = self.controller.file_frame  # Acessa FileFrame via controlador
        current_index = file_frame.get_current_index()  # Obtém índice atual 
        file_paths = file_frame.get_file_paths()

        if current_index < len(file_paths) - 1:
            file_frame.set_current_index(current_index + 1)

        elif current_index == len(file_paths) - 1:
            file_frame.set_current_index(0)

        self.controller.process_and_plot_current_file()

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

    def get_frame(self):
        return self
    