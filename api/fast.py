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


@app.post("/gerar_xml")
async def gerar_xml(file: UploadFile=File(...), operadora: str = Form(...), tipo_produto: str = Form(...)):
    # Gera o(s) arquivo(s) XML a partir dos inputs do usuário.

    arquivo_lido = await file.read()
    s=str(arquivo_lido,'utf-8')
    data = StringIO(s) 

    try:
        gerador = GeradorXML(base_input=data, operadora=operadora, tipo_produto=tipo_produto)
        print('Instância do geradorXML criada. Gerando os XMLs...')

    except Exception as e:
        print('\nNão foi possível criar uma instância do geradorXML.')
        print(e)
        return {"mensagem": "Não foi possível criar uma instância do geradorXML.",
                "exception" : str(e)}
    

    # Gera os XML
    try:
        arquivos_xml, num_guias, numero_arquivos_xml, valor_total_arquivos, avisos = gerador.gera_xml()
        print('\nGeração de XMLs finalizada.')
 
        return {"mensagem": "Arquivo(s) XML gerado(s) com sucesso.",
                "arquivos_xml" : arquivos_xml,
                "num_guias" : num_guias,
                "numero_arquivos_xml" : numero_arquivos_xml,
                "valor_total_arquivos" : valor_total_arquivos,
                "avisos" : avisos}

    except Exception as e:
        print('A instância do geradorXML foi criada, mas ocorreu um erro ao tentar gerar os XMLs.')
        print(e)
        return {"mensagem": 'Ocorreu um erro ao tentar gerar os XMLs.',
                "exception" : str(e)}