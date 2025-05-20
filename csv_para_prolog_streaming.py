import pandas as pd
import unicodedata

# Caminho para o CSV original
ficheiro_csv = "Plataformas_Streaming.csv"
ficheiro_saida = "Plataformas_Streaming.pl"

# Função para normalizar strings como átomos válidos em Prolog
def normalizar(texto):
    texto = str(texto).strip().lower()
    texto = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('utf-8')
    return texto.replace(" ", "_").replace("(", "").replace(")", "").replace("-", "_")

# Ler CSV com codificação e delimitador correto
df = pd.read_csv(ficheiro_csv, sep=';', encoding='latin1')
df.fillna('', inplace=True)

# Função para converter uma linha em facto Prolog
def linha_para_prolog(row):
    nome = str(row['Nome']).replace("'", "\\'")

    tipo = normalizar(row['Tipo'])
    modelo = normalizar(row['Modelo de Pagamento'])

    try:
        ano = int(row['Data de Lançamento'])
    except:
        ano = 0

    pais = str(row['País de Origem']).replace("'", "\\'")

    try:
        assinantes = float(str(row['Assinantes (milhões)']).replace(',', '.'))
    except:
        assinantes = 0.0

    catalogo = normalizar(row['Catálogo Principal'])
    if catalogo == '':
        catalogo = 'sem_catalogo'

    original = normalizar(row['Conteúdo Original'])
    if original not in ['sim', 'nao']:
        original = 'nao'

    try:
        preco = float(str(row['Preço Mensal Base (€)']).replace(',', '.'))
    except:
        preco = 0.0

    return f"plataforma('{nome}', {tipo}, {modelo}, {ano}, '{pais}', {assinantes}, {catalogo}, {original}, {preco})."

# Gerar os factos
factos = [linha_para_prolog(row) for _, row in df.iterrows()]

# Guardar no ficheiro .pl
with open(ficheiro_saida, "w", encoding="utf-8") as f:
    f.write('\n'.join(factos))

print("✔️ Ficheiro Prolog gerado com sucesso:", ficheiro_saida)

