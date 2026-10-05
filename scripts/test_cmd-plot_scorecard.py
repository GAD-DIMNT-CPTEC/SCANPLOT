#!/usr/bin/env python3
import scanplot as sc
from example_config import load

variables, config, output, figures = load()
start, end = config["Starting Time"], config["Ending Time"]
experiments = list(config["Experiments"])
stats = ["ACOR", "RMSE", "VIES"]
selected = list(variables.values())[:3]

data = sc.get_dataframe(start, end, stats, experiments[:2], output, missing="raise")
for kind in ("ganho", "fc"):
    sc.plot_scorecard(data, selected, stats, kind, experiments[:2], output,
                      figDir=figures, saveFig=True)
