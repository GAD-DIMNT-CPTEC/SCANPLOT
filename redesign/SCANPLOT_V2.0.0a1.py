#!/usr/bin/env python
# coding: utf-8

# Usar o ambiente SCANPLOT_PANEL
# @cfbastarz, Jun/2023 (carlos.bastarz@inpe.br)

import os
import io
import intake
import requests
import xarray as xr
import numpy as np
import pandas as pd
import geopandas as gpd
import seaborn as sns
import panel as pn
import param
import hvplot.xarray
import hvplot.pandas
import hvplot as hv
import holoviews as hvs
import cartopy.crs as ccrs
import cartopy.feature as cfeature

from datetime import datetime
from matplotlib import pyplot as plt

hvs.extension('bokeh')

pn.extension('katex')
pn.extension('floatpanel')
pn.extension('texteditor')
pn.extension(notifications=True)
pn.extension(sizing_mode='stretch_width')

# SCANPLOT_V2.0.0a1
# @cfbastarz, Jun/2023 (carlos.bastarz@inpe.br)


Vars = [
('VTMP:925', 'Virtual Temperature @ 925 hPa [K]'),
('VTMP:850', 'Virtual Temperature @ 850 hPa [K]'),
('VTMP:500', 'Virtual Temperature @ 500 hPa [K]'),
('VTMP:250', 'Virtual Temperature @ 250 hPa [K]'),
('VTMP:200', 'Virtual Temperature @ 200 hPa [K]'),
('VTMP:150', 'Virtual Temperature @ 150 hPa [K]'),
('VTMP:070', 'Virtual Temperature @ 70 hPa [K]'),
('VTMP:050', 'Virtual Temperature @ 50 hPa [K]'),
('TEMP:850', 'Absolute Temperature @ 850 hPa [K]'),
('TEMP:500', 'Absolute Temperature @ 500 hPa [K]'),
('TEMP:250', 'Absolute Temperature @ 250 hPa [K]'),
('TEMP:200', 'Absolute Temperature @ 200 hPa [K]'),
('TEMP:150', 'Absolute Temperature @ 150 hPa [K]'),
('TEMP:070', 'Absolute Temperature @ 70 hPa [K]'),
('TEMP:050', 'Absolute Temperature @ 50 hPa [K]'),
('PSNM:000', 'Mean Sea Level Pressure [hPa]'),
('UMES:925', 'Specific Humidity @ 925 hPa [g/Kg]'),
('UMES:850', 'Specific Humidity @ 850 hPa [g/Kg]'),
('UMES:500', 'Specific Humidity @ 500 hPa [g/Kg]'),
('UMES:250', 'Specific Humidity @ 250 hPa [g/Kg]'),
('UMES:200', 'Specific Humidity @ 200 hPa [g/Kg]'),
('UMES:150', 'Specific Humidity @ 150 hPa [g/Kg]'),
('UMES:070', 'Specific Humidity @ 70 hPa [g/Kg]'),
('UMES:050', 'Specific Humidity @ 50 hPa [g/Kg]'),
('AGPL:000', 'Inst. Precipitable Water @ 1000 hPa [Kg/m2]'),
('ZGEO:850', 'Geopotential height @ 850 hPa [gpm]'),
('ZGEO:500', 'Geopotential height @ 500 hPa [gpm]'),
('ZGEO:250', 'Geopotential height @ 250 hPa [gpm]'),
('UVEL:850', 'Zonal Wind @ 850 hPa [m/s]'),
('UVEL:500', 'Zonal Wind @ 500 hPa [m/s]'),
('UVEL:250', 'Zonal Wind @ 250 hPa [m/s]'),
('UVEL:200', 'Zonal Wind @ 200 hPa [m/s]'),
('UVEL:150', 'Zonal Wind @ 150 hPa [m/s]'),
('UVEL:070', 'Zonal Wind @ 70 hPa [m/s]'),
('UVEL:050', 'Zonal Wind @ 50 hPa [m/s]'),
('VVEL:850', 'Meridional Wind @ 850 hPa [m/s]'),
('VVEL:500', 'Meridional Wind @ 500 hPa [m/s]'),
('VVEL:250', 'Meridional Wind @ 250 hPa [m/s]'),
('VVEL:200', 'Meridional Wind @ 200 hPa [m/s]'),
('VVEL:150', 'Meridional Wind @ 150 hPa [m/s]'),
('VVEL:070', 'Meridional Wind @ 70 hPa [m/s]'),
('VVEL:050', 'Meridional Wind @ 50 hPa [m/s]'), 
]    

list_var = [ltuple[0].lower() for ltuple in Vars]

date_range = '20191115122020020100'

colormaps = ['Accent',  'Blues',  'BrBG',  'BuGn',  'BuPu',  'CMRmap',  'Dark2',  'GnBu', 
             'Greens',  'Greys',  'OrRd',  'Oranges',  'PRGn',  'Paired',  'Pastel1', 
             'Pastel2',  'PiYG',  'PuBu', 'PuBuGn',   'PuOr',  'PuRd',  'Purples', 
             'RdBu',  'RdGy',  'RdPu',  'RdYlBu',  'RdYlGn',  'Reds',  'Set1', 
             'Set2',  'Set3',  'Spectral',  'Wistia',  'YlGn', 'YlGnBu',   'YlOrBr', 
             'YlOrRd',  'afmhot',  'autumn',  'binary',  'bone',  'brg',  'bwr', 
             'cividis',  'cool', 
             'coolwarm',  'copper',  'crest',  'cubehelix',  'flag',  'flare',  
             'gist_earth',  'gist_gray',  'gist_heat',  'gist_ncar',   
             'gist_stern',  'gist_yarg',  'gnuplot', 'gnuplot2',   'gray',  'hot',  'hsv', 
             'icefire',  'inferno',  'jet',  'magma',  'mako',  'nipy_spectral',  
             'ocean',  'pink',  'plasma',  'prism',  'rainbow',  'rocket',  'seismic', 
             'spring',  'summer',  'tab10',  'tab20',  'tab20b',  'tab20c',  'terrain',  
             'turbo',  'twilight',  'twilight_shifted',  'viridis',  'vlag',  'winter']

#
# Widgets
#

# Widgets Datas (das distribuições espaciais)
datei = datetime.strptime('2019-11-15', '%Y-%m-%d')
datef = datetime.strptime('2019-11-26', '%Y-%m-%d')

date = pn.widgets.DateSlider(name='Data', start=datei, end=datef, value=datei, format='%Y-%m-%d')
#fcts = pn.widgets.IntSlider(name='Previsão (horas)', start=0, end=264, step=24, value=0)
       
# Widget de Notificações
silence = pn.widgets.Toggle(name='🔔 Silenciar Notificações', button_type='primary', button_style='outline', value=False)

read_catalog = pn.widgets.Button(name='🎲 Ler Catálogo de Dados', button_type='primary')
file_input = pn.widgets.FileInput(name='Escolher Catálogo de Dados', accept='yml', mime_type='text/yml', multiple=False)

# Widgets Série Temporal (_st)    
varlev_st = pn.widgets.Select(name='Variável', disabled=True)
reg_st = pn.widgets.Select(name='Região', disabled=True)
ref_st = pn.widgets.Select(name='Referência', disabled=True)
expt_st = pn.widgets.MultiChoice(name='Experimentos', disabled=True, solid=False)

# Widgets Scorecard (_sc)
Tstats = ['Ganho Percentual', 'Mudança Fracional']
colormap_sc = pn.widgets.Select(name='Cor do Preenchimento', value=colormaps[74], options=colormaps)
invert_colors_sc = pn.widgets.Checkbox(name='Inverter Cores', value=True)

