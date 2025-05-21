import requests
import base64
import pandas as pd
import random

CLIENT_ID = "9e924b4abc484e21950667be3fb7e0d9"
CLIENT_SECRET = "30bd753b7d1f4abf9e958e06479586d4"

def get_access_token(client_id, client_secret):
    auth_url = "https://accounts.spotify.com/api/token"
    auth_header = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()

    response = requests.post(
        auth_url,
        headers={
            "Authorization": f"Basic {auth_header}",
            "Content-Type": "application/x-www-form-urlencoded"
        },
        data={"grant_type": "client_credentials"}
    )

    if response.status_code != 200:
        print("❌ Erro ao obter token de acesso! Verifica credenciais ou permissões.")
        exit(1)

    return response.json()["access_token"]

def get_spotify_content(token, tipo="musica", mercado="US", modo="populares", limite=100):
    headers = {"Authorization": f"Bearer {token}"}
    resultados = []
    vistos = set()
    generos = ["pop", "rock", "jazz", "hip hop", "classical", "indie", "metal", "folk", "trap", "funk", "edm"]

    if tipo == "musica":
        if modo == "populares":
            for genre in generos:
                params = {
                    "q": f"genre:{genre}",
                    "type": "track",
                    "market": mercado,
                    "limit": 20
                }
                r = requests.get("https://api.spotify.com/v1/search", headers=headers, params=params)
                items = r.json().get("tracks", {}).get("items", [])
                for item in items:
                    chave = (item["name"].lower(), item["artists"][0]["name"].lower())
                    if chave in vistos:
                        continue
                    vistos.add(chave)
                    resultados.append({
                        "Plataforma": "Spotify",
                        "Título": item["name"],
                        "Tipo": "Música",
                        "Ano de Lançamento": item["album"]["release_date"][:4],
                        "Nº Temporadas/Filmes na Saga": "NULL",
                        "Nº de Episódios": "NULL",
                        "Género": genre,
                        "Produtor/Artista": item["artists"][0]["name"],
                        "Classificação IMDb": "NULL",
                        "Classificação Etária (PEGI)": "18+" if item["explicit"] else "Livre",
                        "Duração (minutos)": round(item["duration_ms"] / 60000, 2)
                    })
                    if len(resultados) >= limite:
                        return resultados
        elif modo == "aleatorio":
            while len(resultados) < limite:
                genre = random.choice(generos)
                letra = random.choice("abcdefghijklmnopqrstuvwxyz")
                params = {
                    "q": f"{letra} genre:{genre}",
                    "type": "track",
                    "market": mercado,
                    "limit": 20
                }
                r = requests.get("https://api.spotify.com/v1/search", headers=headers, params=params)
                items = r.json().get("tracks", {}).get("items", [])
                for item in items:
                    chave = (item["name"].lower(), item["artists"][0]["name"].lower())
                    if chave in vistos:
                        continue
                    vistos.add(chave)
                    resultados.append({
                        "Plataforma": "Spotify",
                        "Título": item["name"],
                        "Tipo": "Música",
                        "Ano de Lançamento": item["album"]["release_date"][:4],
                        "Nº Temporadas/Filmes na Saga": "NULL",
                        "Nº de Episódios": "NULL",
                        "Género": genre,
                        "Produtor/Artista": item["artists"][0]["name"],
                        "Classificação IMDb": "NULL",
                        "Classificação Etária (PEGI)": "18+" if item["explicit"] else "Livre",
                        "Duração (minutos)": round(item["duration_ms"] / 60000, 2)
                    })
                    if len(resultados) >= limite:
                        return resultados
    elif tipo == "podcast":
        for letra in random.sample("abcdefghijklmnopqrstuvwxyz", 10):
            params = {
                "q": letra,
                "type": "show",
                "market": mercado,
                "limit": 20
            }
            r = requests.get("https://api.spotify.com/v1/search", headers=headers, params=params)
            items = r.json().get("shows", {}).get("items", [])
            for item in items:
                chave = item["name"].lower()
                if chave in vistos:
                    continue
                vistos.add(chave)
                resultados.append({
                    "Plataforma": "Spotify",
                    "Título": item["name"],
                    "Tipo": "Podcast",
                    "Ano de Lançamento": item.get("release_date", "NULL"),
                    "Nº Temporadas/Filmes na Saga": "NULL",
                    "Nº de Episódios": item.get("total_episodes", ""),
                    "Género": item.get("genres", [""])[0] if item.get("genres") else "NULL",
                    "Produtor/Artista": item["publisher"],
                    "Classificação IMDb": "NULL",
                    "Classificação Etária (PEGI)": "18+" if item.get("explicit") else "Livre",
                    "Duração (minutos)": "NULL"
                })
                if len(resultados) >= limite:
                    return resultados
    return resultados

def export_to_csv(conteudos, nome_ficheiro="spotify_conteudos.csv"): #Ajustar o nome do ficheiro
    df = pd.DataFrame(conteudos)
    df.to_csv(nome_ficheiro, index=False, sep=";")
    print(f"\n✅ Exportado para: {nome_ficheiro}")

if __name__ == "__main__":
    tipo = input("Tipo de conteúdo (musica/podcast): ").strip().lower()
    mercado = input("País (código ISO, ex: PT, BR, US): ").strip().upper()
    modo = input("Modo (populares/aleatorio): ").strip().lower()
    token = get_access_token(CLIENT_ID, CLIENT_SECRET)
    conteudos = get_spotify_content(token, tipo=tipo, mercado=mercado, modo=modo, limite=100)
    export_to_csv(conteudos)



#populares: usa playlists editoriais ou rankings
#aleatorio: busca por género ou artista aleatório
           #No caso de música, ele usa géneros e letras iniciais para gerar variedade.
           #No caso de podcasts, faz buscas aleatórias com várias letras.



#CLIENT_ID = "9e924b4abc484e21950667be3fb7e0d9"
#CLIENT_SECRET = "30bd753b7d1f4abf9e958e06479586d4"