from datetime import datetime, date, timedelta
from unidecode import unidecode
import re
import pandas as pd
import xml.etree.ElementTree as ET

# Arquivo com funções auxiiares para geração do XML.
#

# Função para converter diferentes possíveis formatos de data para o formato utilizado no XML
def converte_data_formato_correto(data):
    try:
        return datetime.strptime(data, '%Y-%m-%d %H:%M:%S').strftime("%Y-%m-%d")
    except:
        try:
            return datetime.strptime(data, '%Y-%m-%d').strftime("%Y-%m-%d")
        except:
            try:
                return datetime.strptime(data, '%y/%m/%d %H:%M').strftime("%Y-%m-%d")
            except:
                try:
                    return datetime.strptime(data, '%d/%m/%Y %H:%M:%S').strftime("%Y-%m-%d")
                except:
                    try:
                        return datetime.strptime(data, '%d/%m/%y %H:%M').strftime("%Y-%m-%d")
                    except:
                        try:
                            return datetime.strptime(data, '%d/%m/%Y').strftime("%Y-%m-%d")
                        except:
                            return datetime.strptime(data, '%d/%m/%Y %H:%M').strftime("%Y-%m-%d")
                            

# Função para somar 30 dias a um data (utilizada para criar a dataValidadeSenha a partir da dataAutorizacao)
def adiciona_30_dias(data):
    data = converte_data_formato_correto(data)
    return (datetime.strptime(data, '%Y-%m-%d') + timedelta(days=30)).strftime('%Y-%m-%d')

# Função para ler diferentes formatos de valor monetário e converter para o formato utilizado no XML
def converte_valor_formato_correto(valor):
    valor = valor.replace('.','').replace(',','.').replace('R$','')
    return '{0:.2f}'.format(float(valor))

# Remove todos os acentos de um texto
def remover_acento(x):
    return unidecode(str(x))

# Função para checar se existe numeros de guia do prestador duplicadas
# NÃO ESTÁ SENDO UTILIZADA
def check_duplicadas_num_guia_prestador(tree):
    
    #Gera string com o XML
    tree = tree.getroot()
    xml_str = ET.tostring(tree).decode("ISO-8859-1")
    
    #Procura todos os numeroGuiaPrestador no XML
    string = r'<numeroGuiaPrestador>(\d*)</numeroGuiaPrestador>'
    pattern = re.compile(string)
    resultados = []
    matches = re.findall(pattern, xml_str)
    if len(matches)>0:
        for match in matches:
            resultados.append(match)
    
    # Checa se algum numero está repetido
    df_aux = pd.DataFrame(resultados)
    repetidos = list(df_aux[df_aux.duplicated(keep='first')][0])
    if len(repetidos) > 0:
        print(f'ATENÇÃO! Os numeroGuiaPrestador {repetidos} estão repetidos.')
        return False
    return True


# Função para deixar o XML no formato correto
# Adaptado de: https://stackoverflow.com/questions/28813876/how-do-i-get-pythons-elementtree-to-pretty-print-to-an-xml-file
def _pretty_print(current, parent=None, index=-1, depth=0):
    for i, node in enumerate(current):
        _pretty_print(node, current, i, depth + 1)
    if parent is not None:
        if index == 0:
            parent.text = '\n' + ('\t' * depth)
        else:
            parent[index - 1].tail = '\n' + ('\t' * depth)
        if index == len(parent) - 1:
            current.tail = '\n' + ('\t' * (depth - 1))