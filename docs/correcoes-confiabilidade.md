# Correcoes de confiabilidade (issue #31)

Esta entrega corrige a instalacao, leitura, comparacao e plotagem do SCANPLOT.
O calculo do diagrama de Taylor permanece experimental e nao foi modificado;
sua validacao continua na issue #11.

## Instalacao e exemplos

```sh
python -m pip install .
python -m pip install '.[fields]'  # campos espaciais
python -m pip install '.[gui]'     # interface e campos interativos
python scripts/test_cmd-plot_lines.py --fig-dir /tmp/scanplot-figs
panel serve SCANPLOT_panel_app.py --show
```

Os exemplos usam as tabelas versionadas em `test/SCANTEC.TESTS`. Todos os
exemplos atualizados aceitam `--base`, `--out-dir` e `--fig-dir`. O exemplo
`get_dataset` exige arquivos binarios reais no diretorio informado: esses
arquivos nao estao incluidos no repositorio. O exemplo legado de Taylor nao
faz parte desta atualizacao.

Para testes: `python -m pip install '.[test,gui]'` e `python -m pytest -q`.
O workflow Tests verifica Python 3.10 e 3.13 e importa o wheel fora do checkout.

## Contrato dos dados

- `get_dataframe` conserva `%Previsao` como coluna e tambem o utiliza como
  indice `forecast_hour`, ordenado e sem duplicatas. Se o consumidor precisa
  de posicoes em vez de prazos, deve usar `iloc`.
- `series=True` aceita `analysis_step` (horas, padrao 24); passe
  `data_conf['Analisys Time Step']` para ciclos subdiarios.
- `missing='warn'` informa arquivos ausentes; `'raise'` exige completude;
  `'ignore'` permite omissao deliberada. Ausencia nao e convertida em zero.
- `undef` tem padrao -999.9 e pode ser informado para outras sentinelas.
- A extensao pode ser definida por `tExt='scan'` ou `'scam'` em cada chamada;
  os leitores nao alteram o estado global. Passe a opcao explicitamente em
  consumidores legados que dependiam dessa alteracao implicita.
- `concat_tables_and_loc` seleciona ACOR por identificador exato. Em series,
  o indice e `(initialization, forecast_hour)`; `df_fill_nan` alinha datas e
  prazos por esses valores. Nao ha reshape por posicao ou preenchimento de
  uma data ausente com observacoes de outra data.
- `get_dataset` respeita `outDir`, le um registro Fortran float32 por variavel
  e prazo e verifica arquivos incompletos/excedentes. O passo de previsao,
  nao o de analise, determina a quantidade de registros. O formato pressupoe
  marcadores sequenciais e endianness nativos; outros formatos exigem adaptacao.
- Campos possuem dimensoes `(time, lat, lon)` e coordenada `forecast_hour`.
  Em avaliacao forward, time ancora o inicio do periodo mais o prazo;
  em backward, o inicio do periodo menos o prazo. Para series, a ancora e
  atualizada a cada ciclo. Em estatisticas agregadas, time e uma coordenada
  representativa: os atributos `period_start`/`period_end` preservam o periodo.
- As coordenadas espaciais preservam a resolucao declarada, inclusive quando
  o limite superior de um dominio legado cai entre pontos da grade.

## Significancia

O estimador passa a ser a media da diferenca pareada de ACOR:

`d = ACOR_referencia - ACOR_experimento`.

Para cada prazo, usam-se somente datas com os dois valores finitos.
Com n pares, o intervalo bilateral de 95% e
`media(d) +/- t(0.975, n-1) * std(d, ddof=1) / sqrt(n)`.
Menos de dois pares produz NaN. Uma diferenca constante com dois ou mais
pares tem largura zero. A API retorna media, meia-largura positiva e negativa;
o grafico soma essas meias-larguras a diferenca media para mostrar o intervalo
de confianca em torno da curva. Cada comparacao tem seu proprio painel,
com a mesma escala vertical entre paineis de diferencas. Quando o intervalo
nao cruza zero, a diferenca e significativa a 5% naquele prazo. Diferencas
negativas indicam maior ACOR do experimento comparado que a referencia.

Esse teste assume diferencas aproximadamente normais (ou amostra adequada
para aproximacao) e independentes entre datas. Nao corrige autocorrelacao,
comparacoes multiplas nem estima tamanho efetivo de amostra. Para inferencia
operacional com dependencia temporal, e necessario definir uma estrategia
adicional, como reamostragem em blocos. A transformacao anterior da diferenca
de correlacoes e o uso do p-valor como quantil foram removidos.

## Scorecards

Valores positivos sempre indicam melhora do segundo experimento:

| Estatistica | ganho (percentual) | fc (fracao) |
|---|---|---|
| ACOR | 100 * (exp-ref)/(1-ref) | (exp-ref)/abs(ref) |
| RMSE | 100 * (abs(ref)-abs(exp))/abs(ref) | (abs(ref)-abs(exp))/abs(ref) |
| VIES | 100 * (abs(ref)-abs(exp))/abs(ref) | (abs(ref)-abs(exp))/abs(ref) |

A mudanca de magnitude do vies mede aproximacao a zero, nao mudanca assinada.
Denominadores zero e dados ausentes ficam mascarados. O prazo zero continua
excluido do scorecard, agora por seu valor (0 h), nao pela posicao da linha.
O formato fc usa duas casas decimais. Valores fora da escala permanecem nas
anotacoes mesmo que a cor esteja saturada. Nao foi acrescentado teste de
significancia aos scorecards (issues #12/#15).

## Graficos e interface

Linhas usam os prazos reais de cada experimento. Figuras estaticas sao
retornadas em listas, salvas quando solicitado e retiradas do registro global
do pyplot apos o uso; continuam disponiveis para incorporacao em Panel.
Campos estaticos cobrem o ultimo prazo e um unico prazo. `combine=True`
agrupa arquivos em paineis por variavel/prazo; `hvplot=True` retorna layout
interativo com todos os arquivos. Exportacao PNG no modo interativo gera
erro explicito: use o modo estatico para salvar.

`show_interface(show=False)` constroi a interface sem iniciar servidor.
O aplicativo e a API compartilham `create_interface`; nao utilizam Tkinter
nem caminhos pessoais. A interface oferece linhas, significancia, scorecards
e campos. Taylor nao e oferecido como funcionalidade validada.

## Limites da verificacao

Os testes usam tabelas reais versionadas, campos Fortran sinteticos, comparacao
do intervalo pareado com SciPy e callbacks reais do Panel. Nos testes de mapas,
a chamada de contornos costeiros e substituida para evitar download de Natural
Earth. Isso nao valida dados operacionais, todos os formatos legados ou a
consistencia cientifica do Taylor. Os documentos e notebooks historicos podem
descrever o comportamento anterior; este documento registra as mudancas de API.
