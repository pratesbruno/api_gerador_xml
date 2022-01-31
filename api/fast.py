from fastapi import FastAPI, File, UploadFile,Form
from fastapi.middleware.cors import CORSMiddleware
from gerador_xml.gerador_xml import GeradorXML
from io import StringIO
from datetime import datetime
from gerador_xml.registrar_na_gcp import registrar_na_gcp
   
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.get("/")
def index():
    return {"greeting": "Hello world"}


@app.post("/gerar_xml")
async def gerar_xml(file: UploadFile=File(...), operadora: str = Form(...), tipo_produto: str = Form(...), usuario: str = Form(...)):
    # Gera o(s) arquivo(s) XML a partir dos inputs do usuário.

    arquivo_lido = await file.read()
    s=str(arquivo_lido,'utf-8')
    data = StringIO(s) 

    bucket = 'log-portal-ss'
    data_evento = datetime.now().strftime("%Y%m%d_%H%M%S")
    subpasta_json = 'eventos/'

    try:
        gerador = GeradorXML(base_input=data, operadora=operadora, tipo_produto=tipo_produto, usuario=usuario)
        print('Instância do geradorXML criada. Gerando os XMLs...')

    except Exception as e:
        msg_erro = 'Não foi possível criar uma instância do geradorXML.'
        print('\n' + msg_erro)
        print(e)

        json_object = {
            'tipo_evento' : 'gerar_xml',
            'resultado_evento' : 'falha',
            'mensagem_erro' : f'{msg_erro} - Erro: {e}',
            'usuario' : usuario,
            'data' : datetime.now(),
            'operadora' : operadora,
            'tipo_produto' : tipo_produto,
            'valor_arquivo' : None,
            'nome_arquivo' : None,
            'url_gcp': None,
            'valor_total_gerado' : None
        }
            # Registra arquivo json na GCP
        nome_arquivo_json = f'{operadora}_{data_evento}_{tipo_produto}_falha.json'
        registrar_na_gcp(content=json_object, bucket=bucket, filename=f'{subpasta_json}{nome_arquivo_json}', type='json')
        
        return {"mensagem": "Não foi possível criar uma instância do geradorXML.",
                "exception" : str(e)}

    # Gera os XML
    try:
        arquivos_xml, num_guias, numero_arquivos_xml, valor_total_arquivos, avisos, lista_seq_transacao = gerador.gera_xml()
        print('\nGeração de XMLs finalizada.')

        return {"mensagem": "Arquivo(s) XML gerado(s) com sucesso.",
                "arquivos_xml" : arquivos_xml,
                "num_guias" : num_guias,
                "numero_arquivos_xml" : numero_arquivos_xml,
                "valor_total_arquivos" : valor_total_arquivos,
                "avisos" : avisos,
                "lista_seq_transacao" : lista_seq_transacao}

    except Exception as e:
        msg_erro = 'A instância do geradorXML foi criada, mas ocorreu um erro ao tentar gerar os XMLs.'
        print('\n' + msg_erro)
        print(e)

        json_object = {
            'tipo_evento' : 'gerar_xml',
            'resultado_evento' : 'falha',
            'mensagem_erro' : f'{msg_erro} - Erro: {e}',
            'usuario' : usuario,
            'data' : datetime.now(),
            'operadora' : operadora,
            'tipo_produto' : tipo_produto,
            'valor_arquivo' : None,
            'nome_arquivo' : None,
            'url_gcp': None,
            'valor_total_gerado' : None
        }
            # Registra arquivo json na GCP
        nome_arquivo_json = f'{operadora}_{data_evento}_{tipo_produto}_falha.json'
        registrar_na_gcp(content=json_object, bucket=bucket, filename=f'{subpasta_json}{nome_arquivo_json}', type='json')

        return {"mensagem": 'Ocorreu um erro ao tentar gerar os XMLs.',
                "exception" : str(e)}