statt_sc = pn.widgets.Select(name='Estatística', disabled=True)
tstat = pn.widgets.Select(name='Tipo', disabled=True)
reg_sc = pn.widgets.Select(name='Região', disabled=True)
ref_sc = pn.widgets.Select(name='Referência', disabled=True)
expt1 = pn.widgets.Select(name='Experimento 1', disabled=True)
expt2 = pn.widgets.Select(name='Experimento 2', disabled=True)

# Widgets Distribuição Espacial (_de) 
Fills = ['image', 'contour']
fill_de = pn.widgets.Select(name='Preenchimento', options=Fills)     
colormap_de = pn.widgets.Select(name='Cor do Preenchimento', value=colormaps[0], options=colormaps)      
invert_colors_de = pn.widgets.Checkbox(name='Inverter Cores', value=True) 
interval = pn.widgets.IntInput(name='Intervalos', value=10, step=1, start=5, end=20)     
    
state = pn.widgets.Select(name='Estatística', disabled=True)    
varlev_de = pn.widgets.Select(name='Variável', disabled=True)    
reg_de = pn.widgets.Select(name='Região', disabled=True)    
ref_de = pn.widgets.Select(name='Referência', disabled=True)       
expe_de = pn.widgets.MultiChoice(name='Experimentos', disabled=True, solid=False)    
      
# Widgets Distribuição Espacial Double (_ded) 
fill_ded = pn.widgets.Select(name='Preenchimento', value=Fills[0], options=Fills) 
colormap_ded = pn.widgets.Select(name='Cor do Preenchimento', value=colormaps[80], options=colormaps)      
invert_colors_ded = pn.widgets.Checkbox(name='Inverter Cores', value=True) 
swipe_ded = pn.widgets.Checkbox(name='Juntar Figuras', value=False) 
show_diff_ded = pn.widgets.Checkbox(name='Mostrar Diferença', value=False) 

varlev_ded = pn.widgets.Select(name='Variável', disabled=True)    
reg_ded = pn.widgets.Select(name='Região', disabled=True)    
ref_ded = pn.widgets.Select(name='Referência', disabled=True)    
expe_ded = pn.widgets.MultiChoice(name='Experimentos', disabled=True, solid=False)  
exp1_ded = pn.widgets.Select(name='Experimento 1', disabled=True)
exp2_ded = pn.widgets.Select(name='Experimento 2', disabled=True)

# Variável lógica para determinar se o arquivo de catálogo já foi lido (True) ou não (False)
loaded = pn.widgets.Checkbox(name='Catálogo Carregado', value=False, disabled=True)

## Botão da paleta de cores
show_color_pallete = pn.widgets.Button(name='🎨 Paletas de Cores...', button_type='default')

# Função callback do botão 'Ler Catálogo de Dados' - nela, são definidas todas as widgets
def readCatalog(event):
    global data_catalog
    
    fname = os.path.join(os.getcwd(),'catalog.yml')
    
    try:
        
        data_catalog = intake.open_catalog(os.path.join(os.getcwd(), 'catalog.yml'))

        if silence.value is False: pn.state.notifications.success('Arquivo catalog.yml carregado com sucesso!', duration=5000)
        
        loaded.value = True
        
        Regs = []
        StatsE = []
        StatsT = []
        Exps = []
        Refs = []
        Types = []        
        
        # Para cada entrada no arquivo de catálogo, organiza os atributos
        for source in data_catalog:
            attrs = source.split('-')
            Regs.append(attrs[1])
            if attrs[5] == 'field':
                StatsE.append(attrs[2].upper())
            else:
                StatsT.append(attrs[2].upper())
                Exps.append(attrs[3].upper())
                Refs.append(attrs[4])
            Types.append(attrs[5])

        # Widgets Série Temporal (_st)
        varlev_st.options = [i[0] for i in Vars]
        reg_st.options = [*set(Regs)]
        ref_st.options = [*set(Refs)]
        expt_st.options = [*set(Exps)]
        expt_st.value = [[*set(Exps)][0]]
        
        varlev_st.disabled = reg_st.disabled = ref_st.disabled = expt_st.disabled = False

        # Widgets Scorecard (_sc)
        statt_sc.options = [*set(StatsT)]
        tstat.options = [*set(Tstats)]
        reg_sc.options = [*set(Regs)]
        ref_sc.options = [*set(Refs)]
        expt1.options = [*set(Exps)]
        expt1.value = [*set(Exps)][0]
        expt2.options = [*set(Exps)]
        expt2.value = [*set(Exps)][1]
        
        colormap_sc.disabled = invert_colors_sc.disabled = statt_sc.disabled = tstat.disabled = False
        reg_sc.disabled = ref_sc.disabled = expt1.disabled = expt2.disabled = False

        # Widgets Distribuição Espacial (_de) 
        state.options = [*set(StatsE)]
        varlev_de.options = [i[0] for i in Vars]
        reg_de.options = [*set(Regs)]
        ref_de.options = [*set(Refs)]
        expe_de.options = [*set(Exps)]
        expe_de.value = [[*set(Exps)][0]]
        
        fill_de.disabled = state.disabled = varlev_de.disabled = reg_de.disabled = ref_de.disabled = False    
        colormap_de.disabled = invert_colors_de.disabled = interval.disabled = expe_de.disabled = False
      
        # Widgets Distribuição Espacial Double (_ded) 
        varlev_ded.options = [i[0] for i in Vars]
        reg_ded.options = [*set(Regs)]
        ref_ded.options = [*set(Refs)]
        expe_ded.options = [*set(Exps)]
        expe_ded.value = [[*set(Exps)][0]]
        exp1_ded.options = [*set(Exps)]
        exp1_ded.value = [*set(Exps)][0]
        exp2_ded.options = [*set(Exps)]
        exp2_ded.value = [*set(Exps)][1]
        
        fill_ded.disabled = varlev_ded.disabled = reg_ded.disabled = ref_ded.disabled = colormap_ded.disabled = False      
        invert_colors_ded.disabled = expe_ded.disabled = swipe_ded.disabled = show_diff_ded.disabled = exp1_ded.disabled = False
        exp2_ded.disabled = False      
        
        read_catalog.visible = False
        
    except IOError:
        
        if silence.value is False: pn.state.notifications.error('Arquivo ' + fname + ' não existe!', duration=5000) 
    
read_catalog.on_click(readCatalog)     

winpt = pn.Column(file_input, read_catalog, loaded)    
wst = pn.Column(varlev_st, reg_st, ref_st, expt_st)
wsc = pn.Column(statt_sc, tstat, reg_sc, ref_sc, expt1, expt2, pn.Column(colormap_sc, show_color_pallete), invert_colors_sc)
wde = pn.Column(fill_de, state, varlev_de, reg_de, ref_de, colormap_de, invert_colors_de, interval, expe_de)
#wded = pn.Column(fill_ded, varlev_ded, reg_ded, ref_ded, colormap_ded, invert_colors_ded, expe_ded, swipe_ded, show_diff_ded, exp1_ded, exp2_ded)
wded = pn.Column(state, varlev_ded, reg_ded, ref_ded, exp1_ded, exp2_ded, date, fill_ded, pn.Column(colormap_ded, show_color_pallete), invert_colors_ded, interval, swipe_ded, show_diff_ded)

@pn.depends(file_input, watch=True)
def save(value):
    if file_input.value is not None:
        file_input.save(os.path.join(os.getcwd(),'catalog.yml'))
        if silence.value is False: pn.state.notifications.success('Arquivo catalog.yml salvo com sucesso!', duration=5000)
    else:
        if silence.value is False: pn.state.notifications.warning('Nenhum arquivo para salvar.', duration=5000)

#
# Funções de plotagem
#

def get_min_max_ds(ds):
    return ds.compute().min().item(), ds.compute().max().item()

def get_df(reg, exp, stat, ref, varlev):
    kname = 'scantec-' + reg + '-' + stat + '-' + exp.lower() + '-' + ref + '-table'
    if data_catalog is not None:
        df = data_catalog[kname].read()
        df.set_index('Unnamed: 0', inplace=True)
        df.index.name = '' 
        return df

