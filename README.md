# LC-Repository — Base de Conhecimento sobre Plataformas de Streaming

Este repositório reúne scrapers personalizados, bases de dados em formato CSV e conhecimento lógico em Prolog sobre plataformas de streaming e o seu respetivo conteúdo (vídeo, música, anime e entre outros). É parte de um trabalho da cadeira Lógica Computacional, do curso de Engenharia Informática, onde a informação recolhida é estruturada, analisada e usada num sistema pericial para ajudar o utilizador a encontrar conteúdos com base em preferências.

## 📁 Estrutura do Projeto

```
LC-Repository/
├── Scrapers/                    # Scripts de scraping (Spotify, TMDB, AniList, JustWatch)
├── Ficheiros csv Iniciais/      # Dados brutos recolhidos pelos scrapers
├── Ficheiros csv Finais/        # CSVs normalizados para base de conhecimento
├── Versão Final/                # Sistema pericial final com base de conhecimento (Prolog)
├── Perito Original/             # Primeira versão do motor pericial, fornecido pelos professores da cadeira
├── README.md                    # Este ficheiro
```

## 🔍 Objetivo

- Recolher dados reais de plataformas como Spotify, Netflix, Disney+, Crunchyroll, etc.
- Normalizar os dados num formato comum com atributos como título, género, ano, duração, IMDb, PEGI, produtor, tipo de conteúdo (Filme/Série/Música/Podcast).
- Criar uma base de conhecimento Prolog que alimente um sistema pericial capaz de recomendar conteúdos ou indicar onde encontrar um título.

## ⚙️ Scrapers disponíveis

Os scripts estão na pasta `Scrapers/`:

- `spotify_scraper.py` – Músicas e podcasts populares/aleatórios por país, da plataforma [Spotify](https://developer.spotify.com)
- `tmdb_scraper_100.py` / `tmdb_scraper_1000.py` – Filmes e séries de diferentes plataformas (Netflix, Disney+, etc.), através da base de dados [The Movie Database](https://www.themoviedb.org)
- `anilist_scraper.py` – Animes disponíveis em diferentes plataformas, através do site [Anilist](https://anilist.co/home) com utilização da API [OMDb](https://www.omdbapi.com) para completar dados
- `justwatch_app.py` – Scraper com extração por título do site [JustWatch](https://www.justwatch.com) complementado com uso da API OMDb para mais dados

> ⚠️ Alguns scrapers usam APIs que requerem chaves (`API_KEY`) e headers personalizados. Ver comentários nos scripts.

## 📦 Dados Recolhidos

Os CSVs iniciais estão organizados por plataforma e origem na pasta `Ficheiros csv Iniciais/`. Incluem:

- Filmes e séries de plataformas de vídeo
- Músicas e podcasts de Spotify (vários países)
- Animes de Crunchyroll e HiDive

Exemplos:
```
conteudos_tmdb_1000_filmes_Netflix.csv
spotify_conteudos_PT_Musica_Populares.csv
animes_hidive.csv
```

## 🔄 Dados Finalizados

Os dados foram consolidados nos seguintes ficheiros:

- `Plataformas_Streaming.csv` – Lista de plataformas normalizadas
- `Conteudo_Plataformas_Streaming.csv` – Base de conteúdos normalizada

Estes dados estão prontos para serem usados no sistema pericial.

## 🧠 Sistema Pericial

A versão final do sistema encontra-se em `Versão Final/`:

- `base_streaming.pl` – Base de factos em Prolog com conteúdos e plataformas
- `Perito.pl` – Motor de inferência baseado em perguntas ao utilizador

## ▶️ Como utilizar

Para correr o sistema pericial:

1. Abra um terminal e navegue até à pasta `Versão Final/`.
2. Inicia o interpretador Prolog (ex: [SWI-Prolog](https://www.swi-prolog.org/)).

```text
swipl Perito.pl
```

3. No terminal do Prolog, carregue o motor de inferência:

```text
?- perito.
```

4. Consulte a base de conhecimento:

```text
> 1.
Nome da BC: |: base_streaming.
```

5. Escolha a opção Solucionar e indique se pretende procurar um conteúdo com base em atributos ou descobrir em que plataforma se encontra um determinado título:

```text
> |: 2.
Pretende procurar por atributos (1) ou indicar um conteudo (2)?
|: 1. 
```

No caso de *procurar por atributos (1)*, o sistema irá interagir com o utilizador através de perguntas que irão diferir segundo o tipo de conteúdo que é escolhido. As perguntas que podem ser feitas sobre as preferências são:

- Tipo de conteúdo (TV, Série, Filme, Música, Podcast, OVA)
- Género (Anime, Ação, Comédia, Drama, etc.)
- Classificação etária (PEGI)
- Ano de lançamento
- Classificação IMDb
- Número de temporadas
- Número de episódios
- Produtor / Artista
- Tempo de duração

O utilizador pode usar 'null.' como resposta para não ser considerada essa preferência.


```text
> |: 2.
Pretende procurar por atributos (1) ou indicar um conteudo (2)?
|: 2. 
```

No caso de *indicar um conteúdo (2)*, irá ser perguntado ao utilizador se sabe o nome completo desse mesmo. Caso saiba, é então perguntado qual é esse nome, sendo então devolvida a plataforma de streaming em que esse se encontra. No caso de não saber, pergunta então parte do nome do conteúdo, tipo, ano e género para assim devolver a plataforma de streaming com esse conteúdo disponível.

6. Quando terminar, o utilizador pode:

- Voltar a selecionar a opção **Solucionar** caso deseje realizar uma nova pesquisa;
- Ou escolher a opção **Sair** para encerrar o sistema:

```text
> |: 3.
```

> 💡 Nota: a opção "Sair" termina a interação com o sistema pericial e encerra o programa Prolog, se for a única coisa carregada.

## 🙋 Autores

[JadfPT](https://github.com/JadfPT)
[imdtcode](https://github.com/imdtcode)

## 📜 Licença

Este projeto é académico e sem fins lucrativos. Uso de scrapers e dados destina-se apenas a fins educativos.