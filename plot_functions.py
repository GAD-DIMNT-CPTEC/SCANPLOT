# SCANPLOT - Um sistema de plotagem simples para o SCANTEC
# CC-BY-NC-SA-4.0 2022 INPE

import os
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import rcParams
import seaborn as sns
import skill_metrics as sm

try:
    from IPython import get_ipython
except ImportError:
    def get_ipython():
        return None

import global_variables as gvars
from aux_functions import isnotebook
from data_structures import table_metadata

ipython = get_ipython()


def _options(outDir, kwargs):
    directory = Path(kwargs.get("figDir") or outDir).expanduser()
    save = kwargs.get("saveFig", gvars.saveFig)
    if save:
        directory.mkdir(parents=True, exist_ok=True)
    return directory, kwargs.get("showFig", gvars.showFig), save


def _finish(fig, directory, name, show, save):
    try:
        fig.tight_layout()
        if save:
            fig.savefig(directory / name, bbox_inches="tight", dpi=120)
        if show:
            plt.show()
    finally:
        plt.close(fig)


def _column(frame, variable):
    return variable if variable in frame.columns else variable.lower()


def _indexed(frame):
    if "%Previsao" not in frame or frame["%Previsao"].duplicated().any():
        raise ValueError("Informe tabelas com prazos unicos em %Previsao.")
    return frame.set_index("%Previsao").sort_index()


def _select(dTable, stat, experiment=None):
    selected = []
    for name, frame in dTable.items():
        meta = table_metadata(name)
        if meta["stat"] == stat and (experiment is None or meta["experiment"] == experiment):
            selected.append((name, frame, meta))
    if not selected:
        raise ValueError(f"Nenhuma tabela encontrada: {stat}, {experiment or 'experimentos'}.")
    return selected


def plot_lines(dTable, Vars, Stats, outDir, **kwargs):
    """Plot each series against its actual forecast hours; return figures."""
    directory, show, save = _options(outDir, kwargs)
    figures = []
    for stat in Stats:
        tables = _select(dTable, stat)
        groups = [tables] if kwargs.get("combine", gvars.combine) else [[item] for item in tables]
        for group in groups:
            for variable, description in Vars:
                fig, ax = plt.subplots(figsize=(8, 5))
                styles = kwargs.get("lineStyles", gvars.lineStyles)
                try:
                    for i, (name, frame, meta) in enumerate(group):
                        series = _indexed(frame)[_column(frame, variable)]
                        if styles:
                            ax.plot(series.index, series, styles[i % len(styles)],
                                    label=meta["experiment"])
                        else:
                            ax.plot(series.index, series, marker="o", label=meta["experiment"])
                    ax.set(title=description, xlabel="Horas de Integracao", ylabel=stat)
                    ax.axhline(0.5 if stat == "ACOR" else 0, color="black", linewidth=1)
                    ax.grid(linestyle="--", alpha=0.5)
                    ax.legend()
                    meta = group[0][2]
                    tag = "EXPS" if len(group) > 1 else meta["experiment"]
                    name = f"{stat}{tag}_{meta['start']}{meta['end']}_{variable.replace(':', '').replace('-', '')}.png"
                    _finish(fig, directory, name, show, save)
                finally:
                    plt.close(fig)
                figures.append(fig)
    return figures


