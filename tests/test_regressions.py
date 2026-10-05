from datetime import datetime, timedelta
from pathlib import Path
import subprocess
import sys

import numpy as np
import pandas as pd
import pytest
import matplotlib.pyplot as plt
from scipy.io import FortranFile
from scipy.stats import ttest_rel

import scanplot as sc
from plot_functions import scorecard_values

ROOT = Path(__file__).resolve().parents[1]


def table(values, leads=(0, 24, 48)):
    return pd.DataFrame({'%Previsao': leads, 'x': values})


def name(stat='ACOR', exp='A', start='2020010100', end='2020010300', kind='T'):
    return f'{stat}{exp}_{start}{end}{kind}.scan'


def test_real_tables_and_batch(tmp_path):
    variables, conf = sc.read_namelists(ROOT / 'test/SCANTEC.TESTS')
    frames = sc.get_dataframe(conf['Starting Time'], conf['Ending Time'],
                              ['ACOR', 'RMSE', 'VIES'], list(conf['Experiments']),
                              ROOT / 'test/SCANTEC.TESTS/dataout', missing='raise')
    assert len(variables) == 17 and len(frames) == 12
    before = plt.get_fignums()
    figures = sc.plot_lines(frames, [variables[0]], ['ACOR'], tmp_path,
                            saveFig=True, combine=True)
    assert len(figures) == len(list(tmp_path.glob('*.png'))) == 1
    assert list(figures[0].axes[0].lines[0].get_xdata()) == list(range(0, 361, 24))
    assert plt.get_fignums() == before


@pytest.mark.parametrize('combine,expected', [(False, 2), (True, 1)])
def test_line_forecast_alignment_and_closure(tmp_path, combine, expected):
    frames = {name():table([0.5, 0.6, 0.7]), name(exp='B'):table([0.3, 0.4], (0, 48))}
    figures = sc.plot_lines(frames, [('x', 'X')], ['ACOR'], tmp_path,
                            figDir=tmp_path / 'new', saveFig=True, combine=combine)
    assert len(figures) == expected
    assert len(list((tmp_path / 'new').glob('*.png'))) == expected
    assert not plt.get_fignums()


def test_subdaily_reader_and_undefined(tmp_path):
    for hour in (0, 6, 12):
        stamp = f'20200101{hour:02}'
        table([1, -999.9, 3]).to_csv(tmp_path / name(start=stamp, end=stamp), sep=' ', index=False)
    frames = sc.get_dataframe(datetime(2020,1,1), datetime(2020,1,1,12),
                              ['ACOR'], ['A'], tmp_path, series=True, analysis_step=6)
    assert len(frames) == 3
    assert all(np.isnan(frame.loc[24, 'x']) for frame in frames.values())
    with pytest.raises(FileNotFoundError):
        sc.get_dataframe(datetime(2020,1,1), datetime(2020,1,2), ['RMSE'], ['A'], tmp_path, missing='raise')
    with pytest.warns(UserWarning, match='ausente'):
        assert sc.get_dataframe(datetime(2020,1,1), datetime(2020,1,2), ['RMSE'], ['A'], tmp_path) == {}


def test_dates_and_exact_experiment_matching():
    daily = {}
    for exp, days in [('A', (1, 2)), ('AA', (2, 3))]:
        for day in days:
            stamp = f'2020010{day}00'
            daily[name(exp=exp, start=stamp, end=stamp)] = table([day, day + 1], (0,24))
    start, end = datetime(2020,1,1), datetime(2020,1,3)
    series = sc.concat_tables_and_loc(daily, start, end, ['A','AA'], 'x', True)
    period = [pd.Series([1,2], index=[0,24])] * 2
    aligned = sc.df_fill_nan(period, series)
    assert aligned[0].shape == aligned[1].shape == (3, 2)
    assert aligned[0].loc['2020-01-03'].isna().all()
    assert aligned[1].loc['2020-01-01'].isna().all()
    assert aligned[0].loc['2020-01-02',24] == aligned[1].loc['2020-01-02',24] == 3


