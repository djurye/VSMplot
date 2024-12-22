import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import linregress

# Carregar dados da curva de histerese
# Substitua pelo caminho correto do arquivo .dat
data = np.loadtxt('FLAT_COPT_CO3NM_PARALELO_00001.dat')  
H = data[:, 0]  # Coluna do campo magnético (H)
M = data[:, 1]  # Coluna do momento magnético (M)

# Selecionar subconjunto para calcular regressão linear (pontos de maior valor)
# Por exemplo: considere apenas os pontos onde |H| > um limite
limite = 0.8 * max(abs(H))  # Ajuste conforme necessário
indices = np.where(abs(H) > limite)[0]
H_linear = H[indices]
M_linear = M[indices]

# Calcular a regressão linear no subconjunto selecionado
slope, intercept, _, _, _ = linregress(H_linear, M_linear)

# Remover a inclinação da curva de toda a curva M
M_corrigido = M - (slope * H)

# Plotar os resultados
plt.figure(figsize=(10, 6))
plt.plot(H, M, label='Curva Original', color='blue', alpha=0.6)
plt.plot(H, M_corrigido, label='Curva Corrigida', color='red', linewidth=2)
plt.xlabel('Campo Magnético (H)')
plt.ylabel('Momento Magnético (M)')
plt.title('Correção da Inclinação da Curva de Histerese')
plt.legend()
plt.grid(True)
plt.show()

# Opcional: salvar a curva corrigida em um novo arquivo
np.savetxt('curva_corrigida.dat', np.column_stack((H, M_corrigido)), 
           header='H M_corrigido', comments='', fmt='%.6e')
