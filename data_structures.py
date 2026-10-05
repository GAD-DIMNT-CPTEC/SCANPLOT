# SCANPLOT - Um sistema de plotagem simples para o SCANTEC
# CC-BY-NC-SA-4.0 2022 INPE
"""Readers for SCANTEC tables and sequential Fortran fields."""

from datetime import datetime, timedelta
from pathlib import Path
import pickle
import re
import warnings

import numpy as np
import pandas as pd
from scipy.io import FortranFile, FortranEOFError

import global_variables as gvars

_FILENAME = re.compile(
    r"^(?P<stat>[A-Z]{4})(?P<experiment>.+)_(?P<start>\d{10})"
    r"(?P<end>\d{10})(?P<kind>[TF])\.(?P<extension>scan|scam)$"
)


def table_metadata(name):
    """Parse identifiers without substring matches or fixed experiment lengths."""
    match = _FILENAME.fullmatch(Path(name).name)
    if match is None:
        raise ValueError(f"Nome SCANTEC invalido: {name}")
    return match.groupdict()


def _step(value):
    hours = float(value)
    if not np.isfinite(hours) or hours <= 0 or not hours.is_integer():
        raise ValueError("O passo temporal deve ser um numero inteiro positivo de horas.")
    return int(hours)


def _periods(start, end, series, step):
    if start > end:
        raise ValueError("A data inicial deve ser anterior ou igual a data final.")
    if not series:
        yield start, end
    else:
        while start <= end:
            yield start, start
            start += timedelta(hours=step)


def _missing(paths, policy):
    if policy not in ("warn", "raise", "ignore"):
        raise ValueError("missing deve ser 'warn', 'raise' ou 'ignore'.")
    if paths:
        message = f"{len(paths)} arquivo(s) SCANTEC ausente(s). Primeiro: {paths[0]}"
        if policy == "raise":
            raise FileNotFoundError(message)
        if policy == "warn":
            warnings.warn(message, UserWarning, stacklevel=3)


def get_dataframe(dataInicial, dataFinal, Stats, Exps, outDir, **kwargs):
    """Read tables indexed by forecast hour.

    series=True reads initialization cycles with analysis_step hours (default 24).
    Missing files are reported by default; missing='raise' enforces completeness.
    Undefined values (-999.9 by default) are converted to NaN.
    """
    series = kwargs.get("series", gvars.series)
    extension = kwargs.get("tExt", gvars.tExt)
    step = _step(kwargs.get("analysis_step", 24))
    policy = kwargs.get("missing", "warn")
    _missing([], policy)
    result, absent = {}, []
    root = Path(outDir).expanduser()
    for start, end in _periods(dataInicial, dataFinal, series, step):
        for stat in Stats:
            for experiment in Exps:
                name = f"{stat}{experiment}_{start:%Y%m%d%H}{end:%Y%m%d%H}T.{extension}"
                path = root / name
                if not path.is_file():
                    absent.append(path)
                    continue
                frame = pd.read_csv(path, sep=r"\s+", na_values=[kwargs.get("undef", -999.9)])
                if "%Previsao" not in frame:
                    raise ValueError(f"Coluna %Previsao ausente: {path}")
                frame = frame.apply(pd.to_numeric, errors="raise")
                lead = frame["%Previsao"]
                if lead.isna().any() or lead.duplicated().any() or (lead < 0).any():
                    raise ValueError(f"Prazos invalidos ou duplicados: {path}")
                frame = frame.sort_values("%Previsao")
                frame.index = pd.Index(frame["%Previsao"], name="forecast_hour")
                result[name] = frame
    _missing(absent, policy)
    if kwargs.get("save", gvars.save):
        suffix = "-series" if series else ""
        with (root / f"scantec_ds_table{suffix}.pkl").open("wb") as handle:
            pickle.dump(result, handle)
    return result


