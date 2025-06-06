import requests
import pandas as pd

ANILIST_API_URL = "https://graphql.anilist.co"
OMDB_API_KEY = ""  # Substitua pela sua chave

QUERY = """
query ($page: Int, $perPage: Int) {
  Page(page: $page, perPage: $perPage) {
    media(type: ANIME, sort: POPULARITY_DESC) {
      id
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
      studios(isMain: true) {
        nodes {
          name
        }
      }
      staff {
        edges {
          role
          node {
            name {
              full
            }
          }
        }
      }
    }
  }
}
"""

def mapear_classificacao_pegi(rated):
    mapa = {
        "TV-Y": "Livre", "TV-G": "Livre", "TV-PG": "10+", "TV-14": "14+",
        "TV-MA": "16+", "G": "Livre", "PG": "10+", "PG-13": "12+",
        "R": "16+", "NC-17": "18+", "X": "18+", "NR": "Livre", "UR": "Livre", "": "Livre"
    }
    return mapa.get(rated, rated if rated else "Livre")

def buscar_dados_omdb(titulo, ano):
    for tentativa in [titulo, titulo.split()[0]]:
        params = {"t": tentativa, "y": ano, "apikey": OMDB_API_KEY}
        try:
            r = requests.get("http://www.omdbapi.com/", params=params)
            data = r.json()
            if data.get("Response") == "True":
                imdb = data.get("imdbRating", "NULL")
                rated = mapear_classificacao_pegi(data.get("Rated", ""))
                temporadas = data.get("totalSeasons", "NULL")
                diretor = data.get("Director", "")
                return imdb, rated, temporadas, diretor
        except:
            continue
    return "NULL", "Livre", "NULL", ""

def extrair_produtor_dos_dados_anilist(item, diretor_omdb):
    # Se houver diretor válido da OMDb
    if diretor_omdb and diretor_omdb != "N/A":
        return diretor_omdb

    # Caso contrário, tenta staff de AniList
    for membro in item.get("staff", {}).get("edges", []):
        role = membro.get("role", "").lower()
        nome = membro.get("node", {}).get("name", {}).get("full", "")
        if "director" in role or "original creator" in role:
            return nome

    # Se nada, tenta estúdio principal
    studios = item.get("studios", {}).get("nodes", [])
    if studios:
        return studios[0].get("name", "NULL")

    return "NULL"

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
                imdb, rated, temporadas, diretor = buscar_dados_omdb(nome_ingles, ano)
                produtor = extrair_produtor_dos_dados_anilist(item, diretor)

                resultados.append({
                    "Plataforma": "Crunchyroll",
                    "Título": nome_ingles,
                    "Tipo de Conteúdo": item.get("format", "ANIME"),
                    "Ano de Lançamento": ano,
                    "Nº Temporadas/Filmes na Saga": temporadas,
                    "Nº de Episódios": item.get("episodes", "NULL"),
                    "Género": "ANIME",
                    "Produtor/Artista": produtor,
                    "Classificação IMDb": imdb,
                    "Classificação Etária (PEGI)": rated,
                    "Duração (minutos)": item.get("duration", "")
                })

                if len(resultados) >= 1000:
                    return resultados

    return resultados

def exportar_csv(dados, nome="crunchyroll_animes.csv"):
    df = pd.DataFrame(dados)
    df.to_csv(nome, index=False, sep=";", encoding="utf-8")
    print(f"✅ Exportado para: {nome}")

if __name__ == "__main__":
    animes = buscar_animes_crunchyroll(paginas=40)
    exportar_csv(animes)