def plot_lines_tStudent(dataInicial, dataFinal, dTable_series, Exps, Var, VarName,
                       ldrom_exp, ldrosup_exp, ldroinf_exp, varlev_exps, outDir, **kwargs):
    """Plot ACOR and one mean-centered 95% confidence interval per comparison.

    Inputs retain the signed half-width convention of calc_tStudent. Each
    displayed interval is [mean + lower, mean + upper]; excluding zero
    corresponds to significance at 5% for that comparison and forecast hour.
    """
    if len(Exps) < 2 or len(Exps) != len(varlev_exps) or any(
        len(values) != len(Exps) - 1 for values in (ldrom_exp, ldrosup_exp, ldroinf_exp)
    ):
        raise ValueError("Experimentos, curvas e intervalos devem corresponder.")
    directory, show, save = _options(outDir, kwargs)
    colors = kwargs.get("lineStyles") or plt.rcParams["axes.prop_cycle"].by_key()["color"]
    fig, axes = plt.subplots(len(Exps), 1, sharex=True,
                             figsize=(9, 3 + 2.2 * (len(Exps) - 1)),
                             gridspec_kw={"height_ratios": [1.3] + [1] * (len(Exps) - 1)})
    for i, series in enumerate(varlev_exps):
        axes[0].plot(series.index, series, label=Exps[i], color=colors[i % len(colors)])
    for i, (mean, upper, lower) in enumerate(zip(ldrom_exp, ldrosup_exp, ldroinf_exp), 1):
        color = colors[i % len(colors)]
        ax = axes[i]
        if i > 1:
            ax.sharey(axes[1])
        mean = mean.sort_index()
        low = mean + lower.reindex(mean.index)
        high = mean + upper.reindex(mean.index)
        valid = np.isfinite(mean) & np.isfinite(low) & np.isfinite(high)
        ax.plot(mean.index, mean, color=color, marker="o", markersize=3,
                label="Diferenca media")
        ax.fill_between(mean.index, low, high, where=valid, color=color,
                         alpha=0.22, label="IC 95%")
        ax.axhline(0, color="black", linestyle="--", linewidth=1)
        ax.set(title=f"{Exps[0]} - {Exps[i]}", ylabel="Diferenca de ACOR")
    axes[0].set(title=VarName, ylabel="ACOR")
    axes[0].axhline(0.5, color="black", linewidth=0.8)
    axes[-1].set_xlabel("Horas de Integracao")
    for ax in axes:
        ax.grid(linestyle=":", alpha=0.4)
        ax.legend(loc="best", fontsize=9)
    name = f"ACOREXPS_{dataInicial:%Y%m%d%H}{dataFinal:%Y%m%d%H}_{Var.replace(':', '')}-tStudent.png"
    _finish(fig, directory, name, show, save)
    return [fig]


def scorecard_values(reference, experiment, statistic, kind):
    """Positive means improvement; undefined baselines remain NaN."""
    if kind not in ("ganho", "fc") or statistic not in ("ACOR", "RMSE", "VIES"):
        raise ValueError("Scorecard requer ganho/fc e ACOR/RMSE/VIES.")
    reference, experiment = reference.align(experiment, join="outer")
    reference = reference.where(np.isfinite(reference))
    experiment = experiment.where(np.isfinite(experiment))
    if statistic == "ACOR":
        numerator = experiment - reference
        denominator = 1 - reference if kind == "ganho" else reference.abs()
    else:
        reference, experiment = reference.abs(), experiment.abs()
        numerator = reference - experiment
        denominator = reference
    result = numerator / denominator.where(denominator != 0)
    return result * (100 if kind == "ganho" else 1)


