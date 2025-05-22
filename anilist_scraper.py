import requests
import pandas as pd

ANILIST_API_URL = "https://graphql.anilist.co"
OMDB_API_KEY = " "  # Substitua pela sua chave de API do OMDB

QUERY = """
query ($page: Int, $perPage: Int) {
  Page(page: $page, perPage: $perPage) {
    media(type: ANIME, sort: POPULARITY_DESC) {
      title {
        romaji
        english
      }
      format
      episodes
      duration
      startDate {
        year
      }
      streamingEpisodes {
        site
        title
        url
      }
    }
  }
}
"""

def mapear_classificacao_pegi(rated):
    mapa = {
        "TV-Y": "Livre",
        "TV-G": "Livre",
        "TV-PG": "10+",
        "TV-14": "14+",
        "TV-MA": "16+",
        "G": "Livre",
        "PG": "10+",
        "PG-13": "12+",
        "R": "16+",
        "NC-17": "18+",
        "X": "18+",
        "NR": "Livre",
        "UR": "Livre",
        "": "Livre"
    }
    return mapa.get(rated, rated if rated else "Livre")

def buscar_classificacao_omdb(titulo, ano):
    for tentativa in [titulo, titulo.split()[0]]:
        params = {"t": tentativa, "y": ano, "apikey": OMDB_API_KEY}
        try:
            r = requests.get("http://www.omdbapi.com/", params=params)
            data = r.json()
            if data.get("Response") == "True":
                imdb = data.get("imdbRating", "NULL")
                rated = mapear_classificacao_pegi(data.get("Rated", ""))
                return imdb, rated
        except:
            continue
    return "NULL", "Livre"

def buscar_animes_crunchyroll(paginas=40):
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    resultados = []
    vistos = set()

    for page in range(1, paginas + 1):
        variables = {"page": page, "perPage": 50}
        response = requests.post(ANILIST_API_URL, json={"query": QUERY, "variables": variables}, headers=headers)
        data = response.json()

        for item in data['data']['Page']['media']:
            streams = item.get("streamingEpisodes", [])
            if any(s.get("site") == "Crunchyroll" for s in streams):
                nome_romaji = item['title'].get('romaji', '')
                nome_ingles = item['title'].get('english', '') or nome_romaji
                if nome_ingles in vistos:
                    continue
                vistos.add(nome_ingles)
                ano = item.get("startDate", {}).get("year", "")
                imdb, rated = buscar_classificacao_omdb(nome_ingles, ano)
                resultados.append({
                    "Plataforma": "Crunchyroll",
                    "Título": nome_ingles,
                    "Tipo de Conteúdo": item.get("format", "ANIME"),
                    "Ano de Lançamento": ano,
                    "Nº Temporadas/Filmes na Saga": "NULL",
                    "Nº de Episódios": item.get("episodes", "NULL"),
                    "Género": "ANIME",
                    "Produtor/Artista": "NULL",
                    "Classificação IMDb": imdb,
                    "Classificação Etária (PEGI)": rated,
                    "Duração (minutos)": item.get("duration", "")
                })
                if len(resultados) >= 1000:
                    return resultados

    return resultados

def exportar_csv(dados, nome="crunchyroll_animes.csv"): #Ajuste o nome do arquivo conforme necessário
    df = pd.DataFrame(dados)
    df.to_csv(nome, index=False, sep=";", encoding="utf-8")
    print(f"✅ Exportado para: {nome}")

if __name__ == "__main__":
    animes = buscar_animes_crunchyroll(paginas=40)
    exportar_csv(animes)
