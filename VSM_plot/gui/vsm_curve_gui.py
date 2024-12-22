import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from VSM_plot.models.vsm_data import VsmData
from VSM_plot.core.curve_correction import CurveCorrector
import os

class VsmCurveApp:
    def __init__(self, root):
        self.root = root
        self.root.title("VSM Curve Correction Tool")

        # Lista para armazenar os arquivos selecionados
        self.file_paths = []
        self.current_index = 0
        self.corrected_data = None

        # Prefixo para os arquivos
        self.prefix_var = tk.StringVar(value="corrected_")

        # Layout
        self._create_widgets()

    def _create_widgets(self):
        # Botão para selecionar arquivos
        select_btn = tk.Button(self.root, text="Select Files", command=self.select_files)
        select_btn.pack(pady=5)

        # Campo de texto para prefixo
        tk.Label(self.root, text="Prefix for New Files:").pack(pady=2)
        prefix_entry = tk.Entry(self.root, textvariable=self.prefix_var, width=30)
        prefix_entry.pack(pady=2)

        # Área de gráficos
        self.figure, self.ax = plt.subplots(figsize=(5, 4))
        self.canvas = FigureCanvasTkAgg(self.figure, self.root)
        self.canvas.get_tk_widget().pack(pady=5)

        # Botões para navegar entre arquivos
        nav_frame = tk.Frame(self.root)
        nav_frame.pack()

        prev_btn = tk.Button(nav_frame, text="Previous", command=self.show_previous_file)
        prev_btn.grid(row=0, column=0, padx=5)
        next_btn = tk.Button(nav_frame, text="Next", command=self.show_next_file)
        next_btn.grid(row=0, column=1, padx=5)

        # Botão para salvar arquivos corrigidos
        save_btn = tk.Button(self.root, text="Save Corrected Files", command=self.save_files)
        save_btn.pack(pady=10)

    def select_files(self):
        # Abre um diálogo para selecionar arquivos
        files = filedialog.askopenfilenames(title="Select VSM Files", filetypes=[("DAT Files", "*.dat")])
        if files:
            self.file_paths = list(files)
            self.current_index = 0
            self.process_and_plot_current_file()

    def process_and_plot_current_file(self):
        if not self.file_paths:
            return

        # Processa o arquivo atual
        file_path = self.file_paths[self.current_index]
        vsm = VsmData(file_path)
        columns = ["Magnetic Field (Oe)", "Moment (emu)"]
        filtered_data = vsm.get_columns(columns)

        if filtered_data is not None:
            magnetic_field = filtered_data["Magnetic Field (Oe)"]
            moment = filtered_data["Moment (emu)"]

            corrector = CurveCorrector(magnetic_field, moment)

            # Remove a inclinação
            corrected_moment = corrector.remove_inclination()
            regression_line = corrector.get_regression_line()
            
            # Normaliza os dados
            #moment, corrected_moment = corrector.normalize_data()

            # Salva os dados corrigidos temporariamente
            self.corrected_data = corrector.get_inclination_corrected_data()

            # Plota as curvas
            self.ax.clear()
            self.ax.plot(magnetic_field, moment, label="Original Curve")
            self.ax.plot(regression_line[0], regression_line[1], label="Regression Line", linestyle=":", color="orange")
            self.ax.plot(magnetic_field, corrected_moment, label="Corrected Curve", linestyle="--", color="green")
            self.ax.plot([min(magnetic_field), max(magnetic_field)], [max(corrected_moment), max(corrected_moment)], label="reta", linestyle="-", color="red", linewidth = 0.5)
            self.ax.plot([min(magnetic_field), max(magnetic_field)], [min(corrected_moment), min(corrected_moment)], label="reta", linestyle="-", color="red", linewidth = 0.5)

            self.ax.set_title(os.path.basename(file_path))
            self.ax.set_xlabel("Magnetic Field (Oe)")
            self.ax.set_ylabel("Moment (emu)")
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

# Executa o aplicativo
if __name__ == "__main__":
    root = tk.Tk()
    app = VsmCurveApp(root)
    root.mainloop()
