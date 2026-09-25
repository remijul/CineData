"""
extract_api_tmdb.py
Extraction TMDB en 3 phases, branche "API" du pipeline ETL CinéData.

Phase 1 : /movie/popular (pages 1 à page_fin)       -> champs de base
Phase 2 : /movie/{id}                                -> enrichissement (budget, genres...)
Phase 3 : /movie/{id}/credits                        -> réalisateur(s) + 3 premiers acteurs

Résultat : data/raw/tmdb_full.json

Constantes (URLs, timeout, pages, dossiers) centralisées dans config.json,
pour rester cohérent avec les autres branches du pipeline (CSV, scraping).

Approche : programmation fonctionnelle simple.
"""

import os
import json
import time
import requests
import yaml
from dotenv import load_dotenv

load_dotenv()


def charger_config(chemin="config.yaml"):
    """Charge le fichier de configuration du projet."""
    with open(chemin, "r", encoding="utf-8") as fichier:
        return yaml.safe_load(fichier)


CONFIG = charger_config()
API_KEY = os.getenv("TMDB_API_KEY")

BASE_URL = CONFIG["tmdb"]["base_url"]
LANGUE = CONFIG["tmdb"]["language"]
NB_ACTEURS = CONFIG["tmdb"]["nb_acteurs"]
PAGE_DEBUT = CONFIG["tmdb"]["page_debut"]
PAGE_FIN = CONFIG["tmdb"]["page_fin"]
TIMEOUT = CONFIG["tmdb"]["timeout"]
PAUSE = CONFIG["tmdb"]["pause_entre_requetes"]
MAX_TENTATIVES = CONFIG["tmdb"]["max_tentatives"]

DOSSIER_SORTIE = CONFIG["dossiers"]["data_brute"]
FICHIER_SORTIE = CONFIG["fichiers_sortie"]["tmdb_full"]


# --- Appel API générique, avec gestion des erreurs et du rate limit ---

def appeler_api(url, params=None):
    """
    Effectue un appel GET vers l'API TMDB, avec :
    - gestion du rate limit (429) : pause puis nouvelle tentative
    - plusieurs tentatives en cas d'erreur réseau/timeout
    - ajout automatique de la clé API

    Retourne le JSON de la réponse, ou None si l'appel échoue définitivement
    (le film/la page concernée est alors ignorée plutôt que de faire
    planter tout le pipeline).
    """
    params = dict(params or {})
    params["api_key"] = API_KEY

    for tentative in range(1, MAX_TENTATIVES + 1):
        try:
            reponse = requests.get(url, params=params, timeout=TIMEOUT)

            if reponse.status_code == 429:
                attente = int(reponse.headers.get("Retry-After", 2))
                print(f"Rate limit atteint, pause de {attente}s...")
                time.sleep(attente)
                continue

            reponse.raise_for_status()
            return reponse.json()

        except requests.exceptions.RequestException as erreur:
            print(f"Tentative {tentative}/{MAX_TENTATIVES} échouée pour {url} : {erreur}")
            time.sleep(PAUSE * tentative)

    print(f"Abandon après {MAX_TENTATIVES} tentatives : {url}")
    return None


# --- Phase 1 : films populaires ---

def extraire_champs_populaire(film_brut):
    """Ne garde que les champs utiles depuis un film brut de /movie/popular."""
    return {
        "id": film_brut.get("id"),
        "title": film_brut.get("title"),
        "original_title": film_brut.get("original_title"),
        "original_language": film_brut.get("original_language"),
        "release_date": film_brut.get("release_date"),
        "popularity": film_brut.get("popularity"),
        "vote_average": film_brut.get("vote_average"),
        "vote_count": film_brut.get("vote_count"),
        "adult": film_brut.get("adult"),
        "overview": film_brut.get("overview"),
    }


def phase1_films_populaires(page_debut=PAGE_DEBUT, page_fin=PAGE_FIN):
    """
    Parcourt les pages de films populaires et retourne un dict {id: film}.

    Utilise un dict plutôt qu'une liste pour permettre un enrichissement
    direct par identifiant dans les phases suivantes.
    """
    url = f"{BASE_URL}/movie/popular"
    films = {}

    for page in range(page_debut, page_fin + 1):
        donnees = appeler_api(url, params={"language": LANGUE, "page": page})

        if donnees is None:
            print(f"Page {page} ignorée (échec de récupération).")
            continue

        for film_brut in donnees.get("results", []):
            film = extraire_champs_populaire(film_brut)
            if film["id"] is not None:
                films[film["id"]] = film

        if page % 10 == 0 or page == page_fin:
            print(f"Phase 1 - en cours : {page}/{page_fin} pages traitées, {len(films)} films collectés.")

        time.sleep(PAUSE)

    print(f"Phase 1 - terminée : {len(films)} films collectés au total.\n")
    return films