def plot_scorecard(dTable, Vars, Stats, Tstat, Exps, outDir, **kwargs):
    """Compare exactly two experiments; undefined cells are masked."""
    if len(Exps) != 2 or Exps[0] == Exps[1]:
        raise ValueError("Informe dois experimentos distintos.")
    directory, show, save = _options(outDir, kwargs)
    figures = []
    for stat in Stats:
        selections = [_select(dTable, stat, experiment) for experiment in Exps]
        if any(len(items) != 1 for items in selections):
            raise ValueError("Selecione um unico periodo para cada experimento.")
        left, right = (items[0] for items in selections)
        if (left[2]["start"], left[2]["end"]) != (right[2]["start"], right[2]["end"]):
            raise ValueError("Os periodos dos experimentos devem coincidir.")
        frames = []
        for _, frame, _ in (left, right):
            indexed = _indexed(frame)
            columns = [_column(frame, variable) for variable, _ in Vars]
            indexed = indexed[columns].rename(columns=dict(zip(columns, [v for v, _ in Vars])))
            frames.append(indexed.drop(index=0, errors="ignore").T)
        scores = scorecard_values(*frames, stat, Tstat)
        if scores.empty:
            raise ValueError("Nao ha prazos maiores que zero para o scorecard.")
        fig, ax = plt.subplots(figsize=(10, max(3, len(Vars) * 0.4)))
        limit = 100 if Tstat == "ganho" else 1
        sns.heatmap(scores, ax=ax, annot=True, fmt=".0f" if Tstat == "ganho" else ".2f",
                    cmap="RdYlGn", vmin=-limit, vmax=limit, center=0,
                    mask=scores.isna(), cbar_kws={"label": "Melhora (%)" if Tstat == "ganho" else "Melhora relativa"})
        ax.set(xlabel="Horas de Integracao", ylabel="Variavel",
               title=f"{stat}: {Exps[1]} em relacao a {Exps[0]} ({Tstat})")
        ax.tick_params(axis="y", labelrotation=0)
        meta = left[2]
        name = f"SCORECARD_{Tstat.upper()}_{stat}_{Exps[0]}_{Exps[1]}_{meta['start']}{meta['end']}.png"
        _finish(fig, directory, name, show, save)
        figures.append(fig)
    return figures


def plot_dTaylor(dTable,data_conf,Vars,Stats,outDir,**kwargs):
    
    """
    plot_dTaylor
    ============
    
    Esta função plota o diagrama de Taylor a partir das tabelas de estatísticas
    do SCANTEC, para um ou mais experimentos.
    
    Esta função utiliza o módulo SkillMetrics (https://pypi.org/project/SkillMetrics/). 
    
    Parâmetros de entrada
    ---------------------
        dTable    : objeto dicionário com uma ou mais tabelas do SCANTEC;
        Vars      : lista com os nomes e níveis das variáveis;
        data_conf : objeto dicionário com as configurações do SCANTEC;
        Stats     : lista com os nomes das estatísticas a serem processadas
                    (são necessárias as tabelas ACOR, RMSE e VIES);
        outDir    : string com o diretório com as tabelas do SCANTEC.
    
    Parâmetros de entrada opcionais
    -------------------------------
        showFig : valor Booleano para mostrar ou não as figuras durante a plotagem:
                  * showFig=False (valor padrão), não mostra as figuras (mais rápido);
                  * showFig=True, mostra as figuras (mais lento);
        saveFig : valor Booleano para salvar ou não as figuras durante a plotagem:
                  * saveFig=False (valor padrão), não salva as figuras;
                  * saveFig=True, salva as figuras;
        figDir  : string com o diretório onde as figuras serão salvas.

    Resultado
    ---------
        Figuras salvas no diretório definido na variável outDir ou figDir. Se figDir não
        for passado, então as figuras são salvas no diretório outDir (SCANTEC/dataout).
    
    Uso
    ---
        import scanplot 
        
        data_vars, data_conf = scanplot.read_namelists("~/SCANTEC")
        
        dataInicial = data_conf["Starting Time"]
        dataFinal = data_conf["Ending Time"]
        Vars = list(map(data_vars.get,[*data_vars.keys()]))
        Stats = ["ACOR", "RMSE", "VIES"]
        Exps = list(data_conf["Experiments"].keys())
        outDir = data_conf["Output directory"]
        
        figDir = data_conf["Output directory"]

        dTable = scanplot.get_dataframe(dataInicial,dataFinal,Stats,Exps,outDir)
        
        scanplot.plot_dTaylor(dTable,data_conf,Vars,Stats,outDir,figDir=figDir,showFig=True,saveFig=True)       
 
    Observações
    -----------
        Experimental, esta função considera o devio-padrão como a raiz quadrada do RMSE.
    """
    
    # Verifica se foram passados os argumentos opcionais e atribui os valores

    if 'tExt' in kwargs:
        tExt = kwargs['tExt']      
        # Atualiza o valor global de tExt
        gvars.tExt = tExt
    else:
        tExt = gvars.tExt

    if 'figDir' in kwargs:
        figDir = kwargs['figDir']
    else:
        figDir = outDir

    if 'showFig' in kwargs:
        showFig = kwargs['showFig']
    else:
        showFig = gvars.showFig

    if 'saveFig' in kwargs:
        saveFig = kwargs['saveFig']
    else:
        saveFig = gvars.saveFig

    if isnotebook(get_ipython().__class__.__name__):
        if showFig:
            ipython.run_line_magic('matplotlib', 'inline')           
            mpl.rcParams.update({'figure.max_open_warning': 0})
        else:
            ipython.run_line_magic('matplotlib', 'agg')           
    else:
        if not showFig:
            mpl.use('agg')
            mpl.rcParams.update({'figure.max_open_warning': 0})

    dataInicial = data_conf["Starting Time"]
    dataFinal = data_conf["Ending Time"]

    datai = dataInicial.strftime('%Y%m%d%H')
    dataf = dataFinal.strftime('%Y%m%d%H')

    # Ignore Seaborn and respect rcParams
    sns.reset_orig()
    
    # Set the figure properties (optional)
    rcParams["figure.figsize"] = [8.0, 6.5]
    rcParams['lines.linewidth'] = 1 # line width for plots
    rcParams.update({'font.size': 12}) # font size of axes text
    rcParams['axes.titlepad'] = 40 # title vertical distance from plot
    
    Exps = [*data_conf['Experiments'].keys()]
    
    fig = plt.figure()
       
    for exp in range(len(Exps)): 
        
        for var in range(len(Vars)):
        
            tAcor = list(filter(lambda x:'ACOR' in x, [*dTable.keys()]))[exp]
            tRmse = list(filter(lambda x:'RMSE' in x, [*dTable.keys()]))[exp]
            tVies = list(filter(lambda x:'VIES' in x, [*dTable.keys()]))[exp]
    
            bias  = dTable[tVies].loc[:,[Vars[var][0].lower()]].to_numpy()
            ccoef = dTable[tAcor].loc[:,[Vars[var][0].lower()]].to_numpy()
            crmsd = dTable[tRmse].loc[:,[Vars[var][0].lower()]].to_numpy()
            sdev  = (dTable[tRmse].loc[:,[Vars[var][0].lower()]]**(1/2)).to_numpy() # rever

            biasT = bias.T
            ccoefT = ccoef.T
            crmsdT = crmsd.T
            sdevT = sdev.T
    
            bias = np.squeeze(biasT)
            ccoef = np.squeeze(ccoefT)
            crmsd = np.squeeze(crmsdT)
            sdev = np.squeeze(sdevT)
    
            label = [*dTable[tVies].loc[:,"%Previsao"].values]
        
            if not showFig:
                plt.figure()    

            plt.tight_layout()
    
            sm.taylor_diagram(sdev, crmsd, ccoef, markerLabel = label, 
                              locationColorBar = 'EastOutside',
                              markerDisplayed = 'colorBar', titleColorBar = 'Bias',
                              markerLabelColor='black', markerSize=10,
                              markerLegend='off', cmapzdata=bias,
                              colRMS='g', styleRMS=':',  widthRMS=2.0, titleRMS='on',
                              colSTD='b', styleSTD='-.', widthSTD=1.0, titleSTD ='on',
                              colCOR='k', styleCOR='--', widthCOR=1.0, titleCOR='on')
        
            plt.title("Diagrama de Taylor " + str(Exps[exp]) + '\n' + str(Vars[var][1]), fontsize=14)

            if saveFig:
                #fig_name = 'dtaylor-' + str(Exps[exp]) + '-' + Vars[var][0] + '.png'
                if tExt == 'scan':
                    fig_name = 'DTAYLOR_' + str(Exps[exp]) + '_' + str(datai) + str(dataf) + '_' + Vars[var][0].replace(':', '') + '.png'
                else:
                    fig_name = 'DTAYLOR_' + str(Exps[exp]) + '_' + str(datai) + str(dataf) + '_' + Vars[var][0].replace('-','') + '.png'
                plt.savefig(os.path.join(figDir, fig_name), bbox_inches="tight", dpi=120)

            if showFig:
                plt.show()
            else:
                plt.close(fig)     

    plt.close(fig)     

    return


