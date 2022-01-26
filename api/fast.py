from fastapi import FastAPI, File, UploadFile,Form
from fastapi.middleware.cors import CORSMiddleware
from gerador_xml.gerador_xml import GeradorXML
from io import StringIO
   
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



@app.post("/create_file")
async def create_file(file: UploadFile=File(...), param1: str = Form(...)):
      file2store = await file.read()
      param1 = param1
      return {'file': str(file2store),
              'param1': param1}


@app.post("/gerar_xml")
async def gerar_xml(file: UploadFile=File(...), tipo_input: str = Form(...), operadora: str = Form(...), seq_transacao: int = Form(...), tipo_produto: str = Form(...)):
    # Gera o(s) arquivo(s) XML a partir dos inputs do usuário.

    arquivo_lido = await file.read()
    s=str(arquivo_lido,'utf-8')
    data = StringIO(s) 

    try:
        gerador = GeradorXML(base_input=data, tipo_input=tipo_input, operadora=operadora, seq_transacao=seq_transacao)
        print('Instância do geradorXML criada. Gerando os XMLs...')

    except Exception as e:
        print('\nNão foi possível criar uma instância do geradorXML.')
        print(e)
        return {"mensagem": "Não foi possível criar uma instância do geradorXML.",
                "error" : str(e)}
    
    # Gera os XML
    try:    
        arquivos_xml, num_guias, numero_arquivos_xml, valor_total_arquivos, lista_sequencial_transacao = gerador.gera_xml(tipo_produto=tipo_produto)
        print('\nGeração de XMLs finalizada.')
 
        return {"mensagem": "Arquivo(s) XML gerado(s) com sucesso.",
                "arquivos_xml" : arquivos_xml,
                "num_guias" : num_guias,
                "numero_arquivos_xml" : numero_arquivos_xml,
                "valor_total_arquivos" : valor_total_arquivos,
                "lista_sequencial_transacao" : lista_sequencial_transacao}

    except Exception as e:
        print('A instância do geradorXML foi criada, mas ocorreu um erro ao tentar gerar os XMLs.')
        print(e)
        return {"mensagem": 'A instância do geradorXML foi criada, mas ocorreu um erro ao tentar gerar os XMLs.',
                "error" : str(e)}