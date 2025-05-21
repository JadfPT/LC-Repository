import requests
import pandas as pd
import random

API_KEY = " "  # Substitua pela sua chave de API do TMDB"
BASE_URL = "https://api.themoviedb.org/3"

HEADERS = {}

TIPOS = {
    "filme": "movie",
    "série": "tv",
    "documentário": "movie"
}

PROVIDERS = {
    "netflix": "8",
    "amazon prime": "119",
    "disney+": "337",
    "hbo max": "384",
    "apple tv+": "350",
    "hulu": "15",
    "paramount+": "531",
    "peacock": "386",
    "rakuten tv": "35",
    "youtube": "192",
    "google play": "3",
    "skyshowtime": "619",
    "mubi": "41",
    "filmin": "68"
}

REGIOES_VALIDAS = {
    "US": "United States",
    "BR": "Brazil",
    "PT": "Portugal",
    "GB": "United Kingdom",
    "FR": "France",
    "DE": "Germany",
    "CA": "Canada",
    "ES": "Spain",
    "IN": "India",
    "AU": "Australia",
    "IT": "Italy",
    "MX": "Mexico",
    "AR": "Argentina",
    "JP": "Japan",
    "KR": "South Korea",
    "NL": "Netherlands"
}

def mapear_classificacao(cert):
    mapa = {
        "G": "Livre",
        "PG": "10+",
        "PG-13": "12+",
        "R": "16+",
        "NC-17": "18+",
        "TV-G": "Livre",
        "TV-PG": "10+",
        "TV-14": "14+",
        "TV-MA": "16+",
        "NR": "Livre",
        "UR": "Livre",
        "XX": "18+",
        "X": "18+",
    }
    return mapa.get(cert, "Livre" if not cert else cert)

def buscar_classificacao_etaria(tipo, id_tmdb):
    if tipo == "filme":
        url = f"{BASE_URL}/movie/{id_tmdb}/release_dates"
    else:
        url = f"{BASE_URL}/tv/{id_tmdb}/content_ratings"

    resp = requests.get(url, params={"api_key": API_KEY})
    if resp.status_code != 200:
        return ""

    data = resp.json()

    if tipo == "filme":
        for entry in data.get("results", []):
            if entry.get("iso_3166_1") == "US":
                for rel in entry.get("release_dates", []):
                    cert = rel.get("certification")
                    if cert:
                        return mapear_classificacao(cert)
    else:
        for entry in data.get("results", []):
            if entry.get("iso_3166_1") == "US":
                return mapear_classificacao(entry.get("rating", ""))

    return "Livre"

def buscar_conteudos(tipo="filme", plataforma="netflix", regiao="PT", limite=100, modo="populares"):
    provider_id = PROVIDERS.get(plataforma.lower())
    if not provider_id:
        print(f"❌ Plataforma '{plataforma}' não reconhecida.")
        print("Plataformas disponíveis:")
        for nome in sorted(PROVIDERS):
            print(" -", nome)
        return pd.DataFrame()

    if regiao.upper() == "?":
        print("\n🌍 Regiões válidas sugeridas:")
        for cod, nome in REGIOES_VALIDAS.items():
            print(f" - {cod}: {nome}")
        return pd.DataFrame()

    endpoint = f"{BASE_URL}/discover/{TIPOS[tipo]}"
    base_params = {
        "api_key": API_KEY,
        "sort_by": "popularity.desc",
        "language": "pt-PT",
        "with_watch_providers": provider_id,
        "watch_region": regiao.upper(),
        "with_watch_monetization_types": "flatrate"
    }

    if tipo == "documentário":
        base_params["with_keywords"] = "5340"

    resultados = []
    vistos = set()

    if modo == "populares":
        paginas = [1, 2, 3, 4, 5]
    elif modo == "aleatorio":
        paginas = random.sample(range(1, 101), k=5)
    elif modo == "multipaginas":
        paginas = random.sample(range(1, 101), k=10)
    else:
        paginas = [1]

    for pagina in paginas:
        params = base_params.copy()
        params["page"] = pagina

        resp = requests.get(endpoint, params=params)
        if resp.status_code != 200:
            print("❌ Erro na API:", resp.status_code)
            print(resp.text)
            continue

        data = resp.json()

        for item in data.get("results", []):
            id_unico = item.get("id")
            if id_unico in vistos:
                continue
            vistos.add(id_unico)

            detalhes = requests.get(f"{BASE_URL}/{TIPOS[tipo]}/{id_unico}", params={"api_key": API_KEY}).json()

            titulo = detalhes.get("title") or detalhes.get("name")
            ano = (detalhes.get("release_date") or detalhes.get("first_air_date") or "").split("-")[0]
            if tipo == "série":
                temporadas = detalhes.get("number_of_seasons", "NULL")
                episodios = detalhes.get("number_of_episodes", "NULL")
            else:
                temporadas = "NULL"
                episodios = "NULL"

            generos = ", ".join([g['name'] for g in detalhes.get("genres", [])])

            if tipo == "série":
                criadores = detalhes.get("created_by", [])
                produtor = criadores[0]["name"] if criadores else ""
            else:
                produtoras = detalhes.get("production_companies", [])
                produtor = produtoras[0]["name"] if produtoras else ""

            imdb = detalhes.get("vote_average", "")

            if tipo == "filme":
                duracao = detalhes.get("runtime", "")
            else:
                tempos = detalhes.get("episode_run_time", [])
                duracao = tempos[0] if tempos else ""

            classificacao = buscar_classificacao_etaria(tipo, id_unico)

            resultados.append({
                "Plataforma": plataforma.capitalize(),
                "Título": titulo,
                "Tipo de Conteúdo": tipo.capitalize(),
                "Ano de Lançamento": ano,
                "Nº Temporadas/Filmes na Saga": temporadas,
                "Nº de Episódios": episodios,
                "Género": generos,
                "Produtor/Artista": produtor,
                "Classificação IMDb": imdb,
                "Classificação Etária (PEGI)": classificacao,
                "Duração (minutos)": duracao
            })

            if len(resultados) >= limite:
                break
        if len(resultados) >= limite:
            break

    random.shuffle(resultados)
    return pd.DataFrame(resultados[:limite])

def exportar_csv(df, nome="conteudos_tmdb.csv"): #Ajustar o nome do ficheiro
    df.to_csv(nome, index=False, sep=";", encoding="utf-8")
    print(f"✅ Exportado: {nome}")

if __name__ == "__main__":
    tipo = input("Tipo de conteúdo (filme/série/documentário): ").strip().lower()
    plataforma = input("Plataforma (ex: netflix, prime, disney+): ").strip().lower()
    regiao = input("Região (ex: PT, US, BR ou ? para listar): ").strip().upper()
    modo = input("Modo (populares / aleatorio / multipaginas): ").strip().lower()
    df = buscar_conteudos(tipo=tipo, plataforma=plataforma, regiao=regiao, limite=100, modo=modo)
    exportar_csv(df)



#| Modo           | Resultado                                                          |
#| -------------- | ------------------------------------------------------------------ |
#| `populares`    | Os 100 conteúdos mais populares (primeiras 5 paginas)              |
#| `aleatorio`    | Cinco páginas aleatórias entre 1 e 100 (variação leve)             |
#| `multipaginas` | 10 páginas aleatórias (baralha os resultados e escolhe 100 únicos) |