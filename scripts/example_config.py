"""Shared arguments for executable examples (install scanplot first)."""
import argparse
from pathlib import Path

import scanplot as sc


def load():
    parser = argparse.ArgumentParser()
    parser.add_argument('--base', type=Path, default=Path(__file__).resolve().parents[1] / 'test/SCANTEC.TESTS')
    parser.add_argument('--out-dir', type=Path)
    parser.add_argument('--fig-dir', type=Path)
    args = parser.parse_args()
    variables, config = sc.read_namelists(args.base)
    output = args.out_dir or args.base / 'dataout'
    figures = args.fig_dir or output / 'figs'
    return variables, config, output, figures