def test_paired_interval_matches_scipy():
    dates = pd.date_range('2020-01-01', periods=5)
    ref = pd.DataFrame({24:[.1,.2,.3,.4,.5]}, index=dates)
    exp = pd.DataFrame({24:[.5,.4,.3,.2,.1]}, index=dates)
    mean, upper, lower = sc.calc_tStudent([ref, exp.iloc[::-1]])
    interval = ttest_rel(ref[24], exp[24]).confidence_interval()
    assert mean[0][24] == pytest.approx(0)
    assert upper[0][24] == pytest.approx(interval.high)
    assert lower[0][24] == pytest.approx(interval.low)
    assert np.isfinite(upper[0][24])


def test_paired_missing_and_constant_difference():
    ref = pd.DataFrame({24:[.5,.6,.7], 48:[.1,np.nan,np.nan]})
    exp = pd.DataFrame({24:[.25,.35,.45], 48:[.0,.2,.3]})
    mean, upper, lower = sc.calc_tStudent([ref, exp])
    assert mean[0][24] == pytest.approx(.25)
    assert upper[0][24] == pytest.approx(0, abs=1e-15)
    assert np.isnan(mean[0][48]) and np.isnan(upper[0][48])


@pytest.mark.parametrize('stat,kind,left,right,expected', [
    ('VIES','ganho',1,-2,-100), ('VIES','ganho',-2,1,50),
    ('RMSE','ganho',2,1,50), ('ACOR','ganho',.5,.75,50),
    ('ACOR','fc',.5,.75,.5), ('VIES','fc',1,-2,-1),
])
def test_scorecard_direction(stat, kind, left, right, expected):
    result = scorecard_values(pd.DataFrame([[left]]), pd.DataFrame([[right]]), stat, kind)
    assert result.iloc[0,0] == pytest.approx(expected)


@pytest.mark.parametrize('stat,kind,baseline', [('VIES','ganho',0), ('RMSE','fc',0), ('ACOR','ganho',1)])
def test_scorecard_undefined(stat, kind, baseline):
    result = scorecard_values(pd.DataFrame([[baseline]]), pd.DataFrame([[.2]]), stat, kind)
    assert np.isnan(result.iloc[0,0])


def test_scorecard_exact_names(tmp_path):
    frames = {name('VIES','AA'):table([0,10,10]), name('VIES','A'):table([0,1,1]),
              name('VIES','B'):table([0,-2,-2])}
    figures = sc.plot_scorecard(frames, [('x','X')], ['VIES'], 'ganho', ['A','B'],
                               tmp_path, saveFig=True)
    assert np.all(figures[0].axes[0].collections[0].get_array() == -100)
    assert len(list(tmp_path.glob('*.png'))) == 1
    assert not plt.get_fignums()


def config(tmp_path, end=datetime(2020,1,1)):
    return {'Starting Time':datetime(2020,1,1), 'Ending Time':end,
            'Forecast Total Time':'48', 'Forecast Time Step':'24', 'Analisys Time Step':'6',
            'run domain lower left lat':'0', 'run domain upper right lat':'1',
            'run domain lower left lon':'0', 'run domain upper right lon':'2',
            'run domain resolution dx':'1', 'run domain resolution dy':'1',
            'Output directory':'/not/used', 'Time Step Type':'forward'}


def binary(tmp_path, initial='2020010100', final=None, records=6):
    path = tmp_path / name('RMSE', 'A', initial, final or initial, 'F')
    with FortranFile(path, 'w') as handle:
        for i in range(records):
            handle.write_record(np.arange(6, dtype='f4') + i * 10)
    return path


def test_fields_records_orientation_and_times(tmp_path):
    pytest.importorskip('xarray')
    binary(tmp_path)
    datasets = sc.get_dataset(config(tmp_path), {0:('x','X'),1:('y','Y')}, ['RMSE'], ['A'], tmp_path)
    dataset = next(iter(datasets.values()))
    assert dataset.x.dims == ('time','lat','lon')
    np.testing.assert_array_equal(dataset.x[1], [[20,21,22],[23,24,25]])
    np.testing.assert_array_equal(dataset.y[2], [[50,51,52],[53,54,55]])
    np.testing.assert_array_equal(dataset.forecast_hour, [0,24,48])
    assert pd.Timestamp(dataset.time.values[-1]) == pd.Timestamp('2020-01-03')


