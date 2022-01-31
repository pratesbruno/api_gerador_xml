# Imports
import pandas as pd
import xml.etree.ElementTree as ET
from datetime import datetime, date, timedelta
import hashlib
import io
import math
import time

# Imports das funcoes e infos auxiliares
from gerador_xml.funcoes_auxiliares import _pretty_print, converte_data_formato_correto, adiciona_30_dias, \
                               converte_valor_formato_correto, remover_acento, check_duplicadas_num_guia_prestador
from gerador_xml.registrar_na_gcp import registrar_na_gcp
from gerador_xml.infos_auxiliares import infos_operadoras, infos_versoes_tiss, infos_beep, de_para_colunas_sheets_xml, colunas_utilizadas


# Classe principal que é utilizada para gerar o XML
class GeradorXML():
    def __init__(self, base_input, operadora, tipo_produto, encoding="ISO-8859-1", usuario=None):
        self.base_input = base_input
        self.operadora = operadora
        self.tipo_produto = tipo_produto
        self.encoding = encoding
        self.usuario = usuario
        
        # Infos beep
        self.nome_beep = infos_beep['beep_comany_name']
        
        # Infos dependentes da operadora
        self.versao_tiss = infos_operadoras[self.operadora]['tiss_version']
        self.versao_tiss_formato_url = self.versao_tiss.replace('.','_')
        self.registro_ans = infos_operadoras[self.operadora]['registroANS']
        self.cnes = infos_operadoras[self.operadora]['CNES']
        self.conselhoProfissional = infos_operadoras[self.operadora]['conselho_profissional']
        self.tag_padrao_cabecalho = infos_versoes_tiss[infos_operadoras[self.operadora]['tiss_version']]['tag_padrao_cabecalho']
        self.possui_sequencial_item = infos_versoes_tiss[infos_operadoras[self.operadora]['tiss_version']]['possui_sequencial_item']
        self.numero_caracteres_carteirinha = infos_operadoras[self.operadora]['numero_caracteres_carteirinha']
        self.tipo_atendimento = infos_operadoras[self.operadora].get('tipo_atendimento','06')
        self.identificacao_prestador = infos_operadoras[self.operadora]['identificacao_prestador']
        if self.identificacao_prestador == 'codigoPrestadorNaOperadora':
            self.valor_identificacao_prestador = infos_operadoras[operadora]['codigoPrestadorNaOperadora']
        elif self.identificacao_prestador == 'cnpjContratado':
            self.valor_identificacao_prestador = infos_operadoras[self.operadora]['CNPJ']
            
        # Infos "fixas" para todas as operadoras (pode mudar algum dia?)
        self.carater_atendimento = "1"
        self.codigo_tabela = "22"
        self.indicacao_acidente = "9"
        self.tipo_consulta = "1"
        self.reducao_acrescimo = "1"
        
        # Data e hora atual
        self.data_registro_transacao = datetime.now().strftime("%Y-%m-%d")
        self.hora_registro_transacao = datetime.now().strftime("%H:%M:%S")
        
        # Inicializando variaveis
        self.df_base = None
        self.df_totais = None
        self.sequencial_transacao = None
        self.num_lote = None
        self.lista_sequencial_transacao = []
        self.valor_total_arquivos = None
        self.lista_guias_distintas = None
        self.numero_arquivos_xml = None
        self.lista_valor_total_de_cada_arquivo = []
        self.arquivo_xml_atual = None
        self.cabecalho = None
        self.prestador_para_operadora = None
        self.string_para_hash = None
        self.hash = None
        self.epilogo = None
        self.arquivo_output = None
        self.mes = None
        self.diretorio = None
        self.filename = None
        self.xml_com_namespaces = None
        self.arquivos_xml = []
        self.avisos = []
        
    # Função princial. É preciso indicar o tipo_produto ('lab' ou 'vac') e o xml é gerado
    def gera_xml(self):
        
        # Gera dataframe a partir do arquivo csv
        self.gera_dataframe_base()

        # Gera dataframe com os valores totais por guia
        self.df_totais = self.df_base.astype({'valorTotal': 'float'}).groupby('numeroGuiaOperadora').sum()
        self.valor_total_arquivos = float(self.df_totais.sum()[1])

        # Gera sequencialTransacao e numLote a partir do primeiro voucher e o minuto e segundo atual
        self.sequencial_transacao = int(self.df_base['voucher'][0] + datetime.now().strftime("%M%S") + '01')
        self.num_lote = self.sequencial_transacao
        
        # Gera lista com as guias distintas
        self.lista_guias_distintas = list(self.df_base.numeroGuiaOperadora.unique())
        
        # Define o número de arquivos xmls que serão gerados (max 99 guias por arquivo)
        self.numero_arquivos_xml = math.ceil(len(self.lista_guias_distintas) / 99)
        print(f'Serão gerados {self.numero_arquivos_xml} arquivo(s).\n')
        
        # Gera os arquivos xml
        for i in range(self.numero_arquivos_xml):
            start_time = time.time()
            
            self.arquivo_xml_atual = i
            # Gera o elemento raiz do XML, e as tags de cabeçalho e prestadorParaOperadora
            root = ET.Element('mensagemTISS')
            self.gera_cabecalho()
            try:
                self.gera_prestador_para_operadora()
            except Exception as e:
                print('Erro na função "gera_prestador_para_operadora"')
                print(e)
                self.gera_prestador_para_operadora()

            # Insere cabecalho e prestadorParaOperadora na raiz (mensagemTISS)
            root.insert(1, self.cabecalho)
            root.insert(1, self.prestador_para_operadora)

            # Gera hash
            tree = ET.ElementTree(root)
            self.string_para_hash = ET.tostring(tree.getroot(), encoding=self.encoding, method='text')
            self.gera_hash()
            
            # Gera epilogo com a hash e inclui na raiz
            self.gera_epilogo()
            root.insert(2, self.epilogo)
            tree = ET.ElementTree(root)

            # Cria arquivo xml
            caminho = f'{self.operadora}_{self.data_registro_transacao.replace("-","")}_{self.tipo_produto}_{self.arquivo_xml_atual+1}'
            
            self.arquivo_output = caminho
            self.write_xml(tree)

            print(f'Arquivo XML salvo como xml_gerados/{self.operadora}/{self.data_registro_transacao}/{self.arquivo_output}.xml')
            print(f"Tempo para gerar o último arquivo: --- {round((time.time() - start_time),2)} segundos.\n")
            
            self.arquivos_xml.append(self.xml_com_namespaces)

        self.registra_infos_gcp() 
        return self.arquivos_xml, len(self.lista_guias_distintas), self.numero_arquivos_xml, self.valor_total_arquivos, self.avisos, self.lista_sequencial_transacao
            
    def gera_dataframe_base(self):

        # Gera dataframe a partir do excel, csv ou sql, e remove os acentos
        if True:
            sheet_name = f'{self.operadora}_{self.tipo_produto}_{self.mes}'
        else:
            sheet_name = f'{self.operadora}_{self.tipo_produto}'

        # Gera a base a partir do tipo de input (excel, csv ou sql)
        try:
            self.df_base = pd.read_csv(self.base_input, dtype=str)
        except Exception as e:
            print(str(e))

        # Remove acentos
        self.df_base = self.df_base.applymap(remover_acento)

        # Altera nome das colunas e remove as que não serão usadas
        self.df_base.columns = [de_para_colunas_sheets_xml.get(col.lower().strip(),"Remover") for col in self.df_base.columns]
        self.df_base.drop('Remover',axis=1, inplace=True)
        
        # Gera um número único para o numeroGuiaPrestador a partir do voucher e o index
        # (pode existir números repetidos em arquivos diferentes - isso pode ser um problema?)
        self.df_base['index'] = self.df_base.index
        self.df_base['index'] = self.df_base['index'].apply(lambda x: str(x))
        self.df_base['numeroGuiaPrestador'] = self.df_base['voucher'] + self.df_base['index']

        # Se não houver coluna de senha no csv, assume que nenhum procedimento possui senha
        if 'senha' not in self.df_base.columns:
            self.df_base['senha'] = 'nan'
            msg = 'ATENÇÃO: Coluna de senhas de autorização não encontrada. Será assumido que nenhum procedimento precisa de senha.\n'
            print(msg)
            self.avisos.append(msg)

        # Se não houver coluna de atendimentoRN no csv, assume que nenhum atendimento é de RN
        if 'atendimentoRN' not in self.df_base.columns:
            self.df_base['atendimentoRN'] = 'N'
            msg = 'ATENÇÃO: Coluna de atendimentoRN não encontrada. Será assumido que nenhum atendimento foi de recém-nato.\n'
            print(msg)
            self.avisos.append(msg)
        
        # Caso a operadora seja Omint, usa o numero de carteirinha como NumGuiaOperadora
        if self.operadora[:5] == 'omint':
            self.df_base['numeroGuiaOperadora'] = self.df_base['numeroCarteira']

        # Se algum procedimento tem senha, repete a senha para todos os procedimentos da guia
        df_guias_senhas = self.df_base[['numeroGuiaOperadora','senha']].copy()
        df_guias_senhas = df_guias_senhas[df_guias_senhas['senha']!='nan']
        dict_senhas = pd.Series(df_guias_senhas.senha.values, index=df_guias_senhas.numeroGuiaOperadora).to_dict()
        self.df_base['senha'] = self.df_base['numeroGuiaOperadora'].apply(lambda x: dict_senhas[x] if x in dict_senhas.keys() else 'nan')
        
        #Gera data validade da senha (30 dias depois da dataSolicitacao)
        self.df_base['dataValidadeSenha'] = self.df_base['dataSolicitacao'].apply(lambda x: adiciona_30_dias(x))
        
        # Gera sequencial dos procedimentos dentro da guia
        self.df_base['sequencialItem'] = self.df_base.groupby(['numeroGuiaOperadora']).cumcount() + 1
        
        # Converte a coluna de valor para o formato correto
        self.df_base['valorUnitario'] = self.df_base['valorUnitario'].apply(lambda x: converte_valor_formato_correto(x))
        
        # Gera coluna de valorTotal do procedimento (valor unitario * quantidade)
        self.df_base['valorTotal'] = self.df_base['valorUnitario'].astype(float) * self.df_base['quantidadeExecutada'].astype(int)
        
        # Remove duplicadas
        print(f'Existem {len(self.df_base) - len(self.df_base.drop_duplicates())} linhas duplicadas.')
        self.df_base = self.df_base.drop_duplicates()
          
    def gera_cabecalho(self):
        try:
            self.cabecalho = ET.Element('cabecalho')
            self.gera_identificacao_transacao()
            self.gera_origem()
            self.gera_destino()
            padrao = ET.SubElement(self.cabecalho, self.tag_padrao_cabecalho)
            padrao.text = self.versao_tiss
        except BaseException as e:
            print('Erro ao gerar cabecalho')
            print(f'Erro: {e}')
            
    def gera_identificacao_transacao(self):
        identificacaoTransacao = ET.SubElement(self.cabecalho, 'identificacaoTransacao')
        tipoTransacao = ET.SubElement(identificacaoTransacao, 'tipoTransacao')
        tipoTransacao.text = 'ENVIO_LOTE_GUIAS'
        sequencialTransacao = ET.SubElement(identificacaoTransacao, 'sequencialTransacao')
        sequencialTransacao.text = str(self.sequencial_transacao + self.arquivo_xml_atual)
        self.lista_sequencial_transacao.append(sequencialTransacao.text)
        dataRegistroTransacao = ET.SubElement(identificacaoTransacao, 'dataRegistroTransacao')
        dataRegistroTransacao.text = self.data_registro_transacao
        horaRegistroTransacao = ET.SubElement(identificacaoTransacao, 'horaRegistroTransacao')
        horaRegistroTransacao.text = self.hora_registro_transacao
        
    def gera_origem(self):
        origem = ET.SubElement(self.cabecalho, 'origem')
        self.gera_identificacao_prestador(origem)
    
    def gera_identificacao_prestador(self, origem):
        identificacaoPrestador = ET.SubElement(origem, 'identificacaoPrestador')
        if self.identificacao_prestador == 'cnpjContratado':
            codPrestadorOperadoraOuCNPJ = ET.SubElement(identificacaoPrestador, 'CNPJ')
        elif self.identificacao_prestador == 'codigoPrestadorNaOperadora':
            codPrestadorOperadoraOuCNPJ = ET.SubElement(identificacaoPrestador, 'codigoPrestadorNaOperadora')
        codPrestadorOperadoraOuCNPJ.text = self.valor_identificacao_prestador
        
    def gera_destino(self):
        destino = ET.SubElement(self.cabecalho, 'destino')
        registroANS = ET.SubElement(destino, 'registroANS')
        registroANS.text = self.registro_ans
        
    def gera_prestador_para_operadora(self):
        self.prestador_para_operadora = ET.Element('prestadorParaOperadora')
        loteGuias = ET.SubElement(self.prestador_para_operadora, 'loteGuias')
        numeroLote = ET.SubElement(loteGuias, 'numeroLote')
        numeroLote.text = str(self.num_lote + self.arquivo_xml_atual)
        guiasTiss = self.gera_guias_tiss(self.df_base)
        loteGuias.insert(1,guiasTiss)
    
    def gera_guias_tiss(self, df_base):
        guias = ET.Element('guiasTISS')
        # Zera a variavel que contabiliza o valor total do arquivo xml corrente
        self.valor_total_arquivo_corrente = 0

        # Gera as guias de acordo com o número do arquivo xml que está sendo gerado (max 99 guias por arquivo)
        for guia_atual in self.lista_guias_distintas[(self.arquivo_xml_atual*99):(self.arquivo_xml_atual+1)*99]:
            
            # Pega a linha referente ao primeiro procedimento da guia_atual
            row = self.df_base[self.df_base['numeroGuiaOperadora']==guia_atual].iloc[0]

            # Gera os elementos XML
            guia = ET.SubElement(guias, 'guiaSP-SADT')
            self.gera_cabecalho_guia(guia,row)
            self.gera_dados_autorizacao(guia,row)            
            self.gera_dados_beneficiario(guia, row)
            self.gera_dados_solicitante(guia, row)            
            self.gera_dados_solicitacao(guia, row)            
            self.gera_dados_executante(guia, row)            
            self.gera_dados_atendimento(guia, row)            
            self.gera_procedimentos_executados(guia, row, guia_atual)
            self.gera_valor_total(guia, row, guia_atual) 

        # Registra o valor total do arquivo corrente
        self.lista_valor_total_de_cada_arquivo.append(self.valor_total_arquivo_corrente)
        return guias

    def gera_cabecalho_guia(self, guia, row):
        cabecalhoGuia = ET.SubElement(guia, 'cabecalhoGuia')
        registroANS = ET.SubElement(cabecalhoGuia, 'registroANS')
        registroANS.text = self.registro_ans
        numeroGuiaPrestador = ET.SubElement(cabecalhoGuia, 'numeroGuiaPrestador')
        numeroGuiaPrestador.text = str(row['numeroGuiaPrestador'])

    def gera_dados_autorizacao(self, guia, row):
        dadosAutorizacao = ET.SubElement(guia, 'dadosAutorizacao')
        numeroGuiaOperadora = ET.SubElement(dadosAutorizacao, 'numeroGuiaOperadora')
        # Se a operadora for omint, o código da operadora é sempre '11111111'
        numeroGuiaOperadora.text = str(row['numeroGuiaOperadora']) if self.operadora[:5] != 'omint' else '11111111'
        dataAutorizacao = ET.SubElement(dadosAutorizacao, 'dataAutorizacao')
        dataAutorizacao.text = converte_data_formato_correto(str(row['dataSolicitacao'])) # usa o valor da dataSolicitacao
        
        # Entender melhor quais casos que exigem senha        
        # Gera tag de senha e dataValidadeSenha, caso os valores nao estejam vazios na base
        if str(row['senha']) != 'nan' and str(row['dataValidadeSenha']) != 'nan':
            senha = ET.SubElement(dadosAutorizacao, 'senha')
            senha.text = str(row['senha'])
            dataValidadeSenha = ET.SubElement(dadosAutorizacao, 'dataValidadeSenha')
            dataValidadeSenha.text = converte_data_formato_correto(str(row['dataValidadeSenha']))


    def gera_dados_beneficiario(self, guia, row):
        dadosBeneficiario = ET.SubElement(guia, 'dadosBeneficiario')
        numeroCarteira = ET.SubElement(dadosBeneficiario, 'numeroCarteira')
        
        # Checa se a operadora requer um número específico de caracteres. Se tiver, completa com "0" na frente até formar o número
        if self.numero_caracteres_carteirinha:
            num_carteira = str(row['numeroCarteira']).rjust(self.numero_caracteres_carteirinha, '0')
        else:
            num_carteira = str(row['numeroCarteira'])
        numeroCarteira.text = num_carteira
            
        atendimentoRN = ET.SubElement(dadosBeneficiario, 'atendimentoRN')
        atendimentoRN.text = str(row['atendimentoRN'])
        nomeBeneficiario = ET.SubElement(dadosBeneficiario, 'nomeBeneficiario')
        nomeBeneficiario.text = str(row['nomeBeneficiario'])

    def gera_dados_solicitante(self, guia, row):
        dadosSolicitante = ET.SubElement(guia, 'dadosSolicitante')
        self.gera_contratado_solicitante(dadosSolicitante, row)
        self.gera_profissional_solicitante(dadosSolicitante, row)
        
    def gera_contratado_solicitante(self, dadosSolicitante, row):
        contratadoSolicitante = ET.SubElement(dadosSolicitante, 'contratadoSolicitante')
        codPrestadorOperadoraOuCNPJ = ET.SubElement(contratadoSolicitante, self.identificacao_prestador)
        codPrestadorOperadoraOuCNPJ.text = self.valor_identificacao_prestador
        nomeContratado = ET.SubElement(contratadoSolicitante, 'nomeContratado')
        nomeContratado.text = self.nome_beep

    def gera_profissional_solicitante(self, dadosSolicitante, row):
        profissionalSolicitante = ET.SubElement(dadosSolicitante, 'profissionalSolicitante')
        conselhoProfissional = ET.SubElement(profissionalSolicitante, 'conselhoProfissional')
        conselhoProfissional.text = self.conselhoProfissional ## ->> pegar da coluna? (transformar 6 em 06)
        numeroConselhoProfissional = ET.SubElement(profissionalSolicitante, 'numeroConselhoProfissional')
        numeroConselhoProfissional.text = str(row['numeroConselhoProfissional'])
        UF = ET.SubElement(profissionalSolicitante, 'UF')
        UF.text = str(row['UF'])
        CBOS = ET.SubElement(profissionalSolicitante, 'CBOS')
        CBOS.text = str(row['CBOS'])

    def gera_dados_solicitacao(self, guia, row):
        dadosSolicitacao = ET.SubElement(guia, 'dadosSolicitacao')
        dataSolicitacao = ET.SubElement(dadosSolicitacao, 'dataSolicitacao')
        dataSolicitacao.text = converte_data_formato_correto(str(row['dataSolicitacao']))
        caraterAtendimento = ET.SubElement(dadosSolicitacao, 'caraterAtendimento')
        caraterAtendimento.text = self.carater_atendimento

    def gera_dados_executante(self, guia, row):
        dadosExecutante = ET.SubElement(guia, 'dadosExecutante')
        self.gera_contratado_executante(dadosExecutante, row)
        CNES = ET.SubElement(dadosExecutante, 'CNES')
        CNES.text = self.cnes

    def gera_contratado_executante(self, dadosExecutante, row):
        contratadoExecutante = ET.SubElement(dadosExecutante, 'contratadoExecutante')
        codPrestadorOperadoraOuCNPJ = ET.SubElement(contratadoExecutante, self.identificacao_prestador)
        codPrestadorOperadoraOuCNPJ.text = self.valor_identificacao_prestador
        nomeContratado = ET.SubElement(contratadoExecutante, 'nomeContratado')
        nomeContratado.text = self.nome_beep

    def gera_dados_atendimento(self, guia, row):
        dadosAtendimento = ET.SubElement(guia, 'dadosAtendimento')
        tipoAtendimento = ET.SubElement(dadosAtendimento, 'tipoAtendimento')
        tipoAtendimento.text = self.tipo_atendimento
        indicacaoAcidente = ET.SubElement(dadosAtendimento, 'indicacaoAcidente')
        indicacaoAcidente.text = self.indicacao_acidente
        tipoConsulta = ET.SubElement(dadosAtendimento, 'tipoConsulta')
        tipoConsulta.text = self.tipo_consulta

    def gera_procedimentos_executados(self, guia, row, guia_atual):
        procedimentosExecutados = ET.SubElement(guia, 'procedimentosExecutados')
        # Gera procedimentos (um para cada linha da base correspondente a guia atual)
        df_atual = self.df_base[self.df_base['numeroGuiaOperadora']==guia_atual]
        for index, row in df_atual.iterrows():
            self.gera_procedimento_executado(procedimentosExecutados, row)                

    def gera_procedimento_executado(self, procedimentosExecutados, row):
        procedimentoExecutado = ET.SubElement(procedimentosExecutados, 'procedimentoExecutado')
        if self.possui_sequencial_item:
            sequencialItem = ET.SubElement(procedimentoExecutado, 'sequencialItem')
            sequencialItem.text = str(row['sequencialItem'])
        dataExecucao = ET.SubElement(procedimentoExecutado, 'dataExecucao')
        dataExecucao.text = converte_data_formato_correto(str(row['dataExecucao']))
        self.gera_procedimento(procedimentoExecutado, row)
        quantidadeExecutada = ET.SubElement(procedimentoExecutado, 'quantidadeExecutada')
        quantidadeExecutada.text = str(row['quantidadeExecutada'])
        reducaoAcrescimo = ET.SubElement(procedimentoExecutado, 'reducaoAcrescimo')
        reducaoAcrescimo.text = self.reducao_acrescimo
        valorUnitario = ET.SubElement(procedimentoExecutado, 'valorUnitario')
        valorUnitario.text = '{0:.2f}'.format(float(row['valorUnitario']))
        valorTotal = ET.SubElement(procedimentoExecutado, 'valorTotal')
        valor_total_procedimento = float(row['valorUnitario']) * float(row['quantidadeExecutada'])
        valorTotal.text = '{0:.2f}'.format(valor_total_procedimento)

    def gera_procedimento(self, procedimentoExecutado, row):
        procedimento = ET.SubElement(procedimentoExecutado, 'procedimento')
        codigoTabela = ET.SubElement(procedimento, 'codigoTabela')
        codigoTabela.text = self.codigo_tabela
        codigoProcedimento = ET.SubElement(procedimento, 'codigoProcedimento')
        codigoProcedimento.text = str(row['codigoProcedimento'])
        descricaoProcedimento = ET.SubElement(procedimento, 'descricaoProcedimento')
        descricaoProcedimento.text = str(row['descricaoProcedimento'])

    def gera_valor_total(self, guia, row, guia_atual):
        valorTotal = ET.SubElement(guia, 'valorTotal')
        valorProcedimentos = ET.SubElement(valorTotal, 'valorProcedimentos')
        valorProcedimentos.text = str(self.df_totais.loc[guia_atual,'valorTotal'].round(2))
        valorDiarias = ET.SubElement(valorTotal, 'valorDiarias')
        valorDiarias.text = '0'
        valorTaxasAlugueis = ET.SubElement(valorTotal, 'valorTaxasAlugueis')
        valorTaxasAlugueis.text = '0'
        valorMateriais = ET.SubElement(valorTotal, 'valorMateriais')
        valorMateriais.text = '0'
        valorMedicamentos = ET.SubElement(valorTotal, 'valorMedicamentos')
        valorMedicamentos.text = '0'
        valorOPME = ET.SubElement(valorTotal, 'valorOPME')
        valorOPME.text = '0'
        valorGasesMedicinais = ET.SubElement(valorTotal, 'valorGasesMedicinais')
        valorGasesMedicinais.text = '0'
        valorTotalGeral = ET.SubElement(valorTotal, 'valorTotalGeral')
        valor_guia_corrente = self.df_totais.loc[guia_atual,'valorTotal'].round(2)
        valorTotalGeral.text = str(valor_guia_corrente)
        self.valor_total_arquivo_corrente += valor_guia_corrente

    def gera_epilogo(self):
        self.epilogo = ET.Element('epilogo')
        self.gera_hash()
        _hash = ET.SubElement(self.epilogo, 'hash')
        _hash.text = self.hash
        
    def gera_hash(self):
        md5_hash = hashlib.md5()
        md5_hash.update(self.string_para_hash)
        self.hash = md5_hash.hexdigest()
        
    def write_xml(self, tree):
        # Gera a raiz do XML
        root = tree.getroot()
        # Formata a raiz no formato correto (esse passo é realmente necessário?)
        _pretty_print(root)
        # Gera o ElementTree novamente, no formato correto
        tree = ET.ElementTree(root)

        # Inclui manualmente os namespaces ('<ans:') e o xml declaration
        xml_sem_namespaces = ET.tostring(tree.getroot(),encoding='unicode',method='xml')
        root_string = f"<ans:mensagemTISS xmlns:ans='http://www.ans.gov.br/padroes/tiss/schemas' xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance' xsi:schemaLocation='http://www.ans.gov.br/padroes/tiss/schemas/tissV{self.versao_tiss_formato_url}.xsd'>"
        self.xml_com_namespaces = str(xml_sem_namespaces).replace('</','#$%@').replace('<','<ans:').replace('#$%@','</ans:').replace('<ans:?','<?')
        self.xml_com_namespaces = self.xml_com_namespaces.replace('<ans:mensagemTISS>', root_string)
        self.xml_com_namespaces = f"<?xml version='1.0' encoding='{self.encoding}'?>\n" + self.xml_com_namespaces

    def registra_infos_gcp(self):
        '''Salva infos no bucket da GCP'''

        bucket = 'log-portal-ss'
        
        for i in range(len(self.arquivos_xml)):
            arquivo_na_memoria = io.StringIO(self.arquivos_xml[i])
            data_geracao_xml = datetime.now().strftime("%Y%m%d")
            nome_arquivo = f'{self.operadora}_{data_geracao_xml}_{self.tipo_produto}_{self.lista_sequencial_transacao[i]}_{i+1}.xml'

            # Registra arquivo XML na GCP
            subpasta_xml = f'arquivos-xml/{self.operadora}/{self.data_registro_transacao}/{self.tipo_produto}/'
            url_gcp = registrar_na_gcp(content=arquivo_na_memoria, bucket=bucket, filename=f'{subpasta_xml}{nome_arquivo}', type='xml')

            # Registra json com infos do usuário que gerou o arquivo, o nome do arquivo, o link na gcp, a data, o valor total do arquivo,
            # e o valor total da geração (somando os valores dos arquivos que foram subdivididos para atender o limite de 99 guias)
            json_object = {
                'tipo_evento' : 'gerar_xml',
                'resultado_evento' : 'sucesso',
                'mensagem_erro' : None,
                'usuario' : self.usuario,
                'data' : datetime.now(),
                'operadora' : self.operadora,
                'tipo_produto' : self.tipo_produto,
                'valor_arquivo' : self.lista_valor_total_de_cada_arquivo[i],
                'nome_arquivo' : nome_arquivo,
                'url_gcp': url_gcp,
                'valor_total_gerado' : '{0:,.2f}'.format(self.valor_total_arquivos)
            }
             # Registra arquivo json na GCP
            subpasta_json = f'eventos/{self.operadora}/{self.data_registro_transacao}/{self.tipo_produto}/'
            registrar_na_gcp(content=json_object, bucket=bucket, filename=f'{subpasta_json}{nome_arquivo}', type='json')

        # Printa infos do número de arquivos gerados e do numero de guias distintas nos arquivos
        if self.numero_arquivos_xml == 1:
            msg_inicial = "Foi gerado 1 arquivo xml, referente a "
        else:
            msg_inicial = f"Foram gerados {self.numero_arquivos_xml} arquivos xml, referentes a "
        msg_arquivos_gerados = f"{msg_inicial}{len(self.lista_guias_distintas)} guias distintas."
        print(msg_arquivos_gerados)
        msg_valor_total = f"Valor total dos xml gerados: R$ {'{0:,.2f}'.format(self.valor_total_arquivos)}\n"
        print(msg_valor_total)