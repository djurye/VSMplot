import numpy as np
import pandas as pd
from scipy.stats import linregress

class CurveCorrector:
    def __init__(self, magnetic_field, moment):
        self.magnetic_field = np.array(magnetic_field)
        self.moment = np.array(moment)
        self.corrected_moment = None
        self.regression_line = None

    def remove_inclination(self):
        """
        Remove a inclinação da curva usando regressão linear.
        Retorna os momentos corrigidos.
        """
        # Selecionar subconjunto para calcular regressão linear (pontos de maior valor)
        max_moment_index = np.argmax(self.moment)
        limite_magnetic_field = self.magnetic_field[max_moment_index]  # Maior valor de H
        indices = np.where(self.magnetic_field >= limite_magnetic_field)[0]
        H_linear = self.magnetic_field[indices]
        M_linear = self.moment[indices]
        self.regression_line = H_linear, M_linear
        
        # Calcular a regressão linear no subconjunto selecionado
        slope, intercept, _, _, _ = linregress(H_linear, M_linear)
        
        # Corrigir os momentos removendo a inclinação
        self.corrected_moment = self.moment - (slope * self.magnetic_field)
        print (self.corrected_moment)
        return self.corrected_moment

    def normalize_data(self):
        max_moment = np.max(np.abs(self.moment))
        self.moment = self.moment / max_moment

        max_corrected_moment = np.max(np.abs(self.corrected_moment))
        self.corrected_moment = self.corrected_moment / max_corrected_moment

        return self.moment, self.corrected_moment

    def get_inclination_corrected_data(self):
        """
        Retorna os dados corrigidos em um DataFrame.
        """
        return pd.DataFrame({
            "Magnetic Field (Oe)": self.magnetic_field,
            "Corrected Moment (emu)": self.corrected_moment
        })

    def get_regression_line(self):
        """
        Retorna a linha da regressão linear.
        """
        return self.regression_line
    
    def save_corrected_data(self, output_file):
        """
        Salva os dados corrigidos de momento magnético em um arquivo.
        O arquivo será salvo no formato de duas colunas: campo magnético (H) e momento magnético corrigido (M corrigido).
        
        Parâmetros:
            output_file (str): Caminho do arquivo de saída onde os dados serão salvos.
        """
        if self.corrected_moment is None:
            self.remove_inclination()  # Supondo que você tenha um método para corrigir o momento

        self.normalize_data()
        data_to_save = np.column_stack((self.magnetic_field, self.corrected_moment))
        
        np.savetxt(output_file, data_to_save, header="Campo Magnético (Oe)  Momento Magnético Corrigido (emu)", fmt="%f")

        print(f"Dados corrigidos salvos em {output_file}")
