# Instalação

Para a instalação do SCANPLOT, recomenda-se a utilização da distribuição Anaconda. Para instalar o Anaconda, acesse [https://www.anaconda.com/products/distribution](https://www.anaconda.com/products/distribution), baixe o pacote e realize a instalação da distribuição no seu computador. Esta etapa é importante, pois no repositório do SCANPLOT, há um arquivo com a definição do ambiente que será utilizado para a instalação de todas as dependências.

## Ambiente do Python para o SCANPLOT

O Python permite a criação de ambientes que podem ser utilizados para o desenvolvimento de aplicações que requerem diferentes versões de determinadas bibliotecas do Python. O Anaconda fornece o gerenciador de pacotes `conda` que será utilizado nesse processo.

Para criar um ambiente apropriado para o uso do SCANPLOT, utilize o comando a seguir:

=== "Comando"

    ```bash linenums="1"
    conda env create -f environment.yml
    ```

!!! warning "Atenção"

    A instalação de todos os pacotes do ambiente requer aproximadamente 2,8 GB de espaço em disco.

Após a instalação dos pacotes, basta ativar o ambiente recém criado com o comando:

=== "Comando"

    ```bash linenums="1"
    conda activate SCANPLOT
    ```

Nesta etapa, todos os pacotes necessário para uso e desenvolvimento do SCANPLOT já estão disponíveis.

## Obtenção do SCANPLOT

Para obter uma cópia do SCANPLOT para uso e desenvolvimento em máquina local, utilize o comando a seguir[^1]:

=== "Comando"

    ```bash linenums="1"
    gh repo clone GAM-DIMNT-CPTEC/SCANPLOT
    ```

Alternativamente, uma cópia do SCANPLOT pode ser obtida com o seguinte comando[^2]:

=== "Comando"

    ```bash linenums="1"
    wget -c https://github.com/GAM-DIMNT-CPTEC/SCANPLOT/archive/refs/heads/master.zip
    ```

## Instalação do SCANPLOT

Com uma cópia local do código do SCANPLOT, entre do diretório principal da instalação e execute o comando a seguir:

=== "Comando"

    ```bash linenums="1"
    pip install -e .
    ```

!!! warning "Atenção"

    Este comando deve ser executado dentro do ambiente SCANPLOT criado nas etapas anteriores!

Caso o comando de instalação do SCANPLOT falhe, pode-se prosseguir exportando a variável de ambiente `PYTHONPATH` com o caminho onde se encontra o código do SCANPLOT:

=== "Comando"

    ```bash linenums="1"
    export PYTHONPATH=/caminho/instalacao/SCANPLOT:$PYTHONPATH
    ```

[^1]: Necessário uma conta no GitHub e a instalação do utilitário de linha de comando `gh` (veja mais em [https://anaconda.org/conda-forge/gh](https://anaconda.org/conda-forge/gh))
[^2]: Desta forma, não será possível realizar entregas ao repositório.
