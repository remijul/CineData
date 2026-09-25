-- schema.sql
-- Schéma de la base de données CinéData (version SQLite)
-- 6 tables : films (fusion TMDB + Wikipedia + agrégats MovieLens),
-- genres/film_genre (N-N), personnes/film_personne (N-N avec attributs
-- role + personnage portés par la relation), film_tag (MovieLens).

CREATE TABLE IF NOT EXISTS films (
    id                      INTEGER PRIMARY KEY,   -- identifiant TMDB
    title                   TEXT NOT NULL,
    original_title          TEXT,
    original_language       TEXT,
    release_date            TEXT,
    popularity               REAL,
    vote_average             REAL,
    vote_count                INTEGER,
    adult                     INTEGER,              -- 0/1
    overview                  TEXT,

    -- Phase 2 TMDB
    budget                    INTEGER,
    homepage                  TEXT,
    revenue                   INTEGER,
    runtime                   INTEGER,
    status                    TEXT,
    tagline                   TEXT,

    -- Enrichissement Wikipedia
    resume_wikipedia           TEXT,
    url_wikipedia               TEXT,
    musique                     TEXT,   -- infobox "Music by"
    societes_production          TEXT,  -- infobox "Production companies"

    -- Agrégats MovieLens (relation 1-1 : une valeur par film, pas de table à part)
    note_moyenne_movielens        REAL,
    nombre_avis_movielens         INTEGER
);

CREATE TABLE IF NOT EXISTS genres (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    nom     TEXT UNIQUE NOT NULL
);

-- Association N-N : un film a plusieurs genres, un genre concerne plusieurs films.
CREATE TABLE IF NOT EXISTS film_genre (
    film_id     INTEGER NOT NULL REFERENCES films(id),
    genre_id    INTEGER NOT NULL REFERENCES genres(id),
    PRIMARY KEY (film_id, genre_id)
);

-- Une personne = un identifiant TMDB, réalisateur ou acteur confondus
-- (la distinction se fait au niveau de la relation, pas de la personne).
CREATE TABLE IF NOT EXISTS personnes (
    id              INTEGER PRIMARY KEY,   -- identifiant TMDB de la personne
    name            TEXT NOT NULL,
    original_name   TEXT,
    popularity      REAL
);

-- Association N-N avec attributs portés par la relation :
-- `role` (Réalisateur / Acteur) et `personnage` (nom du rôle joué, acteurs
-- uniquement) ne décrivent ni le film seul ni la personne seule, mais
-- CETTE apparition précise d'une personne dans CE film.
CREATE TABLE IF NOT EXISTS film_personne (
    film_id      INTEGER NOT NULL REFERENCES films(id),
    personne_id  INTEGER NOT NULL REFERENCES personnes(id),
    role         TEXT NOT NULL,   -- "Réalisateur" ou "Acteur"
    personnage   TEXT,            -- nom du personnage (NULL pour un réalisateur)
    PRIMARY KEY (film_id, personne_id, role)
);

-- Tags libres MovieLens : la seule table dédiée à la valeur "folksonomie"
-- de cette source (texte libre, pas de dictionnaire de référence comme
-- pour les genres).
CREATE TABLE IF NOT EXISTS film_tag (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    film_id  INTEGER NOT NULL REFERENCES films(id),
    tag      TEXT NOT NULL
);