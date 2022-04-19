 O módulo `scanplot` possui as seguintes funções:

1. `read_namelists`: esta função lê os arquivos de namelist e definições dos modelos do SCANTEC;
2. `get_dataframe`: esta função transforma uma ou mais tabelas em dataframes do Pandas, acessíveis por meio de um dicionário;
3. `plot_lines`: esta função plota gráficos de linhas a partir dos dataframes;
4. `plot_lines_tStudent`: esta função plota gráficos de linhas a partir dos dataframes, acompanhados do teste de significância t de Student;
5. `plot_scorecard`: esta função plota um scorecard a partir dos dataframes;
6. `plot_dTaylor`: esta função plota um diagrama de Taylor a partir dos dataframes.

As funções possuem formas específicas de utilização. Para saber como utilizá-las, carregue primeiro o módulo `scanplot`:

=== "Comando"

    ```Python linenums="1"
    import scanplot
    ```

ou 

=== "Comando"

    ```Python linenums="1"
    import scanplot as sc
    ```

E em seguida, acesse a documentação da função digitando uma das duas formas a seguir:

=== "Comando"

    ```Python linenums="1"
    help(read_namelists)
    ```

ou

=== "Comando"

    ```Python linenums="1"
    print(red_namelists.__doc__)
    ```