@pn.depends(varlev_st, reg_st, ref_st, expt_st, loaded)
def plotCurves(varlev_st, reg_st, ref_st, expt_st, loaded):
    
    if loaded and varlev_st and reg_st and ref_st and expt_st:       
        
        for i in Vars:
            if i[0] == varlev_st:
                nexp_ext = i[1]

        varlev_st = varlev_st.lower()

        height=500    
        
        for count, i in enumerate(expt_st):
            if count == 0:
                exp = expt_st[count] 
            
                df_vies = get_df(reg_st, exp, 'vies', ref_st, varlev_st)
            
                if df_vies is not None:
            
                    ax_vies = df_vies.hvplot.line(x='%Previsao',
                                          y=varlev_st,
                                          xlabel='Horas',
                                          ylabel='VIES',
                                          shared_axes=False,
                                          grid=True,
                                          line_width=3,
                                          label=str(exp),
                                          fontsize={'ylabel': '12px', 'ticks': 10},
                                          responsive=True,
                                          height=height,
                                          title='VIES' + ' - ' + str(nexp_ext))
            
                    df_rmse = get_df(reg_st, exp, 'rmse', ref_st, varlev_st)
        
                    ax_rmse = df_rmse.hvplot.line(x='%Previsao',
                                          y=varlev_st,
                                          xlabel='Horas',
                                          ylabel='RMSE',
                                          shared_axes=False,
                                          grid=True,
                                          line_width=3,
                                          label=str(exp),
                                          fontsize={'ylabel': '12px', 'ticks': 10},
                                          responsive=True,
                                          height=height,
                                          title='RMSE' + ' - ' + str(nexp_ext))            
                        
                    df_acor = get_df(reg_st, exp, 'acor', ref_st, varlev_st)
            
                    ax_acor = df_acor.hvplot.line(x='%Previsao', 
                                          y=varlev_st,
                                          xlabel='Horas',
                                          ylabel='ACOR',
                                          shared_axes=False,
                                          grid=True,
                                          line_width=3,
                                          label=str(exp),
                                          fontsize={'ylabel': '12px', 'ticks': 10},     
                                          responsive=True,
                                          height=height,
                                          title='ACOR' + ' - ' + str(nexp_ext))  
            
            else:
            
                exp = expt_st[count]
            
                df_vies = get_df(reg_st, exp, 'vies', ref_st, varlev_st)
            
                if df_vies is not None:
            
                    ax_vies *= df_vies.hvplot.line(x='%Previsao', 
                                           y=varlev_st, 
                                           xlabel='Horas', 
                                           ylabel='VIES',
                                           shared_axes=False,
                                           grid=True,
                                           line_width=3,
                                           label=str(exp),  
                                           fontsize={'ylabel': '12px', 'ticks': 10},
                                           responsive=True,
                                           height=height,
                                           title='VIES' + ' - ' + str(nexp_ext))
            
                    df_rmse = get_df(reg_st, exp, 'rmse', ref_st, varlev_st)
            
                    ax_rmse *= df_rmse.hvplot.line(x='%Previsao',
                                           y=varlev_st,
                                           xlabel='Horas',
                                           ylabel='RMSE', 
                                           shared_axes=False,
                                           grid=True,
                                           line_width=3,
                                           label=str(exp), 
                                           fontsize={'ylabel': '12px', 'ticks': 10},
                                           responsive=True,
                                           height=height,
                                           title='RMSE' + ' - ' + str(nexp_ext))       

                    df_acor = get_df(reg_st, exp, 'acor', ref_st, varlev_st)
            
                    ax_acor *= df_acor.hvplot.line(x='%Previsao',
                                           y=varlev_st,
                                           xlabel='Horas',
                                           ylabel='ACOR', 
                                           shared_axes=False,
                                           grid=True,
                                           line_width=3,
                                           label=str(exp),      
                                           fontsize={'ylabel': '12px', 'ticks': 10},
                                           responsive=True,
                                           height=height,
                                           title='ACOR' + ' - ' + str(nexp_ext))             
       
            if ax_vies is not None:
                ax_vies *= hvs.HLine(0).opts(line_width=1, shared_axes=False, responsive=True, height=height, line_color='black', line_dash='dashed')
                ax_rmse *= hvs.HLine(0).opts(line_width=1, shared_axes=False, responsive=True, height=height, line_color='black', line_dash='dashed')
                ax_acor *= hvs.HLine(0.6).opts(line_width=1, shared_axes=False, responsive=True, height=height, line_color='black', line_dash='dashed')    
            

        if ax_vies is not None:
            ax_vies.opts(axiswise=True, legend_position='bottom_left')
            ax_rmse.opts(axiswise=True, legend_position='top_left')
            ax_acor.opts(axiswise=True, legend_position='bottom_left')
    
        layout = hvs.Layout(ax_vies + ax_rmse + ax_acor).cols(3)
    
    else:
        
        layout = pn.Column(
                    pn.pane.Markdown("""
                    # Série Temporal
                    
                    A avaliação por meio de série temporal permite verificar o comportamento de parâmetros (variáveis) do modelo ao longo do tempo, seja por meio da verificação dos erros aleatórios, sistemáticos e habilidade de previsão.
                    """),
                    pn.pane.Alert('⛔ **Atenção:** Nada para mostrar! Para começar, selecione um catálogo de dados ou aguarde a execução da função de plotagem.', alert_type='danger')
                )
    
    return layout
    
