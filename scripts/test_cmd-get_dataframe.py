#!/usr/bin/env python3
import scanplot as sc
from example_config import load

variables, config, output, figures = load()
start, end = config["Starting Time"], config["Ending Time"]
experiments = list(config["Experiments"])
stats = ["ACOR", "RMSE", "VIES"]
selected = list(variables.values())[:3]

data = sc.get_dataframe(start, end, stats, experiments, output, save=True, missing="raise")
daily = sc.get_dataframe(start, end, stats, experiments, output, series=True,
                         analysis_step=config["Analisys Time Step"], save=True)
print(f"{len(data)} tabelas de periodo; {len(daily)} tabelas por inicializacao.")