def test_field_series_rebases_time(tmp_path):
    pytest.importorskip('xarray')
    for stamp in ('2020010100','2020010106'):
        binary(tmp_path, stamp)
    data = sc.get_dataset(config(tmp_path, datetime(2020,1,1,6)), {0:('x','X'),1:('y','Y')},
                          ['RMSE'], ['A'], tmp_path, series=True)
    assert len(data) == 2
    assert pd.Timestamp(list(data.values())[1].time.values[0]) == pd.Timestamp('2020-01-01 06:00')


@pytest.mark.parametrize('records', [5, 7])
def test_incomplete_or_extra_fields(tmp_path, records):
    pytest.importorskip('xarray')
    binary(tmp_path, records=records)
    with pytest.raises(ValueError, match='invalido|incompleto'):
        sc.get_dataset(config(tmp_path), {0:('x','X'),1:('y','Y')}, ['RMSE'], ['A'], tmp_path)


@pytest.mark.parametrize('combine,expected', [(False,6),(True,3)])
def test_plot_all_fields_and_last_time(tmp_path, monkeypatch, combine, expected):
    xr = pytest.importorskip('xarray')
    geoaxes = pytest.importorskip('cartopy.mpl.geoaxes')
    monkeypatch.setattr(geoaxes.GeoAxes, 'coastlines', lambda *args, **kwargs: None)
    dataset = xr.Dataset({'x':(('time','lat','lon'),np.arange(18).reshape(3,2,3))},
                        coords={'time':pd.date_range('2020-01-01', periods=3),
                                'forecast_hour':('time',[0,24,48]),'lat':[0,1],'lon':[0,1,2]})
    data = {name('RMSE','A',kind='F'):dataset, name('RMSE','B',kind='F'):dataset}
    figures = sc.plot_fields(data, [('x','X')], ['RMSE'], tmp_path, combine=combine, saveFig=True)
    assert len(figures) == len(list(tmp_path.glob('*.png'))) == expected
    assert not plt.get_fignums()


def test_optional_modules_not_required():
    code = '''
import sys
class Block:
    def find_spec(self, fullname, *args):
        if fullname.split('.')[0] in {'panel','param','cartopy','xarray','hvplot','holoviews','tkinter','IPython'}:
            raise ImportError(fullname)
sys.meta_path.insert(0, Block())
import scanplot
assert callable(scanplot.get_dataframe)
'''
    subprocess.run([sys.executable, '-c', code], check=True)


def test_gui_real_callback(tmp_path):
    pn = pytest.importorskip('panel')
    from gui_functions import create_interface
    template = create_interface()
    widgets = {item.name:item for item in template.sidebar if isinstance(item, pn.widgets.Widget)}
    widgets['Diretorio SCANTEC'].value = str(ROOT / 'test/SCANTEC.TESTS')
    widgets['Carregar'].clicks += 1
    assert not widgets['Plotar'].disabled
    widgets['Plotar'].clicks += 1
    assert template.main[0].alert_type == 'success'
    assert len(template.main[1]) == 1


def test_single_time_and_interactive_all_files(tmp_path, monkeypatch):
    xr = pytest.importorskip('xarray')
    pn = pytest.importorskip('panel')
    geoaxes = pytest.importorskip('cartopy.mpl.geoaxes')
    pytest.importorskip('geoviews')
    monkeypatch.setattr(geoaxes.GeoAxes, 'coastlines', lambda *args, **kwargs: None)
    dataset = xr.Dataset({'x':(('time','lat','lon'),np.arange(6).reshape(1,2,3))},
                        coords={'time':[pd.Timestamp('2020-01-01')],
                                'forecast_hour':('time',[0]),'lat':[0,1],'lon':[0,1,2]})
    data = {name('RMSE','A',kind='F'):dataset, name('RMSE','B',kind='F'):dataset}
    figures = sc.plot_fields(data, [('x','X')], ['RMSE'], tmp_path, saveFig=True)
    assert len(figures) == len(list(tmp_path.glob('*.png'))) == 2
    for combine, layout_type in [(False,pn.Column), (True,pn.Row)]:
        layout = sc.plot_fields(data, [('x','X')], ['RMSE'], tmp_path, hvplot=True, combine=combine)
        assert isinstance(layout, layout_type) and len(layout) == 2
    with pytest.raises(ValueError, match='saveFig'):
        sc.plot_fields(data, [('x','X')], ['RMSE'], tmp_path, hvplot=True, saveFig=True)


