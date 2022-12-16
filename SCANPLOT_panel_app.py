#!/usr/bin/env python
# coding: utf-8

# Uso
# conda activate SCANPLOT 
# panel serve SCANPLOT_panel_app.py --autoreload  
# @cfbastarz

import numpy as np
import pandas as pd
import holoviews as hv
import param
import panel as pn
from tkinter import Tk, filedialog
#from ttkthemes import ThemedTk

pn.extension('perspective', sizing_mode='stretch_width')

#
import cartopy.crs as ccrs
from cartopy.feature import NaturalEarthFeature, LAND, COASTLINE
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
#

import scanplot as sc

class SCANPLOT(param.Parameterized):  
  
    #
    # CONFIGURAÇÃO SCANTEC
    #

    buttom_read_scantec_path = param.Action(lambda x: x.param.trigger('buttom_read_scantec_path'), 
                                            label='1. Instalação SCANTEC')
   
    scantec_path_read = None
    
    # method keeps on watching whether button is triggered
    @param.depends('buttom_read_scantec_path', watch=True)
    def run_read_scantec_path(self):        
        self.root = Tk()
        #self.root = ThemedTk(theme="breeze")
        self.root.withdraw()
        self.root.attributes('-topmost', True)
        self.open_file = filedialog.askdirectory()
        self.scantec_path_read = True     
    
    # method is watching whether model_trained is updated
    def update_scantec_path(self):
        if self.scantec_path_read:
            return pn.pane.Alert(self.open_file, alert_type='success')
        else: 
            return pn.pane.Alert('Diretório não selecionado!', alert_type='danger')

    data_conf = None
    data_vars = None
    dataInicial = None
    dataFinal = None
    Vars = None
    Stats = None
    Exps = None
    outDir = None
    figDir = None 
    
    # create a button that when pushed triggers 'button'
    button_read_confs_namelists = param.Action(lambda x: x.param.trigger('button_read_confs_namelists'), label='2. Ler Configurações')
   
    confs_namelists_read = None
    
    # method keeps on watching whether button is triggered
    @param.depends('button_read_confs_namelists', watch=True)
    def run_read_confs_namelists(self):   
        scantec_dir = action_SCANPLOT.update_scantec_path()
        self.namelists = sc.read_namelists(scantec_dir.object + '/bin/scantec.conf', scanconf=True)
        
        self.data_conf = self.namelists[1]       
        self.confs_namelists_read = True   
      
    #layout_confs = None
    
    # method is watching whether model_trained is updated
    def update_confs_namelists(self):
        if self.confs_namelists_read:
            return self.data_conf
        else:
            return pn.pane.Alert('Arquivo de configurações não carregado!', alert_type='danger')

    # method is watching whether model_trained is updated
    def transform_confs_namelists(self):
        if self.confs_namelists_read:
            self.layout_confs_box = pn.WidgetBox()

            for key in action_SCANPLOT.data_conf:
                self.layout_confs = pn.Column(pn.widgets.StaticText(name=key, value=action_SCANPLOT.data_conf[key]))
                self.layout_confs_box.append(self.layout_confs)
                        
            return self.layout_confs_box
        else:
            return pn.pane.Alert('Arquivo de configurações não carregado!', alert_type='danger')        
        
    #
    # VARIÁVEIS SCANTEC
    #
        
    # create a button that when pushed triggers 'button'
    button_read_vars_namelists = param.Action(lambda x: x.param.trigger('button_read_vars_namelists'), label='3. Ler Variáveis')
   
    vars_namelists_read = None
    
    # method keeps on watching whether button is triggered
    @param.depends('button_read_vars_namelists', watch=True)
    def run_read_vars_namelists(self):       
        scantec_dir = action_SCANPLOT.update_scantec_path()
        self.namelists = sc.read_namelists(scantec_dir.object + '/bin/scantec.conf', scanconf=True)
        
        self.data_vars = self.namelists[0] 
        self.vars_namelists_read = True        
        
    vars_opts = None       
    #layout_vars = None
    
    # method is watching whether model_trained is updated
    def update_vars_namelists(self):
        if self.vars_namelists_read:
            return self.data_vars
        else:
            return pn.pane.Alert('Arquivo de variáveis não carregado!', alert_type='danger')

    # method is watching whether model_trained is updated
    def transform_vars_namelists(self):
        if self.vars_namelists_read:
            #self.data_vars = None
            self.vars_opts = []
            for idx in self.data_vars:
                tup = self.data_vars[idx]
                var_sig = tup[0]
                var_ext = tup[1]
                var_sig_ext = var_sig + ' (' + var_ext + ')'
                self.vars_opts.append(var_sig_ext)
               
            self.layout_vars = pn.widgets.CheckBoxGroup(name='VARIÁVEIS', 
                                                        value=[self.vars_opts[0]], 
                                                        options=self.vars_opts, 
                                                        inline=False)
                       
