# História de usuários
- Eu como usuário preciso eliminar pontos de ruídos da minha curva
- Eu como usuário preciso acertar a inclinação da minha curva
- Eu como usuário gostaria de obter gráficos de forma automática quando inserir meus dados
- Eu como técnico gostaria de ter visual das técnicas de manipulação dos dados
- Eu como usuário gostaria de poder selecionar varias curvas e criar o gráfico com elas
- Eu como usuário gostaria de definir quais operações de manipulação dos dados quero fazer para corrigir as curvas
...adicionar mais idéias 

# Tarefas
## versão 1
- aplicar outro método de remoção da inclinação
    > encontrar o ponto mais alto da curva (maior), definir o intervalo entre o ponto mais alto a´te o final da curva (intervalo), fazer a regressão a partir do ponto: maior + 0,2 * intervalo (ajustar o coeficiente)
* ok - integrar o visual antigo (vsm_curve_gui) de plotagem de gráfico ao novo modelo(vsm_curve_gui_new_functions)para que seja exibido o processo de manipulação dos dados
    > no primeiro gráfico obtido, seria interessante exibir a curva de regressão linear de cada curva, quando produzir um gráfico utilizável  esse paramentreos devem ser ocultos, exibindo apenas as curvas de interesse
* ok - organizar os frames de vsm_curve_gui_new_functions em seus respectivos arquivos
    > para melhor elegibilidade do código, separar cada frame em file_frame(referente ao frame de manipulaão de arquivos), graph_frame(referente ao frame que contém o grafico), main_frame (referente a janela principal)
- implementar lógica para index.py
    > é necessário criar o código desse arquivo para que seja o arquivo principal para execução do programa
* ok - botões proximo/antrerior podem fazer loop
- criar executável
    > criar um executável para que seja possível abrir o programa sem necessidade de utilizar um interpletador python 
- fazer documnetação no README.md
    > documentar como fazer a instalção, como utilizar o programa, como contribuir...

## versão 1.1
- desenvolver solução para remoção de ruídos
    > pesquisar métodos para remção de ruído em curvas e aplicar no programa
- desenvlver solução para fechamento de curva
    > em alguns casos a curva pode ficar aberta, pesquisar como é possível manipular os dados ara que a curva fique fechada
- adicionar um menu onde é possível selecionar quais os tratamentos de dados serão realizados em cada arquivo
    > nem todos os arquivos será necessário aplicar todas as operações, então é interessante desenvolver dentro do files_frames caixas de seleção individuais ou todos para marcar as operações que devem ser realizadas 

# Observações
os arquivos: file, graph, main_frames deverão ser utilizados quando organizar os frames de vsm_curve_gui
seria interessante desenvolver testes unitários




