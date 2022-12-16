#! /usr/bin/env python3

# SCANPLOT - Um sistema de plotagem simples para o SCANTEC
# CC-BY-NC-SA-4.0 2022 INPE

import global_variables as gvars

import re
import os
import ntpath

import numpy as np
import pandas as pd

from datetime import date, datetime, timedelta

def read_namelists(basepath,**kwargs):

    """
    read_namelists
    ==============
    
    Esta função lê os namelists e arquivos de definições dos modelos do SCANTEC e
    retorna para o usuário dois dicionários, VarsLevs e Confs, com as informações lidas.
    
    Parâmetros de entrada
    ---------------------
        basepath : diretório raiz da instalação do SCANTEC.
        
    Parâmetros de entrada opcionais
    -------------------------------
        basecomp : string com o complemento do diretório raiz da instalação do SCANTEC (específico
                   para múltiplos experimentos).
        scanconf : valor Booleano para indicar apenas o diretório de instalação do SCANTEC ou o caminho 
                   para o arquivo de configurações (considera o caminho para o diretório tables como relativo):
                   * scanconf=False (valor padrão), considera como argumento apenas o diretório de instalação 
                                    do SCANTEC;
                   * scantec=True, considera o caminho absoluto para o nome do arquivo de instalação 'scantec.conf' 
        returnpath : valor Booleano para retornar o caminho absoluto da instalação do SCANTEC.
                     * returnpath=False (valor padrão), não retorna o valor da variável 'basepath';
                     * returnpath=True, retorna o valor da variável 'basepath'

    Resultados
    ----------
        VarsLevs : dicionário com as variáveis, níveis e nomes definidos no arquivo scantec.vars;
        Confs    : dicionário com as definições contidas no arquivo scantec.conf.
    
    Uso
    ---
        import scanplot
        
        data_vars, data_conf = scanplot.read_namelists("~/SCANTEC")
    """
    
    # Verifica se foram passados os argumentos opcionais e atribui os valores
    if 'returnpath' in kwargs:
        returnpath = kwargs['returnpath']
    else:
        returnpath = gvars.returnpath

    if 'scanconf' in kwargs:
        scanconf = kwargs['scanconf']
    else:
        scanconf = gvars.scanconf

    if 'basecomp' in kwargs:
        basecomp = kwargs['basecomp']
        if scanconf:
            filename_conf = os.path.join(basepath)
        else:
            filename_conf = os.path.join(basepath, 'bin', basecomp, 'scantec.conf') 
    else:
        if scanconf:
            filename_conf = os.path.join(basepath)
        else:
            filename_conf = os.path.join(basepath, 'bin/scantec.conf') 

    # Lê o arquivo scantec.vars e transforma a lista de variáveis e níveis e um dicionário
    if scanconf:
        filename_vars = os.path.join(os.path.dirname(basepath), '..', 'tables/scantec.vars')
    else:
        filename_vars = os.path.join(basepath, 'tables/scantec.vars') 
   
    VarsLevs = {}
    
    # Com o método "with open", o arquivo é fechado automaticamente ao final
    with open(filename_vars,'r') as scantec_vars:
      for idx, line in enumerate(scantec_vars.readlines(), start=-4):
        rline = line.lstrip()
        if not (rline.startswith('#') or rline.startswith('::') or rline.startswith('variables:')):
          varlevdesc = rline.strip().split(' ', 1)
          VarsLevs[idx] = (varlevdesc[0], varlevdesc[1].strip('\"'))
        
#    # Lê do arquivo scantec.conf e transforma as informações principais em um dicionário
#    filename = os.path.join(basepath, 'bin/scantec.conf') 
    
    # A função a seguir lê a linha com a informação requerida e cria uma lista com os elementos separados 
    # de acordo com o separador ':'
    Confs = {}
    
    def key_value(linew):
      nlist = re.split(': ',linew)
      key = nlist[0]
      value = nlist[1].split()[0]
      if key == 'Starting Time' or key == 'Ending Time':
          value = datetime.strptime(value, "%Y%m%d%H")
      Confs[key] = value
      return Confs 
    
    # A função a seguir lê a lista de experimentos e cria um dicionário
    Exps = {}
    
    def key_value_exps(lexps):
      for i in range(2, len(lexps)): # 2: desconsidera as linhas "Experiments:" e "#ModelId Name Diretory File_Name_with_mask"
        slexps = lexps[i].split()
        Exps[slexps[1]] = [slexps[0], slexps[2]]
        Confs['Experiments'] = Exps
      return Confs
    
    # Com o método "with open", o arquivo é fechado automaticamente ao final
    with open(filename_conf,'r') as scantec_conf:
      for line in scantec_conf:
        if line.startswith('Starting Time'):
          key_value(line)
        elif line.startswith('Ending Time'):
          key_value(line)
        elif line.startswith('Analisys Time Step'):
          key_value(line)
        elif line.startswith('Forecast Time Step'):
          key_value(line)
        elif line.startswith('Forecast Total Time'):
          key_value(line)
        elif line.startswith('Time Step Type'):
          key_value(line)
        elif line.startswith('History Time'):
          key_value(line)
        elif line.startswith('scantec tables'):
          key_value(line)
        elif line.startswith('run domain number'):
          key_value(line)
        elif line.startswith('run domain lower left lat'):
          key_value(line)
        elif line.startswith('run domain lower left lon'):
          key_value(line)
        elif line.startswith('run domain upper right lat'):
          key_value(line)
        elif line.startswith('run domain upper right lon'):
          key_value(line)
        elif line.startswith('run domain resolution dx'):
          key_value(line)
        elif line.startswith('run domain resolution dy'):
          key_value(line)
        elif line.startswith('Reference Model Name'):
          key_value(line)
        elif line.startswith('Experiments'):
          exps = []
          while not(line.startswith('::')):
            exps.append(line)
            line = next(scantec_conf)
          key_value_exps(exps)
        elif line.startswith('Reference file'):
          key_value(line)
        elif line.startswith('Climatology Model Name'):
          key_value(line)
        elif line.startswith('Climatology file'):
          key_value(line)
        elif line.startswith('Output directory'):
          key_value(line)

    if returnpath:
        if scanconf:
            basepath = os.path.join(os.path.dirname(basepath), '..')
        return VarsLevs, Confs, basepath
    else:
        return VarsLevs, Confs

def dummy(**kwargs): 

    """
    dummy
    ==============
    
    Esta função simplesmente recebe e devolve um ou mais argumentos e é utilizada apenas para testes genéricos
    de chamada de funções a partir do SCANPLOT.
    
    Parâmetros de entrada
    ---------------------
        variavel : variável dos tipos string, Booleana, inteira, real etc.

    Resultados
    ----------
        variavel : dicionário com a(s) variável(is) passada(s) para a função.

    Uso
    ---
        import scanplot
        
        data_vars, data_conf = scanplot.read_namelists("~/SCANTEC")

        tmp = scanplot.dummy(teste=teste)
    """

    return kwargs    
