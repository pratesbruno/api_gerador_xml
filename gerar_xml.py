import sys
import getopt
from gerador_xml.gerador_xml import GeradorXML

def main(argv):
   try:
      opts, args = getopt.getopt(argv,"b:t:o:s:p:",["base_input=","tipo_input=", "operadora=", "seq_transacao=", "tipo_produto="])
   except getopt.GetoptError:
      print('É preciso passar os seguintes argumentos: --base_input --tipo_input --operadora --seq_transacao --tipo_produto')
      sys.exit(2)
   for opt, arg in opts:
      if opt in ("-b", "--base_input"):
         base_input = arg
         if type(base_input) != str:
            print('"base_input" deve ser uma string com o nome do arquivo base (csv).' )

      elif opt in ("-t", "--tipo_input"):
         tipo_input = arg
         if type(tipo_input) != str:
            print('"tipo_input" deve ser uma string indicando o tipo do input ("csv", "excel" ou "sql").' )

      elif opt in ("-o", "--operadora"):
         operadora = arg
         if type(operadora) != str:
            print('"operadora" deve ser uma string com o nome da operadora.' )

      elif opt in ("-s", "--seq_transacao"):
         try:
            seq_transacao = int(arg)
         except:
            print('"seq_transacao" deve ser um número inteiro indicando o sequencial do XML/lote (número único)' )
      
      elif opt in ("-p", "--tipo_produto"):
         tipo_produto = arg
         if type(tipo_produto) != str:
            print('"tipo_produto" deve ser uma string indicando se o produto é "lab" (para exames) ou "vac" (para vacinas).' )

   try:
      gerador = GeradorXML(base_input=base_input, tipo_input=tipo_input, operadora=operadora, seq_transacao=seq_transacao)
      print('Instância do geradorXML criada. Gerando os XMLs...')
      gerador.gera_xml(tipo_produto=tipo_produto)
   except:
      print('\nNão foi possível criar uma instância do geradorXML.')
      print('Verifique se todos os seguintes argumentos foram passados da maneira correta:\n--base_input --tipo_input --operadora --seq_transacao --tipo_produto')
   
if __name__ == '__main__':
    main(sys.argv[1:])