#            return self.layout_vars
            return pn.pane.Alert('Arquivo de variáveis lido corretamente!', alert_type='success')
        else:
            return pn.pane.Alert('Arquivo de variáveis não carregado!', alert_type='danger')        
        
    #
    # TABELAS SCANTEC
    #
    
    # create a button that when pushed triggers 'button'
    button_get_dataframe = param.Action(lambda x: x.param.trigger('button_get_dataframe'), 
                                        label='4. Ler Tabelas')
   
    tables_loaded = None
    
    # method keeps on watching whether button is triggered
    @param.depends('button_get_dataframe', watch=True)
    def run_get_dataframe(self):

        data_conf = action_SCANPLOT.update_confs_namelists()
        dataInicial = data_conf['Starting Time']
        dataFinal = data_conf['Ending Time']
        
        data_vars = action_SCANPLOT.update_vars_namelists()
        #Vars = list(map(data_vars.get,[11,12,13]))
        #Vars = list(data_vars.values())
        #Vars = list(data_vars.values)
        Vars = data_vars.values

        Stats = ['MEAN', 'RMSE', 'VIES']
        Exps = ['X666'] 
        outDir = './test/SCANTEC.2.0.0b2_test_aval_oper/dataout'
        figDir = outDir + '/figs'
        
        self.dataframe = sc.get_dataframe(dataInicial, dataFinal, Stats, 
                                          Exps, outDir, series=False)
        self.tables_loaded = True    
        
    dataframe_lst = None    
    dataframe_names = None
        
    # method is watching whether model_trained is updated
    def update_dataframe(self):
        if self.tables_loaded:
            self.dataframe_lst = {}
            self.dataframe_names = list(self.dataframe.keys())
            for item in self.dataframe_names:
                self.dataframe_lst[item] = pn.widgets.DataFrame(self.dataframe[item], name=item)

            def show_dataframe(dataframe_sel):
                return self.dataframe_lst[self.dataframe_sel.value]

            self.dataframe_sel = pn.widgets.Select(value=self.dataframe_names[0], 
                                     options=self.dataframe_names, name='Tabelas', width=300)
            
            show_dataframe = pn.bind(show_dataframe, dataframe_sel=self.dataframe_sel)  
            
            show_dataframe_panel = pn.panel(self.dataframe_sel.param.value)
            
            @pn.depends(self.dataframe_sel.param.value, watch=True)
            def update_dataframe_pane(dataframe_sel):
                show_dataframe_panel.object = self.dataframe_sel
            
            update_dataframe_pane(self.dataframe_sel.value)
            
#            layout_show_dataframe = pn.Column(self.dataframe_sel, show_dataframe)                 

            file = pn.widgets.Select(value=self.dataframe_names[0], options=[i for i in list(self.dataframe_names)],
                        name='Files')

#            var = pn.widgets.Select(value=self.dataframe[file.value].columns.values[1], 
#                                    options=[i for i in list(self.dataframe[file.value].columns.values[1:])],
#                                    name='Variables')
            var = pn.widgets.CheckBoxGroup(name='Variables', 
                                           value=[str(self.dataframe[file.value].columns.values[1])],
                                           options=list(self.dataframe[file.value].columns.values[1:]), 
                                           inline=True)

            def get_table(file, var):
                return self.dataframe[file].loc[:, var]
#                return self.dataframe[file][var]

            layout_show_dataframe = pn.Column(
                    pn.Column(file, var),
                    pn.bind(get_table, file, var)
                    )
                        
            self.layout_dataframe_box = pn.WidgetBox(layout_show_dataframe)
                
            return self.layout_dataframe_box
        else:    
            return pn.pane.Alert('Tabelas não carregadas!', alert_type='danger')

    #
    # CAMPOS ESPACIAIS SCANTEC
    #
        
    button_get_dataset = param.Action(lambda x: x.param.trigger('button_get_dataset'), 
                                      label='5. Ler Campos Espaciais')

    fields_loaded = None
    
    # method keeps on watching whether button is triggered
    @param.depends('button_get_dataset', watch=True)
    def run_get_dataset(self):
        
        data_conf = action_SCANPLOT.update_confs_namelists()
        #dataInicial = data_conf['Starting Time']
        #dataFinal = data_conf['Ending Time']
        
        data_vars = action_SCANPLOT.update_vars_namelists()
        #Vars = list(data_vars.values())

        Stats = ['MEAN', 'RMSE', 'VIES']
        Exps = ['X666'] 
        outDir = './test/SCANTEC.2.0.0b2_test_aval_oper/dataout'
        #figDir = outDir + '/figs'        
        
        self.dataset = sc.get_dataset(data_conf, data_vars, Stats, 
                                      Exps, outDir)
        self.fields_loaded = True        