@pn.depends(statt_sc, tstat, reg_sc, ref_sc, expt1, expt2, colormap_sc, invert_colors_sc, loaded)    
def plotScorecard(statt_sc, tstat, reg_sc, ref_sc, expt1, expt2, colormap_sc, invert_colors_sc, loaded):
    
    if loaded and statt_sc and tstat and reg_sc and ref_sc and expt1 and expt2 and colormap_sc and invert_colors_sc:   
    
        dfs = globals()['data_catalog']
    
        kname1 = 'scantec-' + reg_sc + '-' + statt_sc.lower() + '-' + expt1.lower() + '-' + ref_sc + '-table'
        kname2 = 'scantec-' + reg_sc + '-' + statt_sc.lower() + '-' + expt2.lower() + '-' + ref_sc + '-table'
    
        df1 = dfs[kname1].read()
        df2 = dfs[kname2].read()
        
        df1.set_index('Unnamed: 0', inplace=True)
        df1.index.name = ''   

        df2.set_index('Unnamed: 0', inplace=True)
        df2.index.name = ''      
        
        p_table1 = pd.pivot_table(df1, index='%Previsao', values=list_var)
        p_table2 = pd.pivot_table(df2, index='%Previsao', values=list_var)
 
        if invert_colors_sc == True:
            cmap = colormap_sc + '_r'
        else:
            cmap = colormap_sc
    
        if tstat == 'Ganho Percentual':
            # Porcentagem de ganho
            if statt_sc == 'ACOR':
                #score_table = ((p_table2[1:].T - p_table1[1:].T) / (1.0 - p_table1[1:].T)) * 100
                score_table = ((p_table2.T - p_table1.T) / (1.0 - p_table1.T)) * 100
            elif statt_sc == 'RMSE' or statt_sc == 'VIES':
                #score_table = ((p_table2[1:].T - p_table1[1:].T) / (0.0 - p_table1[1:].T)) * 100
                score_table = ((p_table2.T - p_table1.T) / (0.0 - p_table1.T)) * 100
        elif tstat == 'Mudança Fracional':
            # Mudança fracional
            #score_table = (1.0 - (p_table2[1:].T / p_table1[1:].T))
            score_table = (1.0 - (p_table2.T / p_table1.T))
 
        if score_table.isnull().values.any():

            #print(score_table)

            # Tentativa de substituir os NaN - que aparecem quando vies e rmse são iguais a zero
            score_table = score_table.fillna(0.0000001)

            # Tentativa de substituir valores -inf por um número não muito grande
            score_table.replace([np.inf, -np.inf], 1000000, inplace=True)

            if silence.value is False: pn.state.notifications.info('Valores como NaN ou Inf podem ter sido substituídos por outros valores.', duration=5000) 

        ## Figura
        plt.figure(figsize = (9,6))

        sns.set(style='whitegrid', font_scale=0.450)
        sns.set_context(rc={'xtick.major.size':  1.5,  'ytick.major.size': 1.5,
                            'xtick.major.pad':   0.05,  'ytick.major.pad': 0.05,
                            'xtick.major.width': 0.5, 'ytick.major.width': 0.5,
                            'xtick.minor.size':  1.5,  'ytick.minor.size': 1.5,
                            'xtick.minor.pad':   0.05,  'ytick.minor.pad': 0.05,
                            'xtick.minor.width': 0.5, 'ytick.minor.width': 0.5})

        if tstat == 'Ganho Percentual':
            ax = sns.heatmap(score_table, annot=True, fmt='.3f', cmap=cmap, 
                             vmin=-100, vmax=100, center=0, linewidths=0.25, square=False,
                             cbar_kws={'shrink': 1.0, 
                                       'ticks': np.arange(-100,110,10),
                                       'pad': 0.01,
                                       'orientation': 'vertical'})

            cbar = ax.collections[0].colorbar
            cbar.set_ticks([-100, -50, 0, 50, 100])
            cbar.set_ticklabels(['pior', '-50%', '0', '50%', 'melhor'])
            cbar.ax.tick_params(labelsize=7)    

            plt.title('Ganho ' + str(statt_sc) + ' (%) - ' + expt1 + ' Vs. ' + expt2, fontsize=8)

        elif tstat == 'Mudança Fracional':
            ax = sns.heatmap(score_table, annot=True, fmt='.3f', cmap=cmap, 
                             vmin=-1, vmax=1, center=0, linewidths=0.25, square=False,
                             cbar_kws={'shrink': 1.0, 
                                       'ticks': np.arange(-1,2,1),
                                       'pad': 0.01,
                                       'orientation': 'vertical'})

            cbar = ax.collections[0].colorbar
            cbar.set_ticks([-1, -0.5, 0, 0.5, 1])
            cbar.set_ticklabels(['pior', '-0.5', '0', '0.5', 'melhor'])
            cbar.ax.tick_params(labelsize=7)    

            plt.title('Mudança Fracional ' + str(statt_sc) + " - " + expt1 + ' Vs. ' + expt2, fontsize=8)

        plt.xlabel('Horas de Integração')
        plt.yticks(fontsize=7)
        #plt.xticks(rotation=90, fontsize=6)    
        plt.xticks(fontsize=7)  
        plt.tight_layout()        

        layout = ax.get_figure()

        plt.close()

    else:
        
        layout = pn.Column(
                    pn.pane.Markdown("""
                    # Scorecard
                    
                    Para uma variável alpha (e.g., pressão, temperatura, umidade, componentes do vento etc.), podem ser calculadas duas métricas que permitem quantificar a variação relativa entre dois experimentos avaliados pelo SCANTEC. As métricas aplicadas são o Ganho Percentual e a Mudança Fracional* e ambas podem ser calculadas com base nas tabelas de estatisticas do SCANTEC. Estas métricas podem ser utilizadas quando se quiser ter uma visão imediata sobre as melhorias obtidas entre duas versões de um modelo ou entre dois experimentos de um mesmo modelo.
                    """),
                    pn.pane.Alert('⛔ **Atenção:** Nada para mostrar! Para começar, selecione um catálogo de dados ou aguarde a execução da função de plotagem.', alert_type='danger')
                )        
        
    return layout

@pn.depends(state, varlev_de, reg_de, ref_de, date, colormap_de, invert_colors_de, interval, expe_de, fill_de)
def plotFields(state, varlev_de, reg_de, ref_de, date, colormap_de, invert_colors_de, interval, expe_de, fill_de):
    
    date = str(date) + ' 12:00' # consertar...

    var = varlev_de.replace(':', '').lower()
    
    for i in Vars:
        if i[0] == varlev_de:
            nexp_ext = i[1]
    
    if invert_colors_de == True:
        cmap = colormap_de + '_r'
    else:
        cmap = colormap_de
    
    if reg_de == 'as':
        data_aspect=1
        frame_height=700
    elif (reg_de == 'hn') or (reg_de == 'hs'):
        data_aspect=1
        frame_height=225        
    elif reg_de == 'tr':
        data_aspect=1
        frame_height=150         
    elif reg_de == 'gl': 
        data_aspect=1
        frame_height=590
  
    for count, i in enumerate(expe_de):
        if count == 0:
            exp = expe_de[count]
            kname = 'scantec-' + reg_de + '-' + state.lower() + '-' + exp.lower() + '-' + ref_de + '-field'
            if data_catalog is not None:
                ds = data_catalog[kname].to_dask()
            
            vmin, vmax = get_min_max_ds(ds[var])
                       
            if fill_de == 'image':
            
                ax = ds.sel(time=date).hvplot.image(x='lon',
                                                    y='lat',
                                                    z=var,
                                                    data_aspect=data_aspect,
                                                    frame_height=frame_height, 
                                                    cmap=cmap, 
                                                    projection=ccrs.PlateCarree(), 
                                                    coastline=True,
                                                    rasterize=True,
                                                    clim=(vmin,vmax),
                                                    title=str(state) + ' - ' + str(nexp_ext) + ' (' + str(date) + ')')    
                
            elif fill_de == 'contour':
                
                ax = ds.sel(time=date).hvplot.contour(x='lon',
                                                      y='lat',
                                                      z=var,
                                                      data_aspect=data_aspect,
                                                      frame_height=frame_height, 
                                                      cmap=cmap, 
                                                      projection=ccrs.PlateCarree(), 
                                                      coastline=True,
                                                      rasterize=True,
                                                      clim=(vmin,vmax),
                                                      levels=interval,
                                                      line_width=2,
                                                      title=str(state) + ' - ' + str(nexp_ext) + ' (' + str(date) + ')')  
             
        else:  
            
            ax *= ds.sel(time=date).hvplot.contour(x='lon',
                                                   y='lat',
                                                   z=var,
                                                   data_aspect=data_aspect,
                                                   frame_height=frame_height, 
                                                   cmap=cmap, 
                                                   projection=ccrs.PlateCarree(), 
                                                   coastline=True,
                                                   clim=(vmin,vmax),
                                                   colorbar=True,
                                                   levels=interval,
                                                   line_width=4,
                                                   line_dash='dashed',
                                                   title=str(state) + ' - ' + str(nexp_ext) + ' (' + str(date) + ')') 
   
    return ax

