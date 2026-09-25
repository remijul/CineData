"""
db.py
Création et alimentation de la base de données SQLite du projet CinéData.
Schéma Option A : films, genres, film_genre, personnes, film_personne, film_tag.

Approche : programmation fonctionnelle simple, sqlite3 (bibliothèque standard).
"""

import json
import sqlite3

CHEMIN_SCHEMA = "sql/schema.sql"
CHEMIN_DB = "data/cinedata.db"

# known_for_department (TMDB) -> role tel que stocké dans film_personne
ROLES_PAR_DEPARTEMENT = {
    "Directing": "Réalisateur",
    "Acting": "Acteur",
}


def creer_connexion(chemin_db=CHEMIN_DB):
    """Ouvre (ou crée) le fichier de base de données SQLite et retourne la connexion."""
    connexion = sqlite3.connect(chemin_db)
    connexion.execute("PRAGMA foreign_keys = ON")
    return connexion


def creer_tables(connexion, chemin_schema=CHEMIN_SCHEMA):
    """Exécute le script SQL de création des tables (schema.sql)."""
    with open(chemin_schema, "r", encoding="utf-8") as fichier:
        script_sql = fichier.read()
    connexion.executescript(script_sql)
    connexion.commit()
    print("Tables créées (ou déjà existantes).")


def inserer_film(connexion, film):
    """
    Insère (ou met à jour) un film dans la table `films`.

    `film` attendu (dict) : toutes les colonnes de la table sont optionnelles
    sauf id/title ; les clés absentes sont insérées comme NULL.
    """
    colonnes = [
        "id", "title", "original_title", "original_language", "release_date",
        "popularity", "vote_average", "vote_count", "adult", "overview",
        "budget", "homepage", "revenue", "runtime", "status", "tagline",
        "resume_wikipedia", "url_wikipedia", "musique", "societes_production",
        "note_moyenne_movielens", "nombre_avis_movielens",
    ]

    valeurs = {colonne: film.get(colonne) for colonne in colonnes}
    noms_colonnes = ", ".join(colonnes)
    placeholders = ", ".join(f":{colonne}" for colonne in colonnes)
    mise_a_jour = ", ".join(f"{colonne} = excluded.{colonne}" for colonne in colonnes if colonne != "id")

    connexion.execute(
        f"""
        INSERT INTO films ({noms_colonnes})
        VALUES ({placeholders})
        ON CONFLICT(id) DO UPDATE SET {mise_a_jour}
        """,
        valeurs,
    )


def obtenir_ou_creer_genre(connexion, nom_genre):
    """Retourne l'id du genre `nom_genre`, en le créant s'il n'existe pas déjà."""
    connexion.execute("INSERT OR IGNORE INTO genres (nom) VALUES (?)", (nom_genre,))
    curseur = connexion.execute("SELECT id FROM genres WHERE nom = ?", (nom_genre,))
    return curseur.fetchone()[0]


def associer_film_genre(connexion, film_id, nom_genre):
    """Associe un film à un genre (crée le genre si besoin)."""
    genre_id = obtenir_ou_creer_genre(connexion, nom_genre)
    connexion.execute(
        "INSERT OR IGNORE INTO film_genre (film_id, genre_id) VALUES (?, ?)",
        (film_id, genre_id),
    )


def obtenir_ou_creer_personne(connexion, personne):
    """
    Insère (ou met à jour) une personne dans `personnes`, à partir de son
    id TMDB (réutilisé tel quel, pas d'autoincrément).
    """
    connexion.execute(
        """
        INSERT INTO personnes (id, name, original_name, popularity)
        VALUES (:id, :name, :original_name, :popularity)
        ON CONFLICT(id) DO UPDATE SET
            name = excluded.name,
            original_name = excluded.original_name,
            popularity = excluded.popularity
        """,
        {
            "id": personne.get("id"),
            "name": personne.get("name"),
            "original_name": personne.get("original_name"),
            "popularity": personne.get("popularity"),
        },
    )
    return personne.get("id")


def associer_film_personne(connexion, film_id, personne):
    """
    Associe un film à une personne (réalisateur ou acteur), avec le rôle
    et, pour un acteur, le personnage joué.

    `personne` (dict) attendu au format extrait par extract_api_tmdb.py :
    id, known_for_department, name, original_name, popularity, character.
    Les personnes dont known_for_department ne correspond à aucun rôle
    connu (ni "Directing" ni "Acting") sont ignorées.
    """
    role = ROLES_PAR_DEPARTEMENT.get(personne.get("known_for_department"))
    if role is None:
        return

    obtenir_ou_creer_personne(connexion, personne)

    personnage = personne.get("character") if role == "Acteur" else None

    connexion.execute(
        """
        INSERT OR IGNORE INTO film_personne (film_id, personne_id, role, personnage)
        VALUES (?, ?, ?, ?)
        """,
        (film_id, personne.get("id"), role, personnage),
    )


def inserer_tag(connexion, film_id, tag):
    """Ajoute un tag MovieLens pour un film."""
    connexion.execute(
        "INSERT INTO film_tag (film_id, tag) VALUES (?, ?)",
        (film_id, tag),
    )


def charger_json(chemin_fichier):
    """Charge un fichier JSON et retourne son contenu (liste ou dict)."""
    with open(chemin_fichier, "r", encoding="utf-8") as fichier:
        return json.load(fichier)