#    # method is watching whether model_trained is updated
#    def update_dataset(self):
#        if self.fields_loaded:
#            return self.dataset
#        else:        
#            return pn.pane.Alert('Arquivos binários não carregados!', alert_type='danger')    

    dataset_lst = None    
    dataset_names = None

    # method is watching whether model_trained is updated
    def update_dataset(self):
        if self.fields_loaded:
            self.dataset_lst = {}
            self.dataset_names = list(self.dataset.keys())
            for item in self.dataset_names:
                #self.dataset_lst[item] = pn.widgets.DataFrame(self.dataset[item].to_dataframe(), name=item)
                #self.dataset_lst[item] = self.dataset[item]
                self.dataset_lst[item] = self.dataset[item].hvplot.contourf(groupby='time', colorbar=True, levels=10,
                                                                            coastline=True, global_extent=True,
                                                                            crs=ccrs.PlateCarree(), projection=ccrs.PlateCarree(), 
                                                                            frame_height=300)

            def show_dataset(dataset_sel):
                return self.dataset_lst[self.dataset_sel.value]

            self.dataset_sel = pn.widgets.Select(value=self.dataset_names[0], 
                                     options=self.dataset_names, name='Campos Espaciais', width=300)
                        
            show_dataset = pn.bind(show_dataset, dataset_sel=self.dataset_sel)  
            
            show_dataset_panel = pn.panel(self.dataset_sel.param.value)
            
            @pn.depends(self.dataset_sel.param.value, watch=True)
            def update_dataset_pane(dataset_sel):
                show_dataset_panel.object = self.dataset_sel
            
            #update_dataset_pane(self.dataset_sel.value)
            
            #layout_show_dataset = pn.Column(self.dataset_sel, show_dataset)
            #layout_show_dataset = pn.Column(update_dataset_pane(self.dataset_sel.value))

            update_dataset_pane(self.dataset_sel.value)
#            layout_show_dataset = pn.Column(self.dataset_sel, show_dataset)    

            file = pn.widgets.Select(options=[i for i in list(self.dataset.keys())],
                        name='Files')

            var = pn.widgets.Select(options=[i for i in self.dataset[file.value].data_vars],
                        name='Variables')

            def get_plot(file, var):
                return self.dataset[file][var].hvplot(groupby='time', 
                                              colorbar=True,
                                              #levels=10,
                                              coastline=True,
                                              #global_extend=True,
                                              crs=ccrs.PlateCarree(), 
                                              projection=ccrs.PlateCarree(),
                                              grid=True, 
                                              #width=500,
                                              frame_height=550,
                                              rasterize=False,
                                              widget_type='scrubber', 
                                              widget_location='bottom')

            layout_show_dataset = pn.Column(
#                    pn.Column(self.dataset_sel, show_dataset, file, var),
                    pn.Column(file, var),
                    pn.bind(get_plot, file, var)
                    )
            
            self.layout_dataset_box = pn.WidgetBox(layout_show_dataset)

            return self.layout_dataset_box
        else:    
            return pn.pane.Alert('Arquivos binários não carregados!', alert_type='danger') 

    #
    # FUNÇÕES DE PLOTAGEM
    #
        
    avaltype_list = ['Gráfico de Linha Simples', 'Gráfico de Linha Com teste t-Student', 
                     'Distribuição Espacial', 'Scorecard', 'Diagrama de Taylor']
     
    #def get_avaltype(avaltype):
    def get_avaltype(self):
        return self.avaltype
    
    #def plotfuncs(avaltype):
    def plotfuncs(self):
#        if self.avaltype == 'Distribuição Espacial':
#            return sc.plot_fields(dSet, Vars, Stats, outDir, combine=True, hvplot=True, avaltype=avaltype)
#        elif self.avaltype == 'Scorecard':
#            return sc.plot_fields(dSet, Vars, Stats, outDir, combine=False, hvplot=True, avaltype=avaltype)
#        else:
#            df = pd.DataFrame(np.random.randn(1000, 4), index=idx, 
#                                columns=list('ABCD')).cumsum()
#            return df.hvplot(title=avaltype)
        self.df = pd.DataFrame(np.random.randn(1000, 4), index=idx, 
                                columns=list('ABCD')).cumsum()
        return self.df.hvplot(title=avaltype)
    
    avaltype = pn.widgets.Select(value=avaltype_list[0], options=avaltype_list,
                                 name='Tipo de Avaliação', width=300)
    
    plotfuncs = pn.bind(plotfuncs, avaltype=avaltype)  
    
    scanplot_plot_panel = pn.panel(avaltype.param.value)
    
    @pn.depends(avaltype.param.value, watch=True)
    #def update_scanplot_plot_pane(avaltype):
    def update_scanplot_plot_pane(self):
        self.scanplot_plot_panel.object = get_avaltype(self.avaltype)
    