@pn.depends(state, varlev_ded, reg_ded, ref_ded, date, colormap_ded, invert_colors_ded, interval, fill_ded, swipe_ded, show_diff_ded, exp1_ded, exp2_ded)
def plotFieldsDouble(state, varlev_ded, reg_ded, ref_ded, date, colormap_ded, invert_colors_ded, interval, fill_ded, swipe_ded, show_diff_ded, exp1_ded, exp2_ded):
    
    if loaded and state and varlev_ded and reg_ded and ref_ded and date and colormap_ded and interval and fill_ded and exp1_ded and exp2_ded:
    
        datefmt = str(date) + ' 12:00' # consertar...

        var = varlev_ded.replace(':', '').lower()

        for i in Vars:
            if i[0] == varlev_ded:
                nexp_ext = i[1]

        if invert_colors_ded == True:
            cmap = colormap_ded + '_r'
        else:
            cmap = colormap_ded

        if reg_ded == 'as':
            data_aspect=1
            frame_height=800
        elif (reg_ded == 'hn') or (reg_ded == 'hs'):
            data_aspect=1
            frame_height=235        
        elif reg_ded == 'tr':
            data_aspect=1
            frame_height=155         
        elif reg_ded == 'gl': 
            data_aspect=1
            frame_height=340
            frame_height=390

        exp1 = exp1_ded
        kname1 = 'scantec-' + reg_ded + '-' + state.lower() + '-' + exp1.lower() + '-' + ref_ded + '-field'
        if data_catalog is not None:
            ds1 = data_catalog[kname1].to_dask()

        exp2 = exp2_ded
        kname2 = 'scantec-' + reg_ded + '-' + state.lower() + '-' + exp2.lower() + '-' + ref_ded + '-field'
        if data_catalog is not None:
            ds2 = data_catalog[kname2].to_dask()

        #vmin, vmax = get_min_max_ds(ds1[var])

        if show_diff_ded:

            #ds_diff = ds1[var].sel(time=datefmt) - ds2[var].sel(time=datefmt)
            ds_diff = ds1[var].isel(time=0) - ds2[var].isel(time=0)

            vmin, vmax = get_min_max_ds(ds_diff)

            if fill_ded == 'image':

                ax1 = ds1.sel(time=datefmt).hvplot.image(x='lon',
                                                      y='lat',
                                                      z=var,
                                                      data_aspect=data_aspect,
                                                      frame_height=frame_height, 
                                                      #frame_width=650,
                                                      cmap=cmap, 
                                                      projection=ccrs.PlateCarree(), 
                                                      coastline=True,
                                                      rasterize=True,
                                                      #datashade=True,
                                                      colorbar=True,
                                                      #features=['borders', 'coastline', 'lakes', 'land', 'ocean', 'rivers', 'states'],   
                                                      clim=(vmin,vmax),
                                                      title=str(state) + ' - ' + str(exp1) + ' - ' + str(nexp_ext) + ' (' + str(datefmt) + ')')    

                ax2 = ds2.sel(time=datefmt).hvplot.image(x='lon',
                                                      y='lat',
                                                      z=var,
                                                      data_aspect=data_aspect,
                                                      frame_height=frame_height, 
                                                      #frame_width=650,
                                                      cmap=cmap, 
                                                      projection=ccrs.PlateCarree(), 
                                                      coastline=True,
                                                      rasterize=True,
                                                      #features=['borders', 'coastline', 'lakes', 'land', 'ocean', 'rivers', 'states'],
                                                      #datashade=True,  
                                                      colorbar=True,   
                                                      clim=(vmin,vmax),
                                                      title=str(state) + ' - ' + str(exp2) + ' - ' + str(nexp_ext) + ' (' + str(datefmt) + ')')         

                axd = (ds1.sel(time=datefmt) - ds2.sel(time=datefmt)).hvplot.image(x='lon',
                                                                                  y='lat',
                                                                                  z=var,
                                                                                  data_aspect=data_aspect,
                                                                                  frame_height=frame_height, 
                                                                                  #frame_width=650,
                                                                                  cmap=cmap, 
                                                                                  projection=ccrs.PlateCarree(), 
                                                                                  coastline=True,
                                                                                  rasterize=True,
                                                                                  #features=['borders', 'coastline', 'lakes', 'land', 'ocean', 'rivers', 'states'], 
                                                                                  #datashade=True,
                                                                                  colorbar=True,
                                                                                  clim=(vmin,vmax),
                                                                                  title=str(state) + ' - ' + 'Dif. (' + str(exp1) + '-' + str(exp2) + ') - ' + str(nexp_ext) + ' (' + str(datefmt) + ')')    

            elif fill_ded == 'contour':

                ax1 = ds1.sel(time=datefmt).hvplot.contour(x='lon',
                                                        y='lat',
                                                        z=var,
                                                        data_aspect=data_aspect,
                                                        frame_height=frame_height, 
                                                        #frame_width=650,
                                                        cmap=cmap, 
                                                        projection=ccrs.PlateCarree(), 
                                                        coastline=True,
                                                        rasterize=True,
                                                        #features=['borders', 'coastline', 'lakes', 'land', 'ocean', 'rivers', 'states'],
                                                        clim=(vmin,vmax),
                                                        levels=interval,
                                                        line_width=1,
                                                        title=str(state) + ' - ' + str(exp1) + ' - ' + str(nexp_ext) + ' (' + str(datefmt) + ')')    

                ax2 = ds2.sel(time=datefmt).hvplot.contour(x='lon',
                                                        y='lat',
                                                        z=var,
                                                        data_aspect=data_aspect,
                                                        frame_height=frame_height, 
                                                        #frame_width=650,
                                                        cmap=cmap, 
                                                        projection=ccrs.PlateCarree(), 
                                                        coastline=True,
                                                        rasterize=True,
                                                        #features=['borders', 'coastline', 'lakes', 'land', 'ocean', 'rivers', 'states'],
                                                        clim=(vmin,vmax),
                                                        levels=interval,
                                                        line_width=1,
                                                        title=str(state) + ' - ' + str(exp2) + ' - ' + str(nexp_ext) + ' (' + str(datefmt) + ')')                  

                axd = (ds1.sel(time=datefmt) - ds2.sel(time=datefmt)).hvplot.contour(x='lon',
                                                                                    y='lat',
                                                                                    z=var,
                                                                                    data_aspect=data_aspect,
                                                                                    frame_height=frame_height, 
                                                                                    #frame_width=650,
                                                                                    cmap=cmap, 
                                                                                    projection=ccrs.PlateCarree(), 
                                                                                    coastline=True,
                                                                                    rasterize=True,
                                                                                    #features=['borders', 'coastline', 'lakes', 'land', 'ocean', 'rivers', 'states'],
                                                                                    #clim=(vmin,vmax),
                                                                                    levels=interval,
                                                                                    line_width=1,
                                                                                    title=str(state) + ' - ' + str(exp1) + ' - ' + str(nexp_ext) + ' (' + str(datefmt) + ')')          
        else:

            vmin, vmax = get_min_max_ds(ds1[var])

            if fill_ded == 'image':

                ax1 = ds1.sel(time=datefmt).hvplot.image(x='lon',
                                                      y='lat',
                                                      z=var,
                                                      data_aspect=data_aspect,
                                                      frame_height=frame_height, 
                                                      #frame_width=650,
                                                      cmap=cmap, 
                                                      projection=ccrs.PlateCarree(), 
                                                      coastline=True,
                                                      rasterize=True,
                                                      #datashade=True,
                                                      colorbar=True,
                                                      #features=['borders', 'coastline', 'lakes', 'land', 'ocean', 'rivers', 'states'],   
                                                      clim=(vmin,vmax),
                                                      title=str(state) + ' - ' + str(exp1) + ' - ' + str(nexp_ext) + ' (' + str(datefmt) + ')')    

                ax2 = ds2.sel(time=datefmt).hvplot.image(x='lon',
                                                      y='lat',
                                                      z=var,
                                                      data_aspect=data_aspect,
                                                      frame_height=frame_height, 
                                                      #frame_width=650,
                                                      cmap=cmap, 
                                                      projection=ccrs.PlateCarree(), 
                                                      coastline=True,
                                                      rasterize=True,
                                                      #features=['borders', 'coastline', 'lakes', 'land', 'ocean', 'rivers', 'states'],
                                                      #datashade=True,  
                                                      colorbar=True,   
                                                      clim=(vmin,vmax),
                                                      title=str(state) + ' - ' + str(exp2) + ' - ' + str(nexp_ext) + ' (' + str(datefmt) + ')')       

            elif fill_ded == 'contour':

                ax1 = ds1.sel(time=datefmt).hvplot.contour(x='lon',
                                                        y='lat',
                                                        z=var,
                                                        data_aspect=data_aspect,
                                                        frame_height=frame_height, 
                                                        #frame_width=650,
                                                        cmap=cmap, 
                                                        projection=ccrs.PlateCarree(), 
                                                        coastline=True,
                                                        rasterize=True,
                                                        #features=['borders', 'coastline', 'lakes', 'land', 'ocean', 'rivers', 'states'],
                                                        clim=(vmin,vmax),
                                                        levels=interval,
                                                        line_width=1,
                                                        title=str(state) + ' - ' + str(exp1) + ' - ' + str(nexp_ext) + ' (' + str(datefmt) + ')')    

                ax2 = ds2.sel(time=datefmt).hvplot.contour(x='lon',
                                                        y='lat',
                                                        z=var,
                                                        data_aspect=data_aspect,
                                                        frame_height=frame_height, 
                                                        #frame_width=650,
                                                        cmap=cmap, 
                                                        projection=ccrs.PlateCarree(), 
                                                        coastline=True,
                                                        rasterize=True,
                                                        #features=['borders', 'coastline', 'lakes', 'land', 'ocean', 'rivers', 'states'],
                                                        clim=(vmin,vmax),
                                                        levels=interval,
                                                        line_width=1,
                                                        title=str(state) + ' - ' + str(exp2) + ' - ' + str(nexp_ext) + ' (' + str(datefmt) + ')')  

        if show_diff_ded:    
            #layout = pn.Column(ax1, ax2, axd, sizing_mode='stretch_width')
            layout = pn.Column(axd, sizing_mode='stretch_width')
            #if reg_ded == 'as':
            #    layout = hvs.Layout(ax1 + ax2 + axd).cols(3)
            #else:
            #    layout = hvs.Layout(ax1 + ax2 + axd).cols(1)
        else:
            if swipe_ded:
                layout = pn.Swipe(ax1, ax2, value=5)
            else:
                if reg_ded == 'as':# or reg_ded == 'gl':
                    layout = hvs.Layout(ax1 + ax2).cols(2)
                else:
                    layout = hvs.Layout(ax1 + ax2).cols(1)

        if silence.value is False: pn.state.notifications.info('As cores nos gráficos podem representar intervalos de valores diferentes.', duration=5000)

    else:
        
        layout = pn.Column(
                    pn.pane.Markdown("""
                    # Distribuição Espacial
                    
                    A avaliação por meio da distribuição espacial permite verificar o comportamento de parêmetros (variáveis) do modelo ao longo do tempo, seja por meio da verificação dos erros aleatórios, sistemáticos e habilidade de previsão.
                    """),
                    pn.pane.Alert('⛔ **Atenção:** Nada para mostrar! Para começar, selecione um catálogo de dados ou aguarde a execução da função de plotagem.', alert_type='danger')
                )          
        
    return layout
    
