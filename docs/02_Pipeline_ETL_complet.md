# Pipeline ETL — CinéData

Documentation du process ETL (Extract / Transform / Load) construit pour ce projet.
Les deux diagrammes Mermaid ci-dessous sont réutilisables tels quels dans le README final.
Noms de fichiers et dossiers alignés sur `config.yaml`.

## 1. Vue d'ensemble du pipeline

Trois branches d'extraction indépendantes convergent vers une étape de transformation unique, puis un chargement en base. **La branche API TMDB est la source principale et déclenche les deux autres** : `extract_csv_movielens.py` et `extract_web_wikipedia.py` se basent tous les deux sur la liste des identifiants de films déjà extraits par `extract_api_tmdb.py` (via `tmdb_movies.json`) pour savoir quels films rechercher/enrichir — ils ne traitent jamais l'intégralité de leur source.

```mermaid
flowchart TD
    subgraph EXTRACT["EXTRACT"]
        direction TB
        A1["extract_api_tmdb.py<br/>Déclencheur : GET /movie/popular<br/>(pages 1 à 100)"] --> A2["data/raw/tmdb_movies.json<br/>id, title, release_date, popularity,<br/>vote_average, budget, genres, equipe..."]
        B1["extract_csv_movielens.py<br/>Filtré sur les ids TMDB déjà extraits"] --> B2["data/raw/movielens_avis.json<br/>tmdb_id, note_moyenne_movielens,<br/>nombre_avis_movielens, tags"]
        C1["extract_web_wikipedia.py<br/>Recherche par titre + vérif. année"] --> C2["data/raw/wikipedia_misc.json<br/>tmdb_id, url_wikipedia,<br/>infobox (Music by, Production companies...), resume"]
    end

    A2 -. "ids TMDB à rechercher" .-> B1
    A2 -. "ids TMDB à rechercher" .-> C1

    subgraph TRANSFORM["TRANSFORM — transform.py"]
        direction TB
        D0["Charge les 3 fichiers depuis data/raw/"] --> D1["Pour chaque film (par tmdb_id)"]
        D1 --> D1a["normaliser_genres()<br/>genres : chaîne → liste"]
        D1a --> D1b["fusionner_movielens()<br/>+ note_moyenne_movielens,<br/>nombre_avis_movielens, tags"]
        D1b --> D1c["fusionner_wikipedia()<br/>+ resume_wikipedia, url_wikipedia,<br/>musique, societes_production"]
    end

    A2 --> D0
    B2 --> D0
    C2 --> D0
    D1c --> D2["data/processed/films_transformes.json<br/>fusion complète, par tmdb_id"]

    subgraph LOAD["LOAD — load.py"]
        direction TB
        E0["Charge films_transformes.json"] --> E1["creer_connexion() + creer_tables()<br/>via sql/schema.sql"]
        E1 --> E2["Pour chaque film"]
        E2 --> E2a["inserer_film()"]
        E2a --> E2b["associer_film_genre() ×N"]
        E2b --> E2c["associer_film_personne() ×N<br/>(role, personnage)"]
        E2c --> E2d["inserer_tag() ×N"]
    end

    D2 --> E0
    E2d --> F["data/cinedata.db<br/>films / genres / film_genre /<br/>personnes / film_personne / film_tag"]
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
        P3a --> P3b["filtrer_equipe()<br/>Directing + Acting<br/>(nb_acteurs premiers, config.yaml)"]
        P3b --> P3c["+ equipe: [id, name, character,<br/>known_for_department...]"]
    end

    P2c --> MERGE["dict films complet, indexé par id"]
    P3c --> MERGE
    MERGE --> SAVE["sauvegarder_json()"]
    SAVE --> OUT["data/raw/tmdb_movies.json"]
```

## 3. Schéma de la base de données

```mermaid
erDiagram
    FILMS {
        int id PK
        text title
        text original_title
        text original_language
        text release_date
        real popularity
        real vote_average
        int vote_count
        int adult
        text overview
        int budget
        text homepage
        int revenue
        int runtime
        text status
        text tagline
        text resume_wikipedia
        text url_wikipedia
        text musique
        text societes_production
        real note_moyenne_movielens
        int nombre_avis_movielens
    }

    GENRES {
        int id PK
        text nom
    }

    FILM_GENRE {
        int film_id FK
        int genre_id FK
    }

    PERSONNES {
        int id PK
        text name
        text original_name
        real popularity
    }

    FILM_PERSONNE {
        int film_id FK
        int personne_id FK
        text role
        text personnage
    }

    FILM_TAG {
        int id PK
        int film_id FK
        text tag
    }

    FILMS ||--o{ FILM_GENRE : "a pour genre"
    GENRES ||--o{ FILM_GENRE : "concerne"
    FILMS ||--o{ FILM_PERSONNE : "a pour équipe"
    PERSONNES ||--o{ FILM_PERSONNE : "apparaît dans"
    FILMS ||--o{ FILM_TAG : "est tagué"
```

Points de lecture :
- `note_moyenne_movielens`/`nombre_avis_movielens` restent des colonnes de `films` (relation 1-1, une seule valeur par film) — pas de table dédiée, contrairement aux tags qui sont multi-valués.
- `film_personne` porte `role` et `personnage` : ces deux colonnes décrivent l'apparition précise d'une personne dans un film donné, pas la personne elle-même (une même personne peut apparaître avec des rôles différents selon les films).
- Les `id` de `films` et `personnes` réutilisent directement l'identifiant TMDB — pas d'auto-incrément, puisque déjà uniques et stables.

## Logique générale

- **Déclencheur unique** : `/movie/popular`, seule route qui ne dépend d'aucun identifiant préalable.
- **Cascade par identifiant** : chaque phase/branche suivante consomme les ids produits en amont — jamais de traitement en aveugle d'une source entière (ex. `extract_csv_movielens.py` ne parcourt pas les 100 000 lignes de MovieLens, seulement celles liées à un film déjà extrait de TMDB).
- **`appeler_api()` / `requete_avec_retry()`** : point de passage unique pour tous les appels réseau de chaque script, avec gestion du rate limit (429) et des erreurs — un échec ponctuel n'interrompt jamais tout le pipeline.
- **Transform isolé du Load** : `transform.py` ne connaît rien de la base de données (il lit `data/raw/`, écrit `data/processed/films_transformes.json`) ; `load.py` ne fait aucune fusion (il lit `data/processed/`, écrit `data/cinedata.db`) — chacun a une seule responsabilité, conformément au découpage ETL validé.
- **Fusion en 3 étapes successives par film** (Transform) : normalisation des genres, puis enrichissement MovieLens, puis enrichissement Wikipedia — dans cet ordre, chaque étape ne touchant que les champs qui lui sont propres.
- **Chargement en 4 étapes par film** (Load) : le film lui-même, puis ses genres, puis son équipe (réalisateurs/acteurs avec rôle et personnage), puis ses tags — reflet direct des 6 tables du schéma.