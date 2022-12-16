# SCANPLOT - Um sistema de plotagem simples para o SCANTEC

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/cfbastarz/SCANPLOT/master)

O SCANPLOT é um módulo escrito em linguagem Python preparado para ler e plotar as tabelas com as estatísticas do Sistema Comunitário de Avaliação de modelos Numéricos de Tempo e Clima (SCANTEC). O seu uso pode ser feito por meio da linha de comando ou através do Jupyter Notebook. O SCANPLOT transforma as tabelas do SCANTEC em dataframes do Pandas e pode ser facilmente extendido a partir da introdução de funções para a plotagem destes dataframes na forma como o usuário precisar.

A versão V1.1.0a do `scanplot` está organizada da seguinte forma:

1. `core_scanplot.py`: contém funções relacionadas com a leitura dos arquivos de configuração do SCANTEC;
2. `data_structures.py`: contém funções relacionadas com as estruturas de dados utilizadas pelo SCANPLOT;
3. `aux_functions.py`: contém funções auxiliares utilizadas em outras partes do módulo;
4. `plot_functions.py`: contém funções relacionadas com a plotagem das estruturas de dados do SCANPLOT;
5. `gui_functions.py`: contém funções relacionadas com as widgets do Jupyter Notebook (parcialmente implementado).

As principais funções do módulo são as seguintes:

1. `read_namelists`: esta função lê os arquivos de namelist e definições dos modelos do SCANTEC;
2. `get_dataframe`: esta função transforma uma ou mais tabelas em dataframes do Pandas, acessíveis por meio de um dicionário;
3. `plot_lines`: esta função plota gráficos de linhas a partir dos dataframes;
3. `plot_lines_tStudent`: esta função plota gráficos de linhas a partir dos dataframes, acompanhadas com o teste de significância t-Student;
4. `plot_scorecard`: esta função plota um scorecard a partir dos dataframes;
5. `plot_dTaylor`: esta função plota um diagrama de Taylor a partir dos dataframes.

A documentação do SCANPLOT pode ser encontrada em https://gam-dimnt-cptec.github.io/SCANPLOT/.

<a href="https://creativecommons.org/licenses/by-nc-sa/4.0/legalcode" target="_blank"><img src="https://mirrors.creativecommons.org/presskit/buttons/88x31/png/by-nc-sa.png" alt="CC-BY-NC-SA" width="100"/></a>