@pn.depends(state, varlev_de, reg_de, ref_de, date, expt1)
def plotSeriesFromField(state, varlev_de, reg_de, ref_de, date, expt1):

    var = varlev_de.replace(':', '').lower()
    
    kname = 'scantec-' + reg_de + '-' + state.lower() + '-' + expt1.lower() + '-' + ref_de + '-field'
    if data_catalog is not None:
        dsv = data_catalog['scantec-gl-rmse_exp18-ref_era5_no_clim-field'].to_dask()

    source = dsv.isel(time=0).hvplot.image(x='lon',
                                           y='lat',
                                           z=var,
                                           geo=True,
                                           projection=ccrs.PlateCarree(),
                                           title=str(state) + ' - ' + str(expt1) + ' (' + str(date) + ')')
    
    map_file = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))

    map_overlay = map_file.hvplot(geo=True, projection=ccrs.PlateCarree(), alpha=0.1)
    
    stream = hvs.streams.Tap(source=source, x=-88 + 360, y=40)
    
    def create_timeseries(x, y):
        ds_sel = dsv.sel(lon=x, lat=y, method='nearest')
        return hvs.Curve(ds_sel, ['time'], [var])
    
    target = hvs.DynamicMap(create_timeseries, streams=[stream]).opts(framewise=True, height=380, responsive=True)#, min_width=700)
    
    return pn.Row(source * map_overlay + target, sizing_mode='stretch_width')

#
# Textos
#

text_gen_info = """
# SCANPLOT

SCANPLOT - Um sistema de visualização simples para o SCANTEC.

## Experimentos:

* **EXP18**: análises e previsões do experimento com o SMNA em coordenada híbrida na resolução TQ0299L064;
* **X666**: análises e previsões do modelo BAM em coordenada híbrida na resolução TQ0666L064.

## Validade:

Os experimentos foram considerados para o período de 2023021612 a 2023030312.

## Avaliação:

O SCANTEC foi utilizado para a avaliação objetiva dos experimentos com os seguintes ajustes:

* Interpolação de todos os campos atmosféricos para a resolução 0,4 graus (lat/lon);
* Utilização das seguintes referências:
    * `ref_era5_no_clim`: utilização das reanálises do Era5 como referência e considerando a média temporal desta referência como climatologia para o cálculo do Coeficiente de Correlação de Anomalias;
    * `ref_era5_no_clim`: utilização das próprias análises dos experimentos como referência e considerando a média temporal desta referência como climatologia para o cálculo do Coeficiente de Correlação de Anomalias;
    * `ref_era5_cfsr_clim` utilização das próprias análses dos experimentos como referência e utilização da reanálise do CFSR como climatologia para o cálculo do Coeficiente de Correlação de Anomalias;
    * `ref_era5_agcm_clim` utilização das próprias análses dos experimentos como referência e utilização da climatologia do antigo MCGA para o cálculo do Coeficiente de Correlação de Anomalias. 

---

Atualizado em: 29/06/2023 ([carlos.bastarz@inpe.br](mailto:carlos.bastarz@inpe.br))
"""

