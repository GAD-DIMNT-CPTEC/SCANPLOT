#!/usr/bin/env python3
import scanplot as sc
from example_config import load

variables, config, output, figures = load()
start, end = config["Starting Time"], config["Ending Time"]
experiments = list(config["Experiments"])
stats = ["ACOR", "RMSE", "VIES"]
selected = list(variables.values())[:3]

data = sc.get_dataframe(start, end, ["ACOR"], experiments, output, missing="raise")
daily = sc.get_dataframe(start, end, ["ACOR"], experiments, output, series=True,
                         analysis_step=config["Analisys Time Step"])
for variable, description in selected:
    period = sc.concat_tables_and_loc(data, start, end, experiments, variable, False)
    series = sc.concat_tables_and_loc(daily, start, end, experiments, variable, True)
    aligned = sc.df_fill_nan(period, series)
    mean, upper, lower = sc.calc_tStudent(aligned)
    sc.plot_lines_tStudent(start, end, daily, experiments, variable, description,
                           mean, upper, lower, period, output, figDir=figures, saveFig=True)
