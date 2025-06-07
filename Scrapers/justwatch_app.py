import requests
import re
import csv
import os
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.microsoft import EdgeChromiumDriverManager
import time

OMDB_API_KEY = ""  # ← Substitui aqui
LIMITE_MAX = 1000
CSV_FILE = "animes_hidive.csv" # Ficheiro CSV para guardar os dados

# Títulos já extraídos
titulos_existentes = set()
if os.path.exists(CSV_FILE):
    with open(CSV_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            titulos_existentes.add(row["Título"])

dados = []

def converter_para_pegi(classificacao):
    mapa = {
        "TV-Y": "3+", "TV-G": "3+", "Livre": "3+", "Not Rated": "3+", "NR": "3+",
        "TV-Y7": "7+",
        "TV-PG": "12+", "TV-14": "12+",
        "R": "16+", "TV-MA": "16+",
        "NC-17": "18+"
    }
    return mapa.get(classificacao.strip(), "NULL")

def buscar_dados_omdb(titulo, ano):
    try:
        url = f"http://www.omdbapi.com/?t={quote_plus(titulo)}&y={ano}&apikey={OMDB_API_KEY}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data.get("Response") == "True":
                tipo_omdb = data.get("Type", "").lower()
                if tipo_omdb == "series":
                    tipo = "TV"
                elif tipo_omdb == "movie":
                    tipo = "Movie"
                else:
                    tipo = "NULL"

                produtor = data.get("Production", "")
                if not produtor or produtor == "N/A":
                    produtor = data.get("Director", "")
                if not produtor or produtor == "N/A":
                    produtor = data.get("Writer", "")
                if not produtor or produtor == "N/A":
                    produtor = data.get("Actors", "")
                if not produtor or produtor == "N/A":
                    produtor = "NULL"
                if produtor and produtor != "NULL":
                    produtor = produtor.replace('"', '').split(",")[0].strip()

                imdb = data.get("imdbRating", "NULL")
                if imdb == "N/A" or not imdb:
                    imdb = "NULL"

                return tipo, produtor, imdb
    except:
        pass
    return "NULL", "NULL", "NULL"

# Setup Selenium
options = Options()
# options.add_argument("--headless")
driver = webdriver.Edge(
    service=Service(EdgeChromiumDriverManager().install()),
    options=options
)

base_url = "https://www.justwatch.com"
page_url = "/us/provider/hidive" # Mudar conforme necessário
pagina = 1

# Criação do ficheiro se não existir
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
        fieldnames = [
            "Plataforma", "Título", "Tipo de Conteúdo", "Ano de Lançamento",
            "Nº Temporadas/Filmes na Saga", "Nº de Episódios", "Género",
            "Produtor/Artista", "Classificação IMDb", "Classificação Etária (PEGI)",
            "Duração (minutos)"
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

while True:
    full_url = f"{base_url}{page_url}"
    print(f"🔎 Acessando: {full_url}")
    driver.get(full_url)

    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "title-list-grid__item"))
        )
    except:
        print("❌ Elementos não carregaram.")
        break

    time.sleep(2)
    blocos = driver.find_elements(By.CLASS_NAME, "title-list-grid__item")
    print(f"📦 Página {pagina} - {len(blocos)} itens encontrados.")

    titulos_links = []
    for bloco in blocos:
        try:
            link = bloco.find_element(By.CLASS_NAME, "title-list-grid__item--link").get_attribute("href")
            titulo = bloco.find_element(By.CLASS_NAME, "picture-comp__img").get_attribute("alt")
            if titulo not in titulos_existentes:
                titulos_links.append((titulo, link))
        except:
            continue

    for i, (titulo, link) in enumerate(titulos_links):
        if len(titulos_existentes) + len(dados) >= LIMITE_MAX:
            print("🛑 Limite de 1000 conteúdos atingido.")
            break
        try:
            driver.get(link)
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CLASS_NAME, "title-detail-hero-details__item"))
            )
            time.sleep(1)

            duracao = "NULL"
            classificacao_imdb = "NULL"
            classificacao_pegi = "NULL"
            ano = "NULL"
            temporadas = "NULL"
            episodios = "NULL"

            detalhes = driver.find_elements(By.CLASS_NAME, "title-detail-hero-details__item")
            for detalhe in detalhes:
                texto = detalhe.text.strip()
                if "min" in texto or "h" in texto:
                    texto_limpo = texto.lower().replace("min", "").replace("m", "").strip()
                    match = re.match(r"(?:(\d+)h)?\s*(\d+)?", texto_limpo)
                    if match:
                        horas = int(match.group(1)) if match.group(1) else 0
                        minutos = int(match.group(2)) if match.group(2) else 0
                        duracao = str(horas * 60 + minutos)
                    else:
                        duracao = re.sub(r"[^\d]", "", texto)
                elif any(x in texto for x in ["TV-", "Livre", "Not Rated", "NR", "R", "G"]):
                    classificacao_pegi = converter_para_pegi(texto.split()[0])
                elif "IMDb" in texto:
                    try:
                        classificacao_imdb = driver.find_element(By.CLASS_NAME, "imdb-score").text.strip().split()[0]
                    except:
                        soup = BeautifulSoup(driver.page_source, "html.parser")
                        imdb_elem = soup.select_one(".imdb-score")
                        if imdb_elem:
                            classificacao_imdb = imdb_elem.text.strip().split()[0]

            try:
                ano = driver.find_element(By.CLASS_NAME, "release-year").text.strip("()")
            except:
                pass

            try:
                episodio_info = driver.find_element(By.XPATH, "//span[contains(text(), 'S') and contains(text(), 'E')]").text.strip()
                match = re.match(r"S(\d+)\s*E(\d+)", episodio_info)
                if match:
                    temporadas = match.group(1)
                    episodios = match.group(2)
            except:
                pass

            tipo_conteudo, produtor, imdb_omdb = buscar_dados_omdb(titulo, ano)
            if classificacao_imdb == "NULL" and imdb_omdb != "NULL":
                classificacao_imdb = imdb_omdb

            if tipo_conteudo == "NULL":
                if "/movie/" in link:
                    tipo_conteudo = "Movie"
                elif "/tv-show/" in link:
                    tipo_conteudo = "TV"

            entrada = {
                "Plataforma": "HIDIVE", # Plataforma do serviço
                "Título": titulo,
                "Tipo de Conteúdo": tipo_conteudo,
                "Ano de Lançamento": ano,
                "Nº Temporadas/Filmes na Saga": temporadas,
                "Nº de Episódios": episodios,
                "Género": "ANIME",
                "Produtor/Artista": produtor,
                "Classificação IMDb": classificacao_imdb,
                "Classificação Etária (PEGI)": classificacao_pegi,
                "Duração (minutos)": duracao
            }

            dados.append(entrada)
            titulos_existentes.add(titulo)

            # Append imediato ao CSV
            with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=entrada.keys())
                writer.writerow(entrada)

            print(f"✅ [{len(titulos_existentes)}] {titulo} salvo.")

        except Exception as e:
            print(f"⚠ Erro no item {i+1} da página {pagina}: {e}")

    if len(titulos_existentes) >= LIMITE_MAX:
        break

    try:
        next_buttons = driver.find_elements(By.CSS_SELECTOR, "a.link-item[href*='page=']")
        proxima_pagina_url = None
        for botao in next_buttons:
            href = botao.get_attribute("href")
            if f"page={pagina+1}" in href:
                proxima_pagina_url = href
                break

        if not proxima_pagina_url:
            print("✅ Fim da paginação.")
            break

        page_url = proxima_pagina_url.replace(base_url, "")
        pagina += 1

    except Exception as e:
        print(f"✅ Erro ao buscar próxima página: {e}")
        break

driver.quit()
print(f"🎉 Total final: {len(titulos_existentes)} títulos guardados.")