#text_vies1 = """
## Viés 
#
#Para uma variável _alpha_ (e.g., pressão, temperatura, umidade, componentes do vento etc.), discretizada em uma grade de _N_ pontos (com dimensões _i_ e _j_ - longitude e latitude, respectivamente, onde _N_ = _i_ x _j_), o Viés é calculado de acordo com a equação a seguir:
#"""
#
#text_vies2 = """
#onde,
#
#* 
#* 
#* 
#"""
#
#text_rmse1 = """
## Raiz do Erro Quadrático Médio
#
#Para uma variável _alpha_ (e.g., pressão, temperatura, umidade, componentes do vento etc.), discretizada em uma grade de _N_ pontos (com dimensões _i_ e _j_ - longitude e latitude, respectivamente, onde _N_ = _i_ x _j_), a Raiz do Erro Quadrático Médio é calculada de acordo com a equação a seguir:
#"""
#
#text_rmse2 = """
#onde,
#
#* 
#* 
#* 
#"""
#
#text_acor1 = """
## Coeficiente de Correlação de Anomalias
#
#O Coeficiente de Correlação de Anomalias é calculado de acordo com a equação a seguir:
#"""
#
#text_acor2 = """
#onde,
#
#* 
#* 
#* 
#"""
#
#text_scor1 ="""
## Scorecard
#
#Para uma variável alpha (e.g., pressão, temperatura, umidade, componentes do vento etc.), podem ser calculadas duas métricas que permitem quantificar a variação relativa entre dois experimentos avaliados pelo SCANTEC. As métricas aplicadas são o Ganho Percentual e a Mudança Fracional* e ambas podem ser calculadas com base nas tabelas de estatisticas do SCANTEC. Estas métricas podem ser utilizadas quando se quiser ter uma visão imediata sobre as melhorias obtidas entre duas versões de um modelo ou entre dois experimentos de um mesmo modelo.
#
#O Ganho Percentual é definido por:
#"""
#
#text_scor2 ="""
#onde,
#
#* E1: tabelas do experimento 1;
#* E2: tabelas do experimento 2;
#* EP: experimento 'perfeito' (valor considerado quando o experimento é perfeito, ie., 0 quando Viés ou RMSE e 1 quando ACOR).
#
#A Mudança Fracional é definida por:
#"""
#
#text_scor3 ="""
#onde,
#
#* E1: tabelas do experimento 1;
#* E2: tabelas do experimento 2;
#* EP: experimento 'perfeito' (valor considerado quando o experimento é perfeito, ie., 0 quando Viés ou RMSE e 1 quando ACOR).
#
#---
#*[BAÑOS, I. H.](http://lattes.cnpq.br/6820161737155390); et al. **Impacto da Assimilação de Perfis de Refratividade do  Satélite Metop-B nas Previsões de Tempo do CPTEC/INPE Durante os Meses de Janeiro e Agosto de 2014.** Disponível em [link](https://www.scielo.br/scielo.php?script=sci_arttext&pid=S0102-77862018000100065).
#"""  
#
#eq_ganho = pn.pane.Markdown(r'$$GP(\alpha) = \frac{E2 - E1}{EP - E1} \times 100$$')
#eq_mf = pn.pane.Markdown(r'$$MF(\alpha) = 1 - \frac{E2}{E1}$$')
#eq_vies = pn.pane.Markdown(r'$$REQM(\alpha) = \frac{1}{N}\sum_{n=1}^{N}\bigg[ \frac{1}{I \cdot J}\sum_{i=1}^{I}\sum_{j=1}^{J}(\alpha_{i,j,n}^{P} - \alpha_{i,j,n}^{O})^{2} \bigg]^\frac{1}{2}$$')
#eq_rmse = pn.pane.Markdown(r'$$REQM(\alpha) = \frac{1}{N}\sum_{n=1}^{N}\bigg[ \frac{1}{I \cdot J}\sum_{i=1}^{I}\sum_{j=1}^{J}(\alpha_{i,j,n}^{P} - \alpha_{i,j,n}^{O})^{2} \bigg]^\frac{1}{2}$$')
#eq_cca = pn.pane.Markdown(r'$$CCA(\alpha) = \frac{\sum\limits_{i=1}^{I}\sum\limits_{j=1}^{J}\big[ (\alpha_{i,j}^{P} - \alpha_{i,j}^{C})\cdot(\alpha_{i,j}^{A} - \alpha_{i,j}^{C}) \big]}{\bigg \lbrace \bigg[ \sum\limits_{i=1}^{I}\sum\limits_{j=1}^{J}(\alpha_{i,j}^{P} - \alpha_{i,j}^{C})^2 \bigg] \bigg[ \sum\limits_{i=1}^{I}\sum\limits_{j=1}^{J}(\alpha_{i,j}^{A} - \alpha_{i,j}^{C})^2 \bigg] \bigg \rbrace ^\frac{1}{2}}$$')
#eq_cca = pn.pane.Markdown(r"""
#$$CCA(\alpha) = \frac{\sum_{i=1}^{I}\sum_{j=1}^{J}\big[ (\alpha_{i,j}^{P} - \alpha_{i,j}^{C})\cdot(\alpha_{i,j}^{A} - \alpha_{i,j}^{C}) \big]}{\bigg lbrace \bigg[ \sum_{i=1}^{I}\sum_{j=1}^{J}(\alpha_{i,j}^{P} - \alpha_{i,j}^{C})^2 \bigg] \bigg[ \sum_{i=1}^{I}\sum_{j=1}^{J}(\alpha_{i,j}^{A} - \alpha_{i,j}^{C})^2 \bigg] \bigg \}}
#$$
#""")

text_st = """
# Série Temporal

A avaliação por meio de série temporal permite verificar o comportamento de parâmetros (variáveis) do modelo ao longo do tempo, seja por meio da verificação dos erros aleatórios, sistemáticos e habilidade de previsão.
"""

text_sc = """
# Scorecard

A avaliação por meio de scorecards permite obter uma visão geral do comportamento de parâmetros (variáveis) do modelo ao longo do tempo.
"""

text_ded = """
# Distribuição Espacial

A avaliação por meio da distribuição espacial permite verificar o comportamento de parêmetros (variáveis) do modelo ao longo do tempo, seja por meio da verificação dos erros aleatórios, sistemáticos e habilidade de previsão.
"""

text_help = """
# Ajuda

Clique sobre as abas `Série Temporal`, `Scorecard` ou `Distribuição Espacial` para acessar as opções de plotagem e visualização das estatísticas calculadas.
Cada tipo de visualização possui opções diferentes e independentes para a realização das plotagens. Utilize as opções para fazer os ajustes necessários.
"""

scanplot_video = pn.pane.Video('https://s0.cptec.inpe.br/pesquisa/das/dist/carlos.bastarz/SCANPLOT/scanplot_video.mp4', width=800, muted=True, volume=0, loop=False)

welcomeText = pn.Column("""
# Bem-vindo!

Este é o SCANPLOT - Um sistema simples de plotagem para o SCANTEC. O SCANTEC - Sistema Comunitário de Avaliação de modelos Numéricos de Tempo E Clima, é um sistema desenvolvido
para a avaliação de modelos numéricos de previsão e clima em uso no CPTEC - Centro de Previsão de Tempo e Estudos Climáticos. O SCANPLOT foi desenvolvido para uso exclusivo com 
o SCANTEC, devido as suas particularidades de desenvolvimento e aplicação.

Para começar, clique no botão `Choose File` (Escolher Arquivo) na barra lateral à esquerda e selecione um catálogo com os dados de avaliação realizada pelo SCANTEC. Em seguida, clique nas abas acima para acessar os resultados.

Se precisar de ajuda, clique nos botões da barra lateral à esquerda ou assista o vídeo de introdução ao uso do SCANPLOT a seguir. 
""", scanplot_video)

text_fu = """
# Selecionar Catálogo

Clique no botão `Choose File` (Escolher Arquivo) na barra lateral à esquerda e selecione um catálogo com os dados de avaliação realizada pelo SCANTEC. Em seguida, clique nas abas acima para acessar os resultados.
"""

text_float_panel = """
# SCANPLOT V2.0.0a1

SCANPLOT - Um sistema de visualização simples para o SCANTEC.

---

CPTEC-INPE, 2023.
"""

#
# Layout
#

## Logos
scantec_logo = 'https://raw.githubusercontent.com/GAM-DIMNT-CPTEC/SCANPLOT/8fe1c419bcb4881a78a3b1ac83673bcd229b075d/img/logo_scantec.png'
inpe_logo = 'https://raw.githubusercontent.com/GAM-DIMNT-CPTEC/SCANPLOT/8fe1c419bcb4881a78a3b1ac83673bcd229b075d/img/logo_inpe.png'

scantec_logo_fp = pn.pane.PNG(scantec_logo, width=200)
inpe_logo = pn.pane.PNG(inpe_logo, width=200)

## Painéis flutuantes e diálogos modais
config1 = {'headerControls':{'maximize': 'remove', 'smallify': 'remove'}
         }

config2 = {'headerControls': {'maximize': 'remove'}}

float_panel = pn.layout.FloatPanel(
    pn.Tabs(('Sobre',
    pn.Row(text_float_panel, scantec_logo_fp)),
           ('Reportar Bugs', 'Encontrou um bug? Abra uma issue no [GitHub do projeto](https://github.com/GAM-DIMNT-CPTEC/SCANPLOT/issues) ou envie um email para [carlos.bastarz@inpe.br](mailto:carlos.bastarz@inpe.br).'),
           ('Contribuir', 'Quer contribuir com o desenvolvimento do SCANPLOT? Envie um email para [carlos.bastarz@inpe.br](mailto:carlos.bastarz@inpe.br).'),
           ), 
    name='SCANPLOT', 
    contained=False, 
    position='center', 
    margin=20, 
    config=config1)

