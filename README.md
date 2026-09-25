# CinéData

Projet 1, Phase 4 — Bloc de compétences 1 (Dev IA).
Pipeline ETL (Extract / Transform / Load) de données cinéma, à partir de trois sources hétérogènes, chargées dans une base relationnelle.

> **Statut : pipeline de données terminé et fonctionnel.** L'API REST (FastAPI) est la prochaine phase de développement, pas encore présentée aux étudiants — ce README sera complété à ce moment-là.

---

## Objectif

Construire un jeu de données cinéma unifié à partir de trois sources différentes (API, fichier CSV, scraping web), le modéliser en base relationnelle, en vue d'une future exposition via une API REST.

## Sources de données

| Source | Type | Contenu | Script |
|---|---|---|---|
| [API TMDB](https://developer.themoviedb.org/docs) | API REST | Films populaires (100 pages), détails, casting/réalisation | `extract_api_tmdb.py` |
| [MovieLens (ml-latest-small)](https://grouplens.org/datasets/movielens/) | Fichier CSV | Notes moyennes, nombre d'avis, tags — filtré sur les films déjà extraits de TMDB | `extract_csv_movielens.py` |
| Wikipedia (EN) | Scraping | Résumé, musique, sociétés de production — recherche par titre + vérification par année | `extract_web_wikipedia.py` |

L'API TMDB est la source principale : les deux autres branches enrichissent uniquement les films déjà identifiés par l'extraction TMDB.

## Pipeline ETL

Voir [`docs/pipeline_etl.md`](docs/pipeline_etl.md) pour le détail complet (diagrammes Mermaid : vue d'ensemble, extraction TMDB en 3 phases, schéma de base de données).

```
extract_api_tmdb.py ─┐
extract_csv_movielens.py ├─→ data/raw/*.json   (Extract)
extract_web_wikipedia.py ─┘
                              │
                    transform.py   (Transform)
                              │
              data/processed/films_transformes.json
                              │
                       load.py   (Load)
                              │
                     data/cinedata.db
```

## Structure du projet

```
cinedata/
├── .env.example
├── .gitignore
├── README.md
├── requirements.txt
├── config.yaml             # constantes du projet (URLs, dossiers, timeouts...)
├── data/
│   ├── raw/                # sorties brutes des extractions (JSON, CSV MovieLens)
│   ├── processed/          # sortie de transform.py
│   └── cinedata.db         # base SQLite (générée, non versionnée)
├── sql/
│   ├── schema.sql          # schéma de la base de données (6 tables)
│   ├── movies_list.sql, movies_count.sql, movie_detail.sql
│   └── top_actor.sql, top_director.sql, top_revenue.sql, top_budget.sql
├── docs/
│   └── pipeline_etl.md     # diagrammes du pipeline et du schéma de données
├── notebooks/
│   ├── extract_api_exploration.ipynb
│   ├── poo_demo_comparative.ipynb
│   ├── scraping_demo.ipynb
│   └── modelisation_demo_v2.ipynb
└── src/
    ├── extract_api_tmdb.py         # Extract — API TMDB (3 phases)
    ├── extract_csv_movielens.py    # Extract — CSV MovieLens
    ├── extract_web_wikipedia.py    # Extract — scraping Wikipedia
    ├── transform.py                # Transform — fusion des 3 sources
    ├── load.py                     # Load — écriture en base
    └── db.py                       # fonctions de création/insertion réutilisées par load.py
```

## Installation

```bash
python -m venv venv
source venv/bin/activate   # ou venv\Scripts\Activate.ps1 sous Windows
pip install -r requirements.txt
cp .env.example .env       # puis renseigner TMDB_API_KEY
```

Télécharger et dézipper le jeu de données [MovieLens ml-latest-small](https://files.grouplens.org/datasets/movielens/ml-latest-small.zip) dans `data/raw/ml-latest-small/`.

## Utilisation

```bash
python src/extract_api_tmdb.py        # -> data/raw/tmdb_movies.json
python src/extract_csv_movielens.py   # -> data/raw/movielens_avis.json
python src/extract_web_wikipedia.py   # -> data/raw/wikipedia_misc.json

python src/transform.py               # -> data/processed/films_transformes.json
python src/load.py                    # -> data/cinedata.db
```

Tous les chemins, URLs, pauses entre requêtes et autres constantes sont centralisés dans `config.yaml`.

## État d'avancement

- [x] Extraction API TMDB (3 phases : films populaires, détails, casting/réalisation)
- [x] Extraction CSV MovieLens (notes agrégées, tags)
- [x] Extraction par scraping Wikipedia (recherche + vérification par année)
- [x] Transform : fusion des 3 sources, normalisation
- [x] Modélisation et chargement en base SQLite (schéma à 6 tables)
- [ ] API REST (FastAPI) — prochaine phase
- [ ] Note technique de fin de projet

## Notes techniques

- Base de données : SQLite (fichier local, pas de serveur à configurer)
- Aucune donnée personnelle identifiante collectée
- Clé API TMDB gérée via variable d'environnement (`.env`, non versionné)
- Gestion du rate limit (429) et des erreurs réseau centralisée dans chaque script d'extraction — un échec ponctuel n'interrompt jamais tout le pipeline
- `data_transformee: data/processed` — convention de nommage alignée sur les autres projets

---

*Auteur : RémiJ — Projet réalisé dans le cadre de la formation Développeur d'application IA.*