def get_dataset(data_conf, data_vars, Stats, Exps, outDir, **kwargs):
    """Read sequential float32 Fortran fields, one record per variable/lead.

    time is initialization + forecast_hour for forward evaluations, or
    verification - forecast_hour for backward evaluations. forecast_hour is
    always nonnegative; the evaluation period is retained in attributes.
    The supplied outDir takes precedence over the configuration.
    """
    import xarray as xr

    series = kwargs.get("series", gvars.series)
    extension = kwargs.get("tExt", gvars.tExt)
    step = _step(data_conf["Forecast Time Step"])
    analysis_step = _step(kwargs.get("analysis_step", data_conf["Analisys Time Step"]))
    total = int(data_conf["Forecast Total Time"])
    if total < 0 or total % step:
        raise ValueError("Forecast Total Time deve ser multiplo do passo de previsao.")
    leads = np.arange(0, total + 1, step)
    direction = data_conf.get("Time Step Type", "forward").strip().lower()
    if direction not in ("forward", "backward"):
        raise ValueError("Time Step Type deve ser forward ou backward.")
    sign = 1 if direction == "forward" else -1

    def axis(lower, upper, resolution):
        lo, hi, delta = (float(data_conf[key]) for key in (lower, upper, resolution))
        if delta <= 0 or hi < lo:
            raise ValueError("Limites ou resolucao espacial invalidos.")
        # Some legacy domains end between grid points; preserve the grid spacing.
        count = int(np.floor((hi - lo) / delta + 1e-6)) + 1
        return lo + np.arange(count) * delta

    lats = axis("run domain lower left lat", "run domain upper right lat",
                "run domain resolution dy")
    lons = axis("run domain lower left lon", "run domain upper right lon",
                "run domain resolution dx")
    variables = [value[0] for value in data_vars.values()]
    if not variables or len(set(variables)) != len(variables):
        raise ValueError("A lista de variaveis deve ser nao vazia e sem duplicatas.")
    root = Path(outDir).expanduser()
    start, end = data_conf["Starting Time"], data_conf["Ending Time"]
    policy = kwargs.get("missing", "warn")
    _missing([], policy)
    result, absent = {}, []
    for initial, final in _periods(start, end, series, analysis_step):
        for stat in Stats:
            for experiment in Exps:
                name = f"{stat}{experiment}_{initial:%Y%m%d%H}{final:%Y%m%d%H}F.{extension}"
                path = root / name
                if not path.is_file():
                    absent.append(path)
                    continue
                values = {v: [] for v in variables}
                try:
                    with FortranFile(path, "r") as handle:
                        for lead in leads:
                            for variable in variables:
                                field = handle.read_reals(np.float32)
                                if field.size != len(lats) * len(lons):
                                    raise ValueError(f"Dimensoes incompativeis: {path}")
                                field = field.reshape((len(lats), len(lons)))
                                field[field == np.float32(kwargs.get("undef", -999.9))] = np.nan
                                values[variable].append(field)
                        try:
                            handle.read_reals(np.float32)
                        except FortranEOFError:
                            pass
                        else:
                            raise ValueError(f"Registros excedentes: {path}")
                except (OSError, ValueError) as exc:
                    raise ValueError(f"Arquivo de campos invalido ou incompleto: {path}: {exc}") from exc
                times = [initial + timedelta(hours=sign * int(lead)) for lead in leads]
                result[name] = xr.Dataset(
                    {v: (("time", "lat", "lon"), np.stack(values[v])) for v in variables},
                    coords={"time": times, "forecast_hour": ("time", leads),
                            "lat": lats, "lon": lons},
                    attrs={"period_start": initial.isoformat(), "period_end": final.isoformat(),
                           "experiment": experiment, "statistic": stat,
                           "time_step_type": direction},
                )
    _missing(absent, policy)
    if kwargs.get("save", gvars.save):
        suffix = "-series" if series else ""
        with (root / f"scantec_ds_field{suffix}.pkl").open("wb") as handle:
            pickle.dump(result, handle)
    return result
