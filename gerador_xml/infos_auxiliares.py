# Arquivo com informações auxiiares para geração do XML.
# 
# O arquivo possui informações das operadoras, das versoes de tiss, e do de-para das colunas utilizadas nos Sheets de Saúde Suplementar para os campos do XML
#
# IMPORTANTE: Manter atualizado. Se essas informações não estiverem atualizadas, o código não irá gerar o XML correto


# Informações básicas de cada operadora
infos_operadoras = {
    
    "amil_one_rj": {
        "registroANS": "326305",
        "CNES": "988107",
        "CNPJ": "28286170000101",
        "tiss_version": "3.05.00",
        "codigoPrestadorNaOperadora": "68507771",
        "conselho_profissional": "06", 
        "identificacao_prestador" : "codigoPrestadorNaOperadora",
        "numero_caracteres_carteirinha": None
    },
    
    "amil_one_sp": {
        "registroANS": "326305",
        "CNES": "9884300",
        "CNPJ": "28286170000446",
        "tiss_version": "3.05.00",
        "codigoPrestadorNaOperadora": "68446772",
        "conselho_profissional": "06",
        "identificacao_prestador" : "codigoPrestadorNaOperadora",
        "numero_caracteres_carteirinha": None
    },
    
    "amil_rj": {
        "registroANS": "326305",
        "CNES": "988107",
        "CNPJ": "28286170000101",
        "tiss_version": "3.05.00",
        "codigoPrestadorNaOperadora": "68507771",
        "conselho_profissional": "06",
        "identificacao_prestador" : "codigoPrestadorNaOperadora",
        "numero_caracteres_carteirinha": 9
    },
    
    "amil_sp": {
        "registroANS": "326305",
        "CNES": "9884300",
        "CNPJ": "28286170000446",
        "tiss_version": "3.05.00",
        "codigoPrestadorNaOperadora": "68446772",
        "conselho_profissional": "06",
        "identificacao_prestador" : "codigoPrestadorNaOperadora",
        "numero_caracteres_carteirinha": 9
    },
    
    'bradesco': {
        "registroANS": "005711",
        "CNES": "9884300",
        "CNPJ": "28286170000101",
        "tiss_version": "3.05.00",
        "codigoPrestadorNaOperadora": "189303",
        "conselho_profissional": "06", ### pode mudar!
        "identificacao_prestador" : "codigoPrestadorNaOperadora",
        "numero_caracteres_carteirinha": None,
        "tipo_atendimento": "05"
    },
    
    "bradesco_operadora": {
        "registroANS": "421715",
        "CNES": "9884300",
        "CNPJ": "28286170000101",
        "tiss_version": "3.05.00",
        "codigoPrestadorNaOperadora": "189303",
        "conselho_profissional": "06", ### pode mudar!
        "identificacao_prestador" : "codigoPrestadorNaOperadora",
        "numero_caracteres_carteirinha": None,
        "tipo_atendimento": "05"
    },
    
    "bradesco_operadora_sp": {
        "registroANS": "421715",
        "CNES": "9884300",
        "CNPJ": "28286170000101",
        "tiss_version": "3.05.00",
        "codigoPrestadorNaOperadora": "202603",
        "conselho_profissional": "06", ### pode mudar!
        "identificacao_prestador" : "codigoPrestadorNaOperadora",
        "numero_caracteres_carteirinha": None,
        "tipo_atendimento": "05"
    },
    
    "bradesco_sp": {
        "registroANS": "005711",
        "CNES": "9884300",
        "CNPJ": "28286170000101",
        "tiss_version": "3.05.00",
        "codigoPrestadorNaOperadora": '202603',
        "conselho_profissional": "06", ### pode mudar!
        "identificacao_prestador" : "codigoPrestadorNaOperadora",
        "numero_caracteres_carteirinha": None,
        "tipo_atendimento": "05"
    },
    
    'caberj' : {
        "registroANS": "24361",
        "CNES": "32436",
        "CNPJ": None,
        "tiss_version": "3.05.00",
        "codigoPrestadorNaOperadora": "155822",
        "conselho_profissional": "06",
        "identificacao_prestador" : "codigoPrestadorNaOperadora",
        "numero_caracteres_carteirinha": None
    },

    'caberj_integral_saude' : {
        "registroANS": "415774",
        "CNES": "9881077",
        "CNPJ": None,
        "tiss_version": "3.05.00",
        "codigoPrestadorNaOperadora": "155822",
        "conselho_profissional": "06",
        "identificacao_prestador" : "codigoPrestadorNaOperadora",
        "numero_caracteres_carteirinha": None
    },

    'camarj' : {
        "registroANS": "418820",
        "CNES": "9881077",
        "CNPJ": "28286170000101",
        "tiss_version": "3.05.00",
        "codigoPrestadorNaOperadora": "000001198",
        "conselho_profissional": "06",
        "identificacao_prestador" : "cnpjContratado", ##??
        "numero_caracteres_carteirinha": None
    },
    
    'careplus' : {
        "registroANS": "379956",
        "CNES": "9884300",
        "CNPJ": "28286170000101",
        "tiss_version": "3.03.01",
        "codigoPrestadorNaOperadora": "",
        "conselho_profissional": "06",
        "identificacao_prestador" : "cnpjContratado",
        "numero_caracteres_carteirinha": None
    },
    
    'cassi' : {
        "registroANS": "346659",
        "CNES": "9045252",
        "CNPJ": "28286170001256",
        "tiss_version": "3.05.00",
        "codigoPrestadorNaOperadora": "94472473",
        "conselho_profissional": "06",
        "identificacao_prestador" : "cnpjContratado",
        "numero_caracteres_carteirinha": None
    },
    
    "fio_saude": {
        "registroANS": "417548",
        "CNES": "9881077",
        "CNPJ": "28286170000101",
        "tiss_version": "3.02.00",
        "codigoPrestadorNaOperadora": "",
        "conselho_profissional": "6",
        "identificacao_prestador" : "cnpjContratado",
        "numero_caracteres_carteirinha": None
    },
    
    "mediservice_rj": {
        "registroANS": "333689",
        "CNES": "9852883",
        "CNPJ": "28286170000101",
        "tiss_version": "3.05.00",
        "codigoPrestadorNaOperadora": "",
        "conselho_profissional": "06",
        "identificacao_prestador" : "cnpjContratado",
        "numero_caracteres_carteirinha": None
    },
    
      "mediservice_sp": {
        "registroANS": "333689",
        "CNES": "9852883",
        "CNPJ": "28286170000446",
        "tiss_version": "3.05.00",
        "codigoPrestadorNaOperadora": "",
        "conselho_profissional": "06",
        "identificacao_prestador" : "cnpjContratado",
          "numero_caracteres_carteirinha": None
    },
    
    "omint_df": {
        "registroANS": "359661",
        "CNES": "9852883",
        "CNPJ": "28286170000950",
        "tiss_version": "3.05.00",
        "codigoPrestadorNaOperadora": "",
        "conselho_profissional": "06",
        "identificacao_prestador" : "cnpjContratado",
        "numero_caracteres_carteirinha": None
    },
    
    "omint_pr": {
        "registroANS": "359661",
        "CNES": "9852883",
        "CNPJ": "28286170000870",
        "tiss_version": "3.05.00",
        "codigoPrestadorNaOperadora": "",
        "conselho_profissional": "06",
        "identificacao_prestador" : "cnpjContratado",
        "numero_caracteres_carteirinha": None
    },
    
      "omint_rj": {
        "registroANS": "359661",
        "CNES": "9852883",
        "CNPJ": "28286170000101",
        "tiss_version": "3.05.00",
        "codigoPrestadorNaOperadora": "",
        "conselho_profissional": "06",
        "identificacao_prestador" : "cnpjContratado",
        "numero_caracteres_carteirinha": None
    },
    
      "omint_sp": {
        "registroANS": "359661",
        "CNES": "9852883",
        "CNPJ": "28286170000446",
        "tiss_version": "3.05.00",
        "codigoPrestadorNaOperadora": "",
        "conselho_profissional": "06",
        "identificacao_prestador" : "cnpjContratado",
        "numero_caracteres_carteirinha": None
    },
    
      "vale": {
        "registroANS": "345695",
        "CNES": "9881077",
        "CNPJ": "28286170000101",
        "tiss_version": "3.05.00",
        "codigoPrestadorNaOperadora": "",
        "conselho_profissional": "06",
        "identificacao_prestador" : "cnpjContratado",
        "numero_caracteres_carteirinha": None
    }
}

