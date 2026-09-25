"""
extract_api.py
Extraction de données films depuis l'API TMDB (The Movie Database).

Approche : programmation fonctionnelle simple.
Pas de classes ici : chaque fonction fait une chose précise, et le bloc
principal (en bas du fichier) les enchaîne. C'est cette version qui servira
de point de départ ; l'atelier POO proposera une évolution optionnelle
vers une version orientée objet.
"""

import os
import time
import json
import requests
from dotenv import load_dotenv

# --- Configuration ---

load_dotenv()  # charge les variables définies dans le fichier .env

API_KEY = os.getenv("TMDB_API_KEY")
BASE_URL = "https://api.themoviedb.org/3"
LANGUE = "fr-FR"


def get_popular_movies(page=1):
    """
    Récupère une page de films populaires depuis TMDB.

    Paramètres :
        page (int) : numéro de page (l'API en renvoie 20 films par page)

    Retourne :
        list[dict] : liste de films bruts (format TMDB), ou liste vide en cas d'erreur
    """
    url = f"{BASE_URL}/movie/popular"
    params = {
        "api_key": API_KEY,
        "language": LANGUE,
        "page": page,
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()  # lève une exception si le code HTTP est >= 400
    except requests.exceptions.RequestException as erreur:
        print(f"Erreur lors de la récupération des films populaires : {erreur}")
        return []

    donnees = response.json()
    return donnees.get("results", [])


def get_movie_details(movie_id):
    """
    Récupère le détail complet d'un film à partir de son identifiant TMDB.

    Paramètres :
        movie_id (int) : identifiant TMDB du film

    Retourne :
        dict | None : détail du film, ou None en cas d'erreur
    """
    url = f"{BASE_URL}/movie/{movie_id}"
    params = {
        "api_key": API_KEY,
        "language": LANGUE,
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as erreur:
        print(f"Erreur lors de la récupération du film {movie_id} : {erreur}")
        return None

    return response.json()


def get_genre_mapping():
    """
    Récupère la correspondance identifiant -> nom de genre (ex. 28 -> "Action").

    Utile car l'endpoint 'popular' ne renvoie que des identifiants de genres
    (genre_ids), pas leurs noms.

    Retourne :
        dict[int, str] : correspondance id -> nom de genre
    """
    url = f"{BASE_URL}/genre/movie/list"
    params = {
        "api_key": API_KEY,
        "language": LANGUE,
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as erreur:
        print(f"Erreur lors de la récupération des genres : {erreur}")
        return {}

    genres = response.json().get("genres", [])
    return {genre["id"]: genre["name"] for genre in genres}


def extraire_champs_utiles(film, genres_mapping):
    """
    Simplifie un film TMDB brut en ne gardant que les champs utiles au projet.
    À adapter/enrichir selon vos besoins (ex. langue originale, popularité...).

    Paramètres :
        film (dict) : film brut au format TMDB
        genres_mapping (dict) : correspondance id -> nom de genre

    Retourne :
        dict : film simplifié
    """
    genres_noms = [genres_mapping.get(gid, "Inconnu") for gid in film.get("genre_ids", [])]

    return {
        "id": film.get("id"),
        "titre": film.get("title"),
        "date_sortie": film.get("release_date"),
        "note_moyenne": film.get("vote_average"),
        "nombre_votes": film.get("vote_count"),
        "genres": genres_noms,
        "synopsis": film.get("overview"),
    }


def sauvegarder_json(donnees, chemin_fichier):
    """Sauvegarde une structure Python (liste ou dict) en fichier JSON lisible."""
    with open(chemin_fichier, "w", encoding="utf-8") as fichier:
        json.dump(donnees, fichier, ensure_ascii=False, indent=2)
    print(f"{len(donnees)} film(s) sauvegardé(s) dans {chemin_fichier}")


# --- Programme principal ---

if __name__ == "__main__":

    if not API_KEY:
        raise SystemExit(
            "Clé API manquante. Vérifiez que TMDB_API_KEY est bien définie dans votre fichier .env"
        )

    print("Récupération de la correspondance des genres...")
    genres_mapping = get_genre_mapping()

    print("Récupération des films populaires (page 1)...")
    films_bruts = get_popular_movies(page=1)

    films_simplifies = [
        extraire_champs_utiles(film, genres_mapping) for film in films_bruts
    ]

    print(f"{len(films_simplifies)} films récupérés.")
    for film in films_simplifies[:5]:
        print(f"Les 5ers films récupérés :")
        print(f"- {film['titre']} ({film['date_sortie']}) — {film['genres']}")

    # Petite pause de politesse avant un éventuel enchaînement d'appels
    time.sleep(0.25)

    sauvegarder_json(films_simplifies, "data/raw/films_tmdb.json")
