"""
transform.py
Étape "Transform" du pipeline ETL CinéData.

Charge les 3 sorties brutes des scripts extract_*.py, fusionne les
enrichissements MovieLens et Wikipedia dans chaque film TMDB, normalise
le champ `genres` (chaîne -> liste), et écrit le résultat dans un fichier
JSON intermédiaire — indépendant de toute logique de base de données.

Entrées :
    data/raw/tmdb_full.json
    data/raw/movielens_avis.json
    data/raw/wikipedia_scraping.json

Sortie :
    data/transformed/films_transformes.json

Approche : programmation fonctionnelle simple.
"""

import os
import json
import yaml


def charger_config(chemin="config.yaml"):
    """Charge le fichier de configuration du projet."""
    with open(chemin, "r", encoding="utf-8") as fichier:
        return yaml.safe_load(fichier)


CONFIG = charger_config()

DOSSIER_BRUT = CONFIG["dossiers"]["data_brute"]
DOSSIER_TRANSFORME = CONFIG["dossiers"]["data_transformee"]

CHEMIN_TMDB = os.path.join(DOSSIER_BRUT, CONFIG["fichiers_sortie"]["tmdb_full"])
CHEMIN_MOVIELENS = os.path.join(DOSSIER_BRUT, CONFIG["fichiers_sortie"]["movielens_avis"])
CHEMIN_WIKIPEDIA = os.path.join(DOSSIER_BRUT, CONFIG["fichiers_sortie"]["wikipedia_scraping"])
CHEMIN_SORTIE = os.path.join(DOSSIER_TRANSFORME, CONFIG["fichiers_sortie"]["films_transformes"])


def charger_json(chemin_fichier):
    """Charge un fichier JSON et retourne son contenu."""
    with open(chemin_fichier, "r", encoding="utf-8") as fichier:
        return json.load(fichier)


# --- Fusion des enrichissements ---

def fusionner_wikipedia(film, entree_wikipedia):
    """
    Enrichit un film avec les données Wikipedia : résumé, url, et deux
    champs d'infobox absents de TMDB (musique, sociétés de production).
    N'écrase jamais un champ déjà présent depuis TMDB (budget/runtime
    restent ceux de TMDB, pas de doublon de source).
    """
    if entree_wikipedia is None or entree_wikipedia.get("url_wikipedia") is None:
        return film

    infobox = entree_wikipedia.get("infobox", {})

    film["resume_wikipedia"] = entree_wikipedia.get("resume")
    film["url_wikipedia"] = entree_wikipedia.get("url_wikipedia")
    film["musique"] = infobox.get("Music by")
    film["societes_production"] = infobox.get("Production companies")

    return film


def fusionner_movielens(film, entree_movielens):
    """Enrichit un film avec les agrégats MovieLens (note moyenne, nb d'avis, tags)."""
    if entree_movielens is None:
        film["note_moyenne_movielens"] = None
        film["nombre_avis_movielens"] = 0
        film["tags"] = []
        return film

    film["note_moyenne_movielens"] = entree_movielens.get("note_moyenne_movielens")
    film["nombre_avis_movielens"] = entree_movielens.get("nombre_avis_movielens", 0)
    film["tags"] = entree_movielens.get("tags", [])
    return film


def normaliser_genres(film):
    """
    Transforme le champ `genres` de chaîne concaténée ("Action, Adventure")
    en liste (["Action", "Adventure"]) — plus directement exploitable par
    l'étape Load, qui n'a plus besoin de reparser une chaîne.
    """
    genres_brut = film.get("genres", "")
    film["genres"] = [genre.strip() for genre in genres_brut.split(",") if genre.strip()]
    return film


def transformer_film(film, movielens_par_id, wikipedia_par_id):
    """Applique toutes les transformations à un seul film."""
    film_id = film["id"]
    film = normaliser_genres(film)
    film = fusionner_movielens(film, movielens_par_id.get(film_id))
    film = fusionner_wikipedia(film, wikipedia_par_id.get(film_id))
    return film


def transformer_films(films_tmdb, movielens_par_id, wikipedia_par_id):
    """Applique la transformation à l'ensemble des films."""
    return [transformer_film(film, movielens_par_id, wikipedia_par_id) for film in films_tmdb]


def sauvegarder_json(donnees, chemin_fichier):
    """Sauvegarde une structure Python en fichier JSON lisible."""
    os.makedirs(os.path.dirname(chemin_fichier), exist_ok=True)
    with open(chemin_fichier, "w", encoding="utf-8") as fichier:
        json.dump(donnees, fichier, ensure_ascii=False, indent=2)
    print(f"Données transformées sauvegardées dans {chemin_fichier}")


# --- Programme principal ---

if __name__ == "__main__":
    films_tmdb = charger_json(CHEMIN_TMDB)
    print(f"{len(films_tmdb)} film(s) chargé(s) depuis tmdb_full.json.")

    movielens_par_id = {entree["tmdb_id"]: entree for entree in charger_json(CHEMIN_MOVIELENS)}
    wikipedia_par_id = {entree["tmdb_id"]: entree for entree in charger_json(CHEMIN_WIKIPEDIA)}

    films_transformes = transformer_films(films_tmdb, movielens_par_id, wikipedia_par_id)

    nb_avec_musique = sum(1 for film in films_transformes if film.get("musique"))
    nb_avec_production = sum(1 for film in films_transformes if film.get("societes_production"))
    nb_avec_avis = sum(1 for film in films_transformes if film.get("nombre_avis_movielens", 0) > 0)

    print(f"{nb_avec_avis} film(s) avec au moins un avis MovieLens.")
    print(f"{nb_avec_musique} film(s) avec un champ 'musique' renseigné (Wikipedia).")
    print(f"{nb_avec_production} film(s) avec un champ 'societes_production' renseigné (Wikipedia).")

    sauvegarder_json(films_transformes, CHEMIN_SORTIE)