#!/usr/bin/env python3
import scanplot as sc
from example_config import load

variables, config, output, figures = load()
start, end = config["Starting Time"], config["Ending Time"]
experiments = list(config["Experiments"])
stats = ["ACOR", "RMSE", "VIES"]
selected = list(variables.values())[:3]

data = sc.get_dataframe(start, end, stats, experiments, output, missing="raise")
for combine in (False, True):
    sc.plot_lines(data, selected, stats, output, figDir=figures, saveFig=True, combine=combine)