def plot_fields(dSet, Vars, Stats, outDir, **kwargs):
    """Plot all selected fields and leads, optionally as combined panels.

    Interactive mode returns a Panel layout and does not save raster files.
    Static mode returns the generated Matplotlib figures.
    """
    import cartopy.crs as ccrs

    selected = {name: dataset for name, dataset in dSet.items()
                if table_metadata(name)["stat"] in Stats}
    if not selected:
        raise ValueError("Nenhum campo encontrado para as estatisticas selecionadas.")
    requested = [v for v, _ in Vars] if Vars else []
    variables = list(dict.fromkeys(v for dataset in selected.values() for v in dataset.data_vars
                                  if not requested or v in requested))
    if not variables:
        raise ValueError("Nenhuma variavel selecionada foi encontrada.")
    directory, show, save = _options(outDir, kwargs)
    combine = kwargs.get("combine", gvars.combine)
    if kwargs.get("hvplot", gvars.hvplot):
        if save:
            raise ValueError("saveFig nao e suportado no modo interativo; use hvplot=False.")
        import hvplot.xarray  # Registers the xarray accessor.
        import panel as pn
        panels = []
        for name, dataset in selected.items():
            for variable in variables:
                if variable in dataset:
                    panels.append(dataset[variable].hvplot.contourf(
                        groupby="time", title=f"{name}: {variable}", colorbar=True,
                        geo=True, coastline=True, crs=ccrs.PlateCarree(), frame_height=300))
        return pn.Row(*panels) if combine else pn.Column(*panels)

    groups = [list(selected.items())] if combine else [[item] for item in selected.items()]
    figures = []
    for group in groups:
        for variable in variables:
            available = [(name, dataset) for name, dataset in group if variable in dataset]
            if not available:
                continue
            def leads(dataset):
                if "forecast_hour" in dataset.coords:
                    return list(dataset.forecast_hour.values)
                return list(range(dataset.sizes["time"]))
            all_leads = sorted(set(lead for _, dataset in available for lead in leads(dataset)))
            for lead in all_leads:
                panels = [(name, dataset, leads(dataset).index(lead))
                          for name, dataset in available if lead in leads(dataset)]
                fig, axes = plt.subplots(1, len(panels), squeeze=False,
                                         figsize=(7 * len(panels), 5),
                                         subplot_kw={"projection": ccrs.PlateCarree()})
                try:
                    for ax, (name, dataset, index) in zip(axes.flat, panels):
                        field = dataset[variable].isel(time=index)
                        field.plot.pcolormesh(ax=ax, transform=ccrs.PlateCarree(),
                                             add_colorbar=True)
                        ax.coastlines()
                        ax.gridlines(draw_labels=True)
                        ax.set_title(f"{name.split('_')[0]} {variable} (+{lead} h)")
                    tag = "COMBINED_" + "_".join(name.rsplit(".", 1)[0] for name, _ in available) if combine else available[0][0].rsplit(".", 1)[0]
                    # Bound filenames for combined plots containing many experiments.
                    if len(tag) > 160:
                        import hashlib
                        tag = "COMBINED_" + hashlib.sha256(tag.encode()).hexdigest()[:16]
                    name = f"{tag}_{variable.replace(':', '')}_{lead}.png"
                    _finish(fig, directory, name, show, save)
                finally:
                    plt.close(fig)
                figures.append(fig)
    return figures
