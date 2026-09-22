# CinéData

Projet 1, Phase 4 — Bloc de compétences 1 (Dev IA).
Collecte, agrégation, stockage et mise à disposition de données cinéma, à partir de plusieurs sources hétérogènes.

> **Statut : projet en cours.** Ce README sera complété au fil de la semaine (installation détaillée, documentation de l'API, résultats). Version actuelle : structure du projet + sources de données.

---

## Objectif

Construire un jeu de données cinéma unifié à partir de trois sources différentes, et le rendre accessible via une API REST — dans une logique de préparation à un futur usage IA (recommandation).

## Sources de données

| Source | Type | Contenu |
|---|---|---|
| [API TMDB](https://developer.themoviedb.org/docs) | API REST | Films populaires, détails, genres, casting |
| [MovieLens (ml-latest-small)](https://grouplens.org/datasets/movielens/) | Fichier CSV | Avis / notes utilisateurs, avec correspondance vers l'id TMDB |
| Wikipedia | Scraping | Compléments (réalisateur, durée, résumé) |

## Structure du projet

```
cinedata/
├── .env.example          # variables attendues (clé API), sans les valeurs réelles
├── .gitignore
├── README.md              # ce fichier
├── requirements.txt
├── data/
│   ├── raw/               # données brutes extraites (JSON, CSV MovieLens)
│   └── cinedata.db        # base SQLite (générée, non versionnée)
├── sql/
│   └── schema.sql         # schéma de la base de données
├── notebooks/
│   ├── extract_api_exploration.ipynb
│   ├── poo_demo_comparative.ipynb
│   ├── scraping_demo.ipynb
│   └── modelisation_demo.ipynb
└── src/
    ├── extract_api.py         # extraction API TMDB (version fonctionnelle)
    ├── extract_api_oop.py     # extraction API TMDB (version orientée objet, optionnelle)
    ├── scraping_wikipedia.py  # scraping Wikipedia / AlloCiné
    ├── db.py                  # création et alimentation de la base SQLite
    ├── aggregate.py           # agrégation des 3 sources (TMDB + scraping + MovieLens)
    └── api.py                 # API REST (à venir)
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

Les scripts s'exécutent dans cet ordre, chacun produisant ce dont le suivant a besoin :

```bash
python src/extract_api.py          # -> data/raw/films_tmdb.json
python src/scraping_wikipedia.py   # -> data/raw/film_scraping.json
python src/aggregate.py            # crée data/cinedata.db et l'alimente à partir des 3 sources
```

## État d'avancement

- [x] Extraction API TMDB
- [x] Scraping Wikipedia / AlloCiné
- [ ] Modélisation et création de la base SQLite
- [ ] Script d'agrégation multi-sources
- [ ] API REST (FastAPI)
- [ ] Note technique de fin de projet

## Notes techniques

- Base de données : SQLite (fichier local, pas de serveur à configurer)
- Aucune donnée personnelle identifiante collectée
- Clé API TMDB gérée via variable d'environnement (`.env`, non versionné)

---

*Auteur : RémiJ — Projet réalisé dans le cadre de la formation Développeur d'application IA.*