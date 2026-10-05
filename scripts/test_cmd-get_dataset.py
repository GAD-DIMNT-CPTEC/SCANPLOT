#!/usr/bin/env python3
import scanplot as sc
from example_config import load

variables, config, output, figures = load()
start, end = config["Starting Time"], config["Ending Time"]
experiments = list(config["Experiments"])
stats = ["ACOR", "RMSE", "VIES"]
selected = list(variables.values())[:3]

data = sc.get_dataset(config, variables, ["RMSE", "VIES", "MEAN"], experiments,
                      output, save=True, missing="raise")
print(f"{len(data)} arquivos de campos.")
