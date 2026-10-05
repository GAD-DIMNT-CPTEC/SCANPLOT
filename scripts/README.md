# Scripts

Os exemplos Python (exceto Taylor) usam os dados versionados em
`test/SCANTEC.TESTS`, sem caminhos pessoais ou pickles previamente gerados.
Instale o projeto com `python -m pip install .` antes de executar os exemplos.

## Uso

```sh
python scripts/test_cmd-plot_lines.py --fig-dir /tmp/scanplot-figs
python scripts/test_cmd-plot_scorecard.py --fig-dir /tmp/scanplot-figs
python scripts/test_cmd-plot_lines_tStudent.py --fig-dir /tmp/scanplot-figs
python scripts/test_cmd-get_dataframe.py --base /caminho/SCANTEC
python scripts/test_cmd-get_dataset.py --base /caminho/SCANTEC --out-dir /caminho/campos
```

Os argumentos comuns sao `--base`, `--out-dir` e `--fig-dir`. Campos exigem
`pip install '.[fields]'` e arquivos Fortran reais, nao incluidos no repositorio.

O exemplo de Taylor e os scripts de submissao XC50 permanecem legados.
A validacao automatica esta em `tests/`: `python -m pytest -q`.