#    update_scanplot_plot_pane(self.avaltype.value)

    def update_plotfuncs(self):
        #update_scanplot_plot_pane(self.avaltype.value)
        #return pn.Column(self.avaltype)
        return pn.pane.Alert('Funções de plotagem não carregadas!', alert_type='danger') 

#    layout_plotfuncs = pn.Column(avaltype, plotfuncs)
#    layout_plotfuncs = pn.Column(avaltype)

#
# Instâncias 
#

action_SCANPLOT = SCANPLOT()   

#
# App layout
#

pn.Column(action_SCANPLOT.param, action_SCANPLOT.update_scantec_path,
                                 action_SCANPLOT.transform_confs_namelists, 
                                 action_SCANPLOT.transform_vars_namelists,
                                 action_SCANPLOT.update_dataframe,
                                 action_SCANPLOT.update_dataset,
                                 action_SCANPLOT.update_plotfuncs)
#                                 action_SCANPLOT.layout_plotfuncs)

#
# Aplicação
#

# Cores
PALETTE = [
    "#ff6f69",
    "#ffcc5c",
    "#88d8b0",
    "#0072B5",
]

ACCENT_BASE_COLOR = PALETTE[3] # 3 = azul (padrão panel)

logo_scantec = './img/logo_scantec_lateral.png'
logo_cptec = './img/cptec_menor.png'
logo_inpe = './img/logo_inpe.png'

# Título (barra superior)
title = 'SCANPLOT'

# Informações (barra lateral esquerda)
description = """
**SCANPLOT: Um Sistema de Plotagem Simples para o SCANTEC**

SCANTEC - Sistema Comunitário de Avaliação de modelos Numéricos de Tempo E Clima

INPE - Instituto Nacional de Pesquisas Espaciais

CPTEC - Centro de Previsão de Tempo e Estudos Climáticos
"""

disclaimer = """
**AVISO:** As informações apresentadas nesta página são fornecidas em caráter experimental.
"""

main_message = """
#### INSTRUÇÕES DE USO

Utilize os botões a seguir na seguinte ordem:

1. **Instalação SCANTEC:** escolha do diretório de instalação do SCANTEC;
2. **Ler Configurações:** leitura do arquivo de configurações `scantec.conf`;
3. **Ler Variáveis:** leitura do arquivo de variáveis `scantec.vars`;
4. **Ler Tabelas:** leitura das tabelas do SCANTEC com a função `get_dataframe`;
5. **Ler Campos Espaciais:** leitura dos campos espaciais do SCANTEC com a função `get_dataset`;
6. **Funções de Plotagem:** selecão do tipo de gráfico a ser plotado (avaliação estatística).
"""  
    
# Layout

#pn.template.FastGridTemplate(
pn.template.FastListTemplate(
#pn.template.MaterialTemplate(
#pn.template.VanillaTemplate(
#pn.template.GoldenTemplate(
#pn.template.BootstrapTemplate(
    site = title,
    title = 'Interface',
    sidebar = [pn.Column(main_message, action_SCANPLOT.param, logo_inpe)],
    #main = [pn.Column(pn.pane.Alert(disclaimer, alert_type='warning'), 
    main = [pn.Column( 
                      '#### DIRETÓRIO SCANTEC',    action_SCANPLOT.update_scantec_path, 
                      pn.Tabs(('Configurações',    pn.Column(action_SCANPLOT.transform_confs_namelists, action_SCANPLOT.transform_vars_namelists)),
#                              ('Variáveis',        action_SCANPLOT.transform_vars_namelists ),
                              ('Tabelas',          action_SCANPLOT.update_dataframe         ), 
                              ('Campos Espaciais', action_SCANPLOT.update_dataset           ), 
#                              ('Funções de Plotagem', action_SCANPLOT.layout_plotfuncs),
                              ('Funções de Plotagem', action_SCANPLOT.update_plotfuncs),
                              dynamic=False),
                      pn.pane.Alert(disclaimer, alert_type='warning')
                      )], main_max_width='1900px',
    accent_base_color = ACCENT_BASE_COLOR,
    header_background = ACCENT_BASE_COLOR,
).show()
