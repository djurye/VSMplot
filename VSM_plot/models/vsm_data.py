import pandas as pd

class VsmData:
    def __init__(self, file_path):
        self.file_path = file_path
        self.header = {}  # Dicionário para armazenar o cabeçalho
        self.data = None  # DataFrame para armazenar os dados
        self._load_file()

    def _load_file(self):
        """
        Lê o arquivo, extrai o cabeçalho e os dados.
        """
        data_started = False
        data_lines = []

        with open(self.file_path, "r") as file:
            for line in file:
                line = line.strip()
                if not line:
                    continue
                
                # Detecta o fim do cabeçalho e o início dos dados
                if line == "[Data]":
                    data_started = True
                    continue
                
                # Processa o cabeçalho
                if not data_started and "=" in line:
                    key, value = line.split("=", 1)
                    self.header[key.strip()] = value.strip()
                
                # Coleta as linhas de dados
                if data_started:
                    data_lines.append(line)

        # Processa a seção de dados usando pandas
        if data_lines:
            column_names = data_lines[0].split(",")
            data_rows = [line.split(",") for line in data_lines[1:]]
            self.data = pd.DataFrame(data_rows, columns=column_names)
            self._convert_numeric_columns()

    def _convert_numeric_columns(self):
        """
        Converte colunas que devem ser numéricas.
        """
        for col in self.data.columns:
            try:
                self.data[col] = pd.to_numeric(self.data[col], errors="coerce")
            except ValueError:
                pass  # Ignora se não puder converter

    def get_header(self):
        """
        Retorna o cabeçalho como um dicionário.
        """
        return self.header

    def get_data(self):
        """
        Retorna os dados como um pandas DataFrame.
        """
        return self.data
    
    def get_columns(self, columns):
        """
        Retorna apenas as colunas especificadas.
        :param columns: Lista com os nomes das colunas desejadas.
        :return: DataFrame contendo as colunas especificadas.
        """
        if self.data is not None:
            try:
                return self.data[columns]
            except KeyError as e:
                print(f"Erro: Uma ou mais colunas não foram encontradas: {e}")
                return None
        else:
            print("Os dados não estão disponíveis.")
            return None


    def save_to_csv(self, output_path):
        """
        Salva os dados em um arquivo CSV.
        :param output_path: Caminho para salvar o arquivo CSV.
        """
        if self.data is not None:
            self.data.to_csv(output_path, index=False)
        else:
            print("Nenhum dado para salvar.")

# Exemplo de uso
if __name__ == "__main__":
    file_path = "FLAT_COPT_CO3NM_PARALELO_00001.dat"
    vsm = VsmData(file_path)

    # Exibe o cabeçalho
    print("--- Cabeçalho ---")
    for key, value in vsm.get_header().items():
        print(f"{key}: {value}")

    # Exibe os dados
    print("\n--- Dados ---")
    print(vsm.get_data().head())

    # Salva os dados em um CSV
    vsm.save_to_csv("processed2_vsm_data.csv")
