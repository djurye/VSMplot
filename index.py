from VSM_plot.models.vsm_data import VsmData
from VSM_plot.core.curve_correction import CurveCorrector

def main():
    # Caminho do arquivo
    file_path = "FLAT_COPT_CO3NM_PARALELO_00001.dat"

    # Carrega os dados usando VsmData
    vsm = VsmData(file_path)
    columns = ["Magnetic Field (Oe)", "Moment (emu)"]
    filtered_data = vsm.get_columns(columns)

    if filtered_data is not None:
        magnetic_field = filtered_data["Magnetic Field (Oe)"]
        moment = filtered_data["Moment (emu)"]

        # Remove a inclinação da curva
        corrector = CurveCorrector(magnetic_field, moment)
        corrector.remove_inclination()

        # Salva os dados corrigidos em CSV
        corrector.save_corrected_data("corrected_vsm_data.csv")

if __name__ == "__main__":
    main()