## Barra de ferramentas do editor de textos
toolbar=[
  ['bold', 'italic', 'underline', 'strike'],        # toggled buttons
  ['blockquote', 'code-block'],
  [{ 'header': 1 }, { 'header': 2 }],               # custom button values
  [{ 'list': 'ordered'}, { 'list': 'bullet' }],
  [{ 'script': 'sub'}, { 'script': 'super' }],      # superscript/subscript
  [{ 'indent': '-1'}, { 'indent': '+1' }],          # outdent/indent
  [{ 'direction': 'rtl' }],                         # text direction
  [{ 'size': ['small', False, 'large', 'huge'] }],  # custom dropdown
  [{ 'header': [1, 2, 3, 4, 5, 6, False] }],
  [{ 'color': [] }, { 'background': [] }],          # dropdown with defaults from theme
  [{ 'font': [] }],
  [{ 'align': [] }],
  ['clean']                                         # remove formatting button
]

## Widget do editor de textos
editor = pn.widgets.TextEditor(placeholder='Digitar texto...', 
                               #mode='bubble',
                               toolbar=toolbar, 
                               #margin=(0, 0, 10, 0), 
                               #height=50, 
                               #width=50,
                              )

## Botão salvar do editor de textos
editor_save_btn = pn.widgets.Button(name='💾 Salvar', button_type='success')

## Painel flutuante do editor de textos
text_editor = pn.layout.FloatPanel(pn.Column(editor, pn.Column(editor_save_btn, width=200)),# sizing_mode='stretch_width'),
                                   name='SCANPLOT - Editor de Texto', 
                                   contained=False, 
                                   position='center', 
                                   #margin=20,
                                   config=config2)

## Botão do editor de textos
editor_btn = pn.widgets.Button(name='🗒️ Editor de Texto', button_type='primary')

## Conteúdo do diálogo modal da paleta de cores
col_pallete1 = pn.pane.PNG('/extra3/SCANPLOT/jupyter/img/cp_uniform_sequential.png', width=1000)
col_pallete2 = pn.pane.PNG('/extra3/SCANPLOT/jupyter/img/cp_diverging.png', width=1000)
col_pallete3 = pn.pane.PNG('/extra3/SCANPLOT/jupyter/img/cp_rainbow.png', width=1000)
col_pallete4 = pn.pane.PNG('/extra3/SCANPLOT/jupyter/img/cp_categorical.png', width=1000)
col_pallete5 = pn.pane.PNG('/extra3/SCANPLOT/jupyter/img/cp_mono_sequential.png', width=1000)
col_pallete6 = pn.pane.PNG('/extra3/SCANPLOT/jupyter/img/cp_other_sequential.png', width=1000)
col_pallete7 = pn.pane.PNG('/extra3/SCANPLOT/jupyter/img/cp_miscellaneous.png', width=1000)

## Abas do diálogo modal da paleta de cores
color_palletes_tabs = pn.Tabs(('Uniform Sequential', col_pallete1), 
                              ('Diverging', col_pallete2),
                              ('Rainbow', col_pallete3),
                              ('Categorical', col_pallete4),
                              ('Mono Sequential', col_pallete5),
                              ('Other Sequential', col_pallete6),
                             )

## Demais botões dos outros diálogos modais
modal_btn = pn.widgets.Button(name='📖 Informações Gerais', button_type='primary')
modal_btn_fu = pn.widgets.Button(name='📊 Sobre', button_type='success')
modal_btn_st = pn.widgets.Button(name='📊 Sobre', button_type='success')
modal_btn_sc = pn.widgets.Button(name='📊 Sobre', button_type='success')
modal_btn_ded = pn.widgets.Button(name='📊 Sobre', button_type='success')
modal_help = pn.widgets.Button(name='🛟 Ajuda', button_type='primary')

## Cartões da barra lateral
card_parameters_fu = pn.Card(winpt, modal_btn_fu, title='Selecionar catálogo', collapsed=False)
card_parameters_st = pn.Card(wst, modal_btn_st, title='Série Temporal', collapsed=False)
card_parameters_sc = pn.Card(wsc, modal_btn_sc, title='Scorecard', collapsed=False)
card_parameters_ded = pn.Card(wded, modal_btn_ded, title='Distribuição Espacial', collapsed=False)

#
# INÍCIO DO TEMPLATE
#
        
## Inicializa o template (demais elementos como o conteúdo da barra lateral, botões, diálogos modais, abas e área principal são adicionados depois)
template = pn.template.BootstrapTemplate(title = 'SCANPLOT V2.0.0a1', logo = scantec_logo)

## Abas da área principal (actvive=0 = define a primeira aba como ativa; dynamic=True = carrega as demais abas apenas quando forem clicadas)
tabs = pn.Tabs(dynamic=True, active=0)
tabs.append(('Início', welcomeText))
tabs.append(('Série Temporal', plotCurves))
tabs.append(('Scorecard', plotScorecard))
tabs.append(('Distribuição Espacial', plotFieldsDouble))

## Adiciona um placeholder do modal à barra lateral
template.modal.append(pn.Column())

## Textos dos diálogos modais
text_info1 = pn.Column(text_gen_info)
text_info2 = pn.Column(text_st)
text_info3 = pn.Column(text_fu)

## Inicaliza a barra lateral com o cartão do seletor de catálogos
col = pn.Column(card_parameters_fu)

## Atualiza o conteúdo da barra lateral de acordo com a aba ativa (utiliza o conteúdo da primeira aba no início)
@pn.depends(tabs.param.active, watch=True)
def insert_widget(active_tab):
    if active_tab == 0: 
        col[0] = card_parameters_fu
        text_info3[0] = text_fu   
    elif active_tab == 1: 
        col[0] = card_parameters_st
        text_info2[0] = text_st
    elif active_tab == 2: 
        col[0] = card_parameters_sc    
        text_info2[0] = text_sc
    elif active_tab == 3: 
        col[0] = card_parameters_ded
        text_info2[0] = text_ded
        
## Funções que definem quais botões abrem quais diálogos modais        
def show_modal_1(event):
    template.modal[0].clear()
    template.modal[0].append(text_info1)
    template.open_modal()

def show_modal_2(event):
    template.modal[0].clear()
    template.modal[0].append(text_info2)
    template.open_modal()    
        
def show_modal_3(event):
    template.modal[0].clear()
    template.modal[0].append(pn.Column('# Paletas de Cores', 'Mais informações em <a href="https://holoviews.org/user_guide/Colormaps.html" target="_blank">Colormaps</a>.', color_palletes_tabs))
    template.open_modal()

def show_modal_4(event):
    template.modal[0].clear()
    template.modal[0].append(pn.Column(text_help))
    template.open_modal()    
    
def show_modal_5(event):
    template.modal[0].clear()
    template.modal[0].append(text_info3)
    template.open_modal()      
    
def show_text_editor(event):
    placeholder[:] = [text_editor]    
    
## Callback dos botões e diálogos modais    
modal_btn.on_click(show_modal_1)
modal_btn_fu.on_click(show_modal_5) 
modal_btn_st.on_click(show_modal_2)
modal_btn_sc.on_click(show_modal_2)
modal_btn_ded.on_click(show_modal_2)      

show_color_pallete.on_click(show_modal_3)    
modal_help.on_click(show_modal_4)    
editor_btn.on_click(show_text_editor)
  
placeholder = pn.Column(height=0, width=0)   
    
template.sidebar.append(col)
template.sidebar.append(modal_btn)
template.sidebar.append(modal_help)
template.sidebar.append(editor_btn)
template.sidebar.append(silence)
template.sidebar.append('##### CPTEC-INPE, 2023.')
template.main.append(pn.Column(
    tabs,    
    float_panel, 
    placeholder,
    pn.pane.Alert('⚠️ **Aviso:** As informações aqui apresentadas não representam informações oficiais e não devem ser utilizadas para a tomada de decisão.', alert_type='warning')
    )
)

template.servable();