# --- Phase 2 : détails ---

def extraire_champs_details(details_bruts):
    """Ne garde que les champs utiles depuis un détail brut de /movie/{id}."""
    genres = details_bruts.get("genres", [])
    genres_concatenes = ", ".join(genre.get("name", "") for genre in genres if genre.get("name"))

    return {
        "budget": details_bruts.get("budget"),
        "homepage": details_bruts.get("homepage"),
        "genres": genres_concatenes,
        "revenue": details_bruts.get("revenue"),
        "runtime": details_bruts.get("runtime"),
        "status": details_bruts.get("status"),
        "tagline": details_bruts.get("tagline"),
    }


def phase2_details(films):
    """
    Enrichit chaque film du dict `films` avec ses champs de détail.
    Modifie `films` en place (et le retourne, pour un enchaînement lisible).
    """
    total = len(films)

    for index, movie_id in enumerate(list(films.keys()), start=1):
        url = f"{BASE_URL}/movie/{movie_id}"
        donnees = appeler_api(url, params={"language": LANGUE})

        if donnees is None:
            print(f"Détails ignorés pour le film {movie_id} (échec de récupération).")
        else:
            films[movie_id].update(extraire_champs_details(donnees))

        if index % 100 == 0 or index == total:
            print(f"Phase 2 - en cours : {index}/{total} films traités.")

        time.sleep(PAUSE)

    print(f"Phase 2 - terminée : {total} films traités.\n")
    return films


# --- Phase 3 : casting et réalisation ---

def extraire_personne(personne):
    """Ne garde que les champs utiles pour un membre de l'équipe (cast ou crew)."""
    return {
        "id": personne.get("id"),
        "known_for_department": personne.get("known_for_department"),
        "name": personne.get("name"),
        "original_name": personne.get("original_name"),
        "popularity": personne.get("popularity"),
        "character": personne.get("character"),
    }


def filtrer_equipe(credits_bruts):
    """
    Filtre l'équipe d'un film à partir de la réponse brute de /credits :
    - réalisation : personnes de `crew` dont known_for_department == "Directing"
    - casting principal : personnes de `cast` dont known_for_department == "Acting"
      et dont `order` est compris entre 0 et 2 (les 3 premiers rôles crédités)
    """
    equipe = []

    for membre_crew in credits_bruts.get("crew", []):
        if membre_crew.get("job") == "Director":
            equipe.append(extraire_personne(membre_crew))

    for membre_cast in credits_bruts.get("cast", []):
        ordre = membre_cast.get("order")
        if (
            membre_cast.get("known_for_department") == "Acting"
            and ordre is not None
            and 0 <= ordre <= NB_ACTEURS - 1
        ):
            equipe.append(extraire_personne(membre_cast))

    return equipe


def phase3_credits(films):
    """
    Enrichit chaque film du dict `films` avec sa liste `equipe`
    (réalisateur(s) + 3 premiers acteurs crédités).
    """
    total = len(films)

    for index, movie_id in enumerate(list(films.keys()), start=1):
        url = f"{BASE_URL}/movie/{movie_id}/credits"
        donnees = appeler_api(url, params={"language": LANGUE})

        if donnees is None:
            print(f"Casting ignoré pour le film {movie_id} (échec de récupération).")
            films[movie_id]["equipe"] = []
        else:
            films[movie_id]["equipe"] = filtrer_equipe(donnees)

        if index % 100 == 0 or index == total:
            print(f"Phase 3 - en cours : {index}/{total} films traités.")

        time.sleep(PAUSE)

    print(f"Phase 3 - terminée : {total} films traités.\n")
    return films


def sauvegarder_json(donnees, chemin_fichier):
    """Sauvegarde une structure Python en fichier JSON lisible."""
    os.makedirs(os.path.dirname(chemin_fichier), exist_ok=True)
    with open(chemin_fichier, "w", encoding="utf-8") as fichier:
        json.dump(donnees, fichier, ensure_ascii=False, indent=2)
    print(f"Données sauvegardées dans {chemin_fichier}")


# --- Programme principal ---

if __name__ == "__main__":
    if not API_KEY:
        raise SystemExit(
            "Clé API manquante. Vérifiez que TMDB_API_KEY est bien définie dans votre fichier .env"
        )

    print(f"=== Phase 1 : films populaires (pages {PAGE_DEBUT} à {PAGE_FIN}) ===")
    films = phase1_films_populaires()

    print("=== Phase 2 : détails ===")
    films = phase2_details(films)

    print("=== Phase 3 : casting et réalisation ===")
    films = phase3_credits(films)

    chemin_sortie = os.path.join(DOSSIER_SORTIE, FICHIER_SORTIE)
    sauvegarder_json(list(films.values()), chemin_sortie)
