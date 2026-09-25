# Pipeline ETL — CinéData

Documentation du process ETL (Extract / Transform / Load) construit pour ce projet.

## 1. Vue d'ensemble du pipeline

Trois branches d'extraction indépendantes convergent vers une étape de transformation unique, puis un chargement en base. **La branche API TMDB est la source principale et déclenche les deux autres** : `extract_csv_movielens.py` et `extract_web_wikipedia.py` se basent tous les deux sur la liste des identifiants de films déjà extraits par `extract_api_tmdb.py` (via `tmdb_full.json`) pour savoir quels films rechercher/enrichir — ils ne traitent jamais l'intégralité de leur source.

```mermaid
flowchart TD
    subgraph EXTRACT["EXTRACT"]
        direction TB
        A1["extract_api_tmdb.py<br/>Déclencheur : GET /movie/popular<br/>(pages 1 à 100)"] --> A2["tmdb_full.json<br/>id, title, release_date, popularity,<br/>vote_average, budget, genres, equipe..."]
        B1["extract_csv_movielens.py<br/>Filtré sur les ids TMDB déjà extraits"] --> B2["movielens_avis.json<br/>tmdb_id, note_moyenne_movielens,<br/>nombre_avis_movielens, tags"]
        C1["extract_web_wikipedia.py<br/>Recherche par titre + vérif. année"] --> C2["wikipedia_scraping.json<br/>tmdb_id, url_wikipedia,<br/>infobox (Music by, Production companies...), resume"]
    end

    A2 -. "ids TMDB à rechercher" .-> B1
    A2 -. "ids TMDB à rechercher" .-> C1

    subgraph TRANSFORM["TRANSFORM"]
        D1["transform.py<br/>normaliser_genres()<br/>fusionner_movielens()<br/>fusionner_wikipedia()"]
    end

    A2 --> D1
    B2 --> D1
    C2 --> D1
    D1 --> D2["films_transformes.json<br/>fusion des 3 sources, par tmdb_id"]

    subgraph LOAD["LOAD"]
        E1["load.py<br/>(via db.py) inserer_film()<br/>associer_film_genre()<br/>associer_film_personne()<br/>inserer_tag()"]
    end

    D2 --> E1
    E1 --> F["cinedata.db<br/>films / genres / film_genre /<br/>personnes / film_personne / film_tag"]
```

## 2. Détail de l'extraction TMDB (3 phases)

Le déclencheur unique de tout le pipeline est l'appel à `/movie/popular`. Les identifiants de films qu'il retourne pilotent ensuite en cascade les deux phases suivantes — aucune autre source de la liste des films n'est utilisée.

```mermaid
flowchart TD
    START(["Déclencheur<br/>GET /movie/popular?page=1..100"]) --> P1

    subgraph PHASE1["Phase 1 — phase1_films_populaires()"]
        P1["Pour chaque page (1 à 100)"] --> P1a["appeler_api()"]
        P1a --> P1b["extraire_champs_populaire()"]
        P1b --> P1c["films id, title, release_date,<br/>popularity, vote_average..."]
    end

    P1c --> IDS(["Ensemble des ids TMDB collectés<br/>jusqu'à 2000 films"])

    IDS --> P2
    IDS --> P3

    subgraph PHASE2["Phase 2 — phase2_details()"]
        P2["Pour chaque id"] --> P2a["GET /movie/id<br/>appeler_api()"]
        P2a --> P2b["extraire_champs_details()"]
        P2b --> P2c["+ budget, genres, revenue,<br/>runtime, status, tagline"]
    end

    subgraph PHASE3["Phase 3 — phase3_credits()"]
        P3["Pour chaque id"] --> P3a["GET /movie/id/credits<br/>appeler_api()"]
        P3a --> P3b["filtrer_equipe()<br/>Directing + Acting (order 0-2)"]
        P3b --> P3c["+ equipe: [id, name, character,<br/>known_for_department...]"]
    end

    P2c --> MERGE["dict films complet, indexé par id"]
    P3c --> MERGE
    MERGE --> SAVE["sauvegarder_json()"]
    SAVE --> OUT["tmdb_full.json"]
```

## Logique générale

- **Déclencheur unique** : `/movie/popular`, seule route qui ne dépend d'aucun identifiant préalable.
- **Cascade par identifiant** : chaque phase/branche suivante consomme les ids produits en amont — jamais de traitement en aveugle d'une source entière (ex. `extract_csv_movielens.py` ne parcourt pas les 100 000 lignes de MovieLens, seulement celles liées à un film déjà extrait de TMDB).
- **`appeler_api()` / `requete_avec_retry()`** : point de passage unique pour tous les appels réseau de chaque script, avec gestion du rate limit (429) et des erreurs — un échec ponctuel n'interrompt jamais tout le pipeline.
- **Transform isolé du Load** : `transform.py` ne connaît rien de la base de données ; `load.py` ne fait aucune fusion — chacun a une seule responsabilité, conformément au découpage ETL validé.