def test_tstudent_plot_real_leads(tmp_path):
    series = [pd.Series([.5,.4], index=[24,72]), pd.Series([.4,.3], index=[24,72])]
    means = [pd.Series([.1,.1], index=[24,72])]
    upper = [pd.Series([.05,.05], index=[24,72])]
    figures = sc.plot_lines_tStudent(datetime(2020,1,1), datetime(2020,1,3), {},
        ['A','B'], 'x', 'X', means, upper, [-upper[0]], series, tmp_path, saveFig=True)
    np.testing.assert_array_equal(figures[0].axes[1].lines[0].get_xdata(), [24,72])
    assert not plt.get_fignums()


def test_confidence_panels_center_intervals_on_means(tmp_path):
    curves = [pd.Series([.8,.7], index=[24,72])] * 3
    means = [pd.Series([.1,.2], index=[24,72]), pd.Series([-.2,-.3], index=[24,72])]
    upper = [pd.Series([.04,.03], index=[72,24])] * 2
    lower = [-value for value in upper]
    originals = [value.copy() for value in means + upper + lower]
    figures = sc.plot_lines_tStudent(datetime(2020,1,1), datetime(2020,1,3), {},
        ['A','B','C'], 'x', 'X', means, upper, lower, curves, tmp_path)
    axes = figures[0].axes
    assert len(axes) == 3
    for ax, mean in zip(axes[1:], means):
        vertices = ax.collections[0].get_paths()[0].vertices
        assert vertices[:,1].min() == pytest.approx((mean + lower[0]).min())
        assert vertices[:,1].max() == pytest.approx((mean + upper[0]).max())
        assert ax.get_ylim()[0] < vertices[:,1].min()
        assert ax.get_ylim()[1] > vertices[:,1].max()
        np.testing.assert_array_equal(ax.lines[0].get_ydata(), mean)
        np.testing.assert_array_equal(ax.lines[1].get_ydata(), [0,0])
    assert axes[1].get_title() == 'A - B'
    assert axes[2].get_title() == 'A - C'
    assert axes[1].get_ylim() == axes[2].get_ylim()
    for actual, original in zip(means + upper + lower, originals):
        pd.testing.assert_series_equal(actual, original)
    assert not plt.get_fignums()


def test_backward_and_grid_spacing(tmp_path):
    pytest.importorskip('xarray')
    binary(tmp_path)
    conf = config(tmp_path)
    conf['Time Step Type'] = 'backward'
    conf['run domain upper right lon'] = '2.5'
    data = sc.get_dataset(conf, {0:('x','X'),1:('y','Y')}, ['RMSE'], ['A'], tmp_path)
    dataset = next(iter(data.values()))
    np.testing.assert_array_equal(dataset.lon, [0,1,2])
    assert pd.Timestamp(dataset.time.values[-1]) == pd.Timestamp('2019-12-30')


def test_legacy_table_extension(tmp_path):
    path = tmp_path / name().replace('.scan', '.scam')
    frame = table([.1,.2,.3]).rename(columns={'x':'X'})
    frame.to_csv(path, sep=' ', index=False)
    frames = sc.get_dataframe(datetime(2020,1,1), datetime(2020,1,3), ['ACOR'], ['A'],
                              tmp_path, tExt='scam', missing='raise')
    series = sc.concat_tables_and_loc(frames, datetime(2020,1,1), datetime(2020,1,3), ['A'], 'X', False)
    np.testing.assert_array_equal(series[0], [.1,.2,.3])
