# SCANPLOT - Um sistema de plotagem simples para o SCANTEC
# CC-BY-NC-SA-4.0 2022 INPE
"""Optional Panel interface; importing scanplot does not import Panel or Tk."""

from pathlib import Path


def create_interface():
    """Build the application without starting a server (requires scanplot[gui])."""
    import panel as pn
    import scanplot as sc

    pn.extension()
    installation = pn.widgets.TextInput(name="Diretorio SCANTEC", value="")
    output = pn.widgets.TextInput(name="Diretorio dos resultados", value="")
    load = pn.widgets.Button(name="Carregar", button_type="primary")
    experiments = pn.widgets.MultiChoice(name="Experimentos", options=[])
    variables = pn.widgets.MultiChoice(name="Variaveis", options=[])
    statistics = pn.widgets.MultiChoice(name="Estatisticas", options=["ACOR", "RMSE", "VIES"], value=["ACOR"])
    mode = pn.widgets.Select(name="Grafico", options=["Linhas", "Significancia", "Scorecard", "Campos"])
    score = pn.widgets.Select(name="Score", options=["ganho", "fc"])
    draw = pn.widgets.Button(name="Plotar", button_type="primary", disabled=True)
    status = pn.pane.Alert("Selecione os dados.", alert_type="light")
    result = pn.Column()
    state = {}

    def select_mode(event):
        options = ["RMSE", "VIES", "MEAN"] if mode.value == "Campos" else ["ACOR", "RMSE", "VIES"]
        statistics.options = options
        statistics.value = [value for value in statistics.value if value in options] or [options[0]]
        statistics.disabled = mode.value == "Significancia"
        if statistics.disabled:
            statistics.value = ["ACOR"]
        score.visible = mode.value == "Scorecard"

    mode.param.watch(select_mode, "value")
    select_mode(None)

    def read(event):
        draw.disabled = True
        state.clear()
        result.clear()
        try:
            base = Path(installation.value).expanduser()
            data_vars, config = sc.read_namelists(str(base))
            directory = output.value.strip() or str(base / "dataout")
            if not Path(directory).expanduser().is_dir():
                raise ValueError("Diretorio dos resultados nao encontrado.")
            state.update(variables=data_vars, config=config, directory=directory)
            experiments.options = list(config["Experiments"])
            experiments.value = list(experiments.options)
            variables.options = {description: variable for variable, description in data_vars.values()}
            variables.value = [next(iter(data_vars.values()))[0]]
            draw.disabled = False
            status.object, status.alert_type = "Dados configurados.", "success"
        except (OSError, ValueError, KeyError, IndexError) as exc:
            status.object, status.alert_type = str(exc), "danger"

    def plot(event):
        result.clear()
        try:
            if not state or not experiments.value or not variables.value or not statistics.value:
                raise ValueError("Selecione dados, experimentos, variaveis e estatisticas.")
            config = state["config"]
            selected_vars = [item for item in state["variables"].values() if item[0] in variables.value]
            selected_exps = experiments.value
            stats = ["ACOR"] if mode.value == "Significancia" else statistics.value
            start, end = config["Starting Time"], config["Ending Time"]
            directory = state["directory"]
            if mode.value == "Campos":
                data = sc.get_dataset(config, state["variables"], stats, selected_exps,
                                      directory, missing="raise")
                figures = sc.plot_fields(data, selected_vars, stats, directory, combine=True)
            else:
                data = sc.get_dataframe(start, end, stats, selected_exps, directory, missing="raise")
                if mode.value == "Linhas":
                    figures = sc.plot_lines(data, selected_vars, stats, directory, combine=True)
                elif mode.value == "Scorecard":
                    figures = sc.plot_scorecard(data, selected_vars, stats, score.value,
                                                selected_exps, directory)
                else:
                    daily = sc.get_dataframe(start, end, stats, selected_exps, directory, series=True,
                                             analysis_step=config["Analisys Time Step"], missing="raise")
                    figures = []
                    for variable, description in selected_vars:
                        period = sc.concat_tables_and_loc(data, start, end, selected_exps, variable, False)
                        series = sc.concat_tables_and_loc(daily, start, end, selected_exps, variable, True)
                        aligned = sc.df_fill_nan(period, series)
                        mean, upper, lower = sc.calc_tStudent(aligned)
                        figures.extend(sc.plot_lines_tStudent(start, end, daily, selected_exps,
                                       variable, description, mean, upper, lower, period, directory))
            result.extend(pn.pane.Matplotlib(fig, tight=True) for fig in figures)
            status.object, status.alert_type = "Graficos atualizados.", "success"
        except (OSError, ValueError, KeyError, IndexError, ImportError) as exc:
            status.object, status.alert_type = str(exc), "danger"

    load.on_click(read)
    draw.on_click(plot)
    return pn.template.FastListTemplate(
        title="SCANPLOT", sidebar=[installation, output, load, experiments, variables,
                                  statistics, mode, score, draw],
        main=[status, result],
    )


def show_interface(**kwargs):
    """Start the optional Panel interface and return its template."""
    template = create_interface()
    if kwargs.pop("show", True):
        template.show(**kwargs)
    return template