# Informações sobre as versões do TISS
infos_versoes_tiss = {
    
   "3.05.00": {
        "tag_padrao_cabecalho": "Padrao",
        "possui_sequencial_item": True
    },
    
    "3.03.01": {
        "tag_padrao_cabecalho": "Padrao",
        "possui_sequencial_item": False
    },
    
    "3.02.00": {
        "tag_padrao_cabecalho": "versaoPadrao",
        "possui_sequencial_item": False
    }
}

# Nome da beep, como aparecerá no XML
infos_beep = {
    "beep_comany_name": "BEEP SERVICOS MEDICOS LTDA"
}

# De-para das colunas como estão no Sheets utilizado pela Saúde Suplementar (com letras minusculas), para o campo correspondente no XML
de_para_colunas_sheets_xml = {
    'nº guia operadora' : 'numeroGuiaOperadora',
    'data de solicitação' : 'dataSolicitacao',
    'código de autorização' : 'senha',
    'carteira' : 'numeroCarteira',
    'beneficiário nome': 'nomeBeneficiario',
    'conselho profissional (crm)' : 'conselhoProfissional',
    'crm': 'numeroConselhoProfissional',
    'código cbo/especialidade' : 'CBOS',
    'data de agendamento': 'dataExecucao',
    'código procedimento operadora': 'codigoProcedimento',
    'descrição do procedimento' : 'descricaoProcedimento',
    'vacina' : 'descricaoProcedimento',
    'qtd' : 'quantidadeExecutada',
    'uf' : 'UF',
    'valor' : 'valorUnitario',
    'voucher' : 'voucher',
    'atendimentorn' : 'atendimentoRN'
}

# Colunas que serão de fato utilizadas para gerar o XML (todas as outras são excluídas para otimizar o código)
colunas_utilizadas = [
     'numeroGuiaOperadora',
     'dataSolicitacao',
     'senha',
     'numeroCarteira',
     'nomeBeneficiario',
     'conselhoProfissional',
     'numeroConselhoProfissional',
     'CBOS',
     'dataExecucao',
     'codigoProcedimento',
     'descricaoProcedimento',
     'quantidadeExecutada',
     'UF',
     'valorUnitario',
     'voucher',
     'sequencialItem',
     'dataValidadeSenha',
     'atendimentoRN',
     'valorTotal'
]