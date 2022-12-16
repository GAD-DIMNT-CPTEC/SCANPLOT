# SCANPLOT - Um sistema de plotagem simples para o SCANTEC
# CC-BY-NC-SA-4.0 2022 INPE

"""
scanplot
========

    Este módulo contém funções associadas à leitura das informações do namelist do SCANTEC
    e à plotagem das tabelas do SCANTEC (ACOR, RMSE, MEAN e VIES).

Funções
-------
    read_nemalists      : lê os namelists e arquivos de definições do SCANTEC;
    get_dataframe       : transforma as tabelas do SCANTEC em dataframes;
    get_dataset         : transforma os campos com a distribuição espacial das estatísticas do SCANTEC datasets;
    plot_lines          : plota gráficos de linha com os dataframes das tabelas do SCANTEC;
    plot_lines_tStudent : plota gráficos de linha com os dataframes das tabelas do SCANTEC;
    plot_scorecard      : resume as informações dos dataframes com as tabelas do SCANTEC em scorecards;
    plot_dTaylor        : plota diagramas de Taylor a partir de dois experimentos utilizando
                          os dataframes com as tabelas do SCANTEC.
"""

from core_scanplot import read_namelists, dummy
from data_structures import get_dataframe, get_dataset
from aux_functions import concat_tables_and_loc, df_fill_nan, calc_tStudent, isnotebook 
from plot_functions import plot_lines, plot_lines_tStudent, plot_scorecard, plot_dTaylor, plot_fields 
from gui_functions import show_interface
