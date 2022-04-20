# Leitura dos namelists do SCANTEC

O SCANTEC é um software de linha de comando escrito em linguagem Fortran preparado para ler, interpolar e calcular as estatísticas básicas (Viés, Raiz do Erro Quadrático Médio e Correlação de Anomalias) a partir dos resultados de modelos de previsão numérica de tempo, como os modelos BAM, BRAMS e Eta. O SCANPLOT faz o trabalho de criar as estruturas de dados adequadas e plotar os resultados. As estruturas de dados criadas pelo SCANPLOT, são determinadas a partir das tabelas com o resumo das estatísticas calculadas pelo SCANTEC. Para utilizar o SCANPLOT, o usuário deve ler os arquivos de namelist e definições dos modelos utilizados nas avaliações, de forma que o software saiba quais foram as definições utilizadas pelo usuário e em que local estão armazenadas as tabelas com os resultados.

Para isso, basta utilizar a função `read_namelists` a partir do módulo principal `scanplot`. A função `read_namelists` está implementada no script [`core_scanplot.py`](https://github.com/cfbastarz/SCANPLOT/blob/master/core_scanplot.py) do SCANPLOT. Esta e as demais funções, podem ser acessadas a partir do módulo principal, o qual deverá ser carregado:


=== "Comando"

    ```python linenums="1"
    import scanplot
    ```

Para conhecer como deve ser utilizada a função `read_namelists`, o usuário pode utilizar um dos comandos a seguir:

=== "Comando"

    ```python linenums="1"
    help(scanplot.read_namelists)
    ```

=== "Resultado"

    ```python linenums="1"
    Help on function read_namelists in module core_scanplot:
    
    read_namelists(basepath)
        read_namelists
        ==============
        
        Esta função lê os namelists e arquivos de definições dos modelos do SCANTEC e
        retorna para o usuário dois dicionários, VarsLevs e Confs, com as informações lidas.
        
        Parâmetros de entrada
        ---------------------
            basepath : diretório raiz da instalação do SCANTEC.
            
        Resultados
        ----------
            VarsLevs : dicionário com as variáveis, níveis e nomes definidos no arquivo scantec.vars;
            Confs    : dicionário com as definições contidas no arquivo scantec.conf.
        
        Uso
        ---
            import scanplot
            
            data_vars, data_conf = scanplot.read_namelists("~/SCANTEC")
    ```


A função `read_namelists` recebe um caminho (raiz da instalação do SCANTEC, no exemplo `/scripts/ensemble/SCANTEC.TESTS`) como parâmetro de entrada e retorna para o usuário dois dicionários, os quais contém as informações dos arquivos `scantec.conf` e `scantec.vars` do SCANTEC. Estes arquivos possuem as definições dos modelos (intervalo de tempo da avalação, nome do modelo, resolução, caminhos etc). Os nomes `data_vars` e `data_conf` são os nomes dos objetos que serão criados e que conterão os dicionários com as definições dos arquivos `scantec.vars` e `scantec.conf`, respectivamente. A escolha destes nomes fica a critério do usuário.

!!! info "Informação"

    Um dicionário é uma estrutura de dados associativa.


=== "Comando"

    ```python linenums="1"
    data_vars, data_conf = scanplot.read_namelists('/scripts/ensemble/SCANTEC.TESTS')
    ```

Para inspecionar o conteúdo e a estrutura dos dados contidos nos objetos `data_conf` e `data_vars`, basta digitar os nomes no prompt:

=== "Comando"

    ```python linenums="1"
    data_conf
    ```

=== "Resultado"

    ```python linenums="1"
    {'Starting Time': datetime.datetime(2020, 6, 1, 0, 0),
     'Ending Time': datetime.datetime(2020, 8, 15, 0, 0),
     'Analisys Time Step': '24',
     'Forecast Time Step': '24',
     'Forecast Total Time': '360',
     'Time Step Type': 'forward',
     'History Time': '48',
     'scantec tables': '/scripts/ensemble/SCANTEC.TESTS/tables',
     'run domain number': '1',
     'run domain lower left lat': '-80',
     'run domain lower left lon': '0',
     'run domain upper right lat': '80',
     'run domain upper right lon': '360',
     'run domain resolution dx': '0.9375000000',
     'run domain resolution dy': '0.9375000000',
     'Reference Model Name': 'GFS_0p25_5levs',
     'Reference file': '/lustre_xc50/carlos_bastarz/GFS_subset/%iy4%im2%id2%ih2/gfs.t00z.pgrb2.0p25.f000.%iy4%im2%id2%ih2.ctl',
     'Experiments': {'X126': ['BAM_TQ0126L028_9levs',
       '/lustre_xc50/carlos_bastarz/oensMB09_test_preXC50/pos/dataout/TQ0126L028/%iy4%im2%id2%ih2/NMC/GPOSNMC%iy4%im2%id2%ih2%fy4%fm2%fd2%fh2P.fct.TQ0126L028.ctl'],
      'XENM': ['BAM_TQ0126L028_9levs',
       '/lustre_xc50/carlos_bastarz/oensMB09_test_preXC50/ensmed/dataout/TQ0126L028/%iy4%im2%id2%ih2/GPOSENM%iy4%im2%id2%ih2%fy4%fm2%fd2%fh2P.fct.TQ0126L028.ctl'],
      'T126': ['BAM_TQ0126L028_9levs',
       '/lustre_xc50/carlos_bastarz/from_tupa/dados/ensemble/dsk001/oens_MB09_tupa/pos/dataout/TQ0126L028/%iy4%im2%id2%ih2/NMC/GPOSNMC%iy4%im2%id2%ih2%fy4%fm2%fd2%fh2P.fct.TQ0126L028.ctl'],
      'TENM': ['BAM_TQ0126L028_9levs',
       '/lustre_xc50/carlos_bastarz/from_tupa/dados/ensemble/dsk001/oens_MB09_tupa/ensmed/dataout/TQ0126L028/%iy4%im2%id2%ih2/GPOSENM%iy4%im2%id2%ih2%fy4%fm2%fd2%fh2P.fct.TQ0126L028.ctl']},
     'Climatology Model Name': 'AGCM_TQ0062L028_50YR_CLIMATOLOGY_18levs',
     'Climatology file': '/lustre_xc50/carlos_bastarz/climatologia/climatologia50yr.%mc.ctl',
     'Output directory': '/scripts/ensemble/SCANTEC.TESTS/dataout'}
    ```

Da mesma forma com `data_vars`:

=== "Comando"

    ```python linenums="1"
    data_vars
    ```

=== "Resultado"

    ```python linenums="1"
    {0: ('PSNM:000', 'Pressão Reduzida ao Nível Médio do Mar [hPa]'),
     1: ('TEMP:850', 'Temperatura Absoluta @ 850 hPa [K]'),
     2: ('TEMP:500', 'Temperatura Absoluta @ 500 hPa [K]'),
     3: ('TEMP:250', 'Temperatura Absoluta @ 250 hPa [K]'),
     4: ('UMES:925', 'Umidade Específica @ 925 hPa [g/Kg]'),
     5: ('UMES:850', 'Umidade Específica @ 850 hPa [g/Kg]'),
     6: ('UMES:500', 'Umidade Específica @ 500 hPa [g/Kg]'),
     7: ('AGPL:925', 'Água Precipitável @ 925 hPa [Kg/m2]'),
     8: ('ZGEO:850', 'Altura Geopotencial @ 850 hPa [gpm]'),
     9: ('ZGEO:500', 'Altura Geopotencial @ 500 hPa [gpm]'),
     10: ('ZGEO:250', 'Altura Geopotencial @ 250 hPa [gpm]'),
     11: ('UVEL:850', 'Vento Zonal @ 850 hPa [m/s]'),
     12: ('UVEL:500', 'Vento Zonal @ 500 hPa [m/s]'),
     13: ('UVEL:250', 'Vento Zonal @ 250 hPa [m/s]'),
     14: ('VVEL:850', 'Vento Meridional @ 850 hPa [m/s]'),
     15: ('VVEL:500', 'Vento Meridional @ 500 hPa [m/s]'),
     16: ('VVEL:250', 'Vento Meridional @ 250 hPa [m/s]')}
    ```
