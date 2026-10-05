#! /usr/bin/env python3

# SCANPLOT - Um sistema de plotagem simples para o SCANTEC
# Copyright (C) 2020 INPE
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import numpy as np
import pandas as pd
from scipy.stats import t

from data_structures import table_metadata


def isnotebook(shell):
    return shell == "ZMQInteractiveShell"


def concat_tables_and_loc(dTable, dataInicial, dataFinal, Exps, Var, series):
    """Select ACOR by exact experiment, retaining dates and forecast hours."""
    result = []
    first, last = dataInicial.strftime("%Y%m%d%H"), dataFinal.strftime("%Y%m%d%H")
    for experiment in Exps:
        pieces = {}
        for name, table in dTable.items():
            metadata = table_metadata(name)
            if metadata["stat"] != "ACOR" or metadata["experiment"] != experiment:
                continue
            if series:
                if metadata["start"] != metadata["end"] or not first <= metadata["start"] <= last:
                    continue
            elif (metadata["start"], metadata["end"]) != (first, last):
                continue
            column = Var if Var in table else Var.lower()
            selected = table.set_index("%Previsao")[column].sort_index()
            if selected.index.has_duplicates:
                raise ValueError(f"Prazos duplicados: {name}")
            date = pd.to_datetime(metadata["start"], format="%Y%m%d%H")
            if date in pieces:
                raise ValueError(f"Tabelas ambiguas para {experiment}: {date}")
            pieces[date] = selected
        if not pieces:
            raise ValueError(f"Nenhuma tabela ACOR encontrada para {experiment}.")
        if series:
            selected = pd.concat(pieces, names=["initialization", "forecast_hour"]).sort_index()
        else:
            selected = next(iter(pieces.values()))
            selected.index.name = "forecast_hour"
        result.append(selected)
    return result


def df_fill_nan(varlev_exps, varlev_dia_exps):
    """Align daily ACOR by initialization and lead, never by row position."""
    if not varlev_exps or len(varlev_exps) != len(varlev_dia_exps):
        raise ValueError("Informe series e tabelas de periodo para os mesmos experimentos.")
    frames = []
    for daily in varlev_dia_exps:
        if not isinstance(daily.index, pd.MultiIndex) or daily.index.nlevels != 2:
            raise ValueError("As series devem ter indices de inicializacao e prazo.")
        if daily.index.has_duplicates:
            raise ValueError("Inicializacoes e prazos duplicados.")
        frames.append(daily.unstack(level=1))
    dates = frames[0].index
    leads = varlev_exps[0].index
    for frame, period in zip(frames, varlev_exps):
        dates = dates.union(frame.index)
        leads = leads.union(frame.columns).union(period.index)
    return [frame.reindex(index=dates.sort_values(), columns=leads.sort_values())
            for frame in frames]


def calc_tStudent(lst_varlev_dia_exps_rsp):
    """Paired t interval (95%) for reference ACOR minus experiment ACOR.

    Returns mean differences and positive/negative half-widths around zero,
    preserving the historical plotting API. A difference outside these bounds
    corresponds to a paired confidence interval excluding zero.
    Pairs are aligned by date/lead and nonfinite values excluded pairwise.
    Fewer than two pairs yields NaN. Independent dates are assumed; temporal
    autocorrelation requires a separate effective-sample/block analysis.
    """
    if len(lst_varlev_dia_exps_rsp) < 2:
        raise ValueError("Sao necessarios ao menos dois experimentos.")
    reference = lst_varlev_dia_exps_rsp[0]
    means, upper, lower = [], [], []
    for experiment in lst_varlev_dia_exps_rsp[1:]:
        ref, exp = reference.align(experiment, join="outer")
        differences = (ref - exp).where(np.isfinite(ref) & np.isfinite(exp))
        n = differences.count()
        mean = differences.mean().where(n >= 2)
        half = pd.Series(t.ppf(0.975, n - 1), index=n.index) * differences.std(ddof=1) / np.sqrt(n)
        half = half.where(n >= 2)
        means.append(mean)
        upper.append(half)
        lower.append(-half)
    return means, upper, lower
