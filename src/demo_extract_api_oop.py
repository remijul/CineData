"""
extract_api_oop.py
Extraction de données films depuis l'API TMDB — version orientée objet.

Version OPTIONNELLE / BONUS : reprend exactement la même logique que
src/extract_api.py, réorganisée en classe. Comparez les deux fichiers
côte à côte pour voir ce que la POO change concrètement.
"""

import os
import time
import json
import requests
from dotenv import load_dotenv


class TMDBExtractor:
    """
    Encapsule l'accès à l'API TMDB : une instance = une configuration
    (clé API + langue) qui reste disponible pour tous les appels suivants,
    sans avoir à la repasser en paramètre à chaque fonction.
    """

    BASE_URL = "https://api.themoviedb.org/3"

    def __init__(self, api_key, langue="fr-FR"):
        self.api_key = api_key
        self.langue = langue
        self._genres_mapping = None  # sera rempli au premier appel, puis mis en cache

    def _params(self, extra=None):
        """Construit les paramètres de requête communs à tous les appels."""
        params = {"api_key": self.api_key, "language": self.langue}
        if extra:
            params.update(extra)
        return params

    def get_popular_movies(self, page=1):
        """Récupère une page de films populaires. Retourne une liste de dicts."""
        url = f"{self.BASE_URL}/movie/popular"

        try:
            response = requests.get(url, params=self._params({"page": page}), timeout=10)
            response.raise_for_status()
        except requests.exceptions.RequestException as erreur:
            print(f"Erreur lors de la récupération des films populaires : {erreur}")
            return []

        return response.json().get("results", [])

    def get_movie_details(self, movie_id):
        """Récupère le détail complet d'un film. Retourne un dict ou None."""
        url = f"{self.BASE_URL}/movie/{movie_id}"

        try:
            response = requests.get(url, params=self._params(), timeout=10)
            response.raise_for_status()
        except requests.exceptions.RequestException as erreur:
            print(f"Erreur lors de la récupération du film {movie_id} : {erreur}")
            return None

        return response.json()

    def get_genre_mapping(self):
        """
        Récupère la correspondance id -> nom de genre, avec mise en cache :
        l'appel réseau n'est fait qu'une seule fois par instance, même si
        cette méthode est appelée plusieurs fois. C'est un des bénéfices
        concrets de garder un état (self._genres_mapping) dans l'objet.
        """
        if self._genres_mapping is not None:
            return self._genres_mapping

        url = f"{self.BASE_URL}/genre/movie/list"

        try:
            response = requests.get(url, params=self._params(), timeout=10)
            response.raise_for_status()
        except requests.exceptions.RequestException as erreur:
            print(f"Erreur lors de la récupération des genres : {erreur}")
            return {}

        genres = response.json().get("genres", [])
        self._genres_mapping = {genre["id"]: genre["name"] for genre in genres}
        return self._genres_mapping

    def get_movie_credits(self, movie_id, nb_acteurs=5):
        """Récupère les principaux acteurs d'un film (bonus, cf. atelier API)."""
        url = f"{self.BASE_URL}/movie/{movie_id}/credits"

        try:
            response = requests.get(url, params=self._params(), timeout=10)
            response.raise_for_status()
        except requests.exceptions.RequestException as erreur:
            print(f"Erreur lors de la récupération du casting du film {movie_id} : {erreur}")
            return []

        cast_brut = response.json().get("cast", [])
        cast_trie = sorted(cast_brut, key=lambda acteur: acteur.get("order", 999))
        return [
            {"nom": acteur.get("name"), "role": acteur.get("character")}
            for acteur in cast_trie[:nb_acteurs]
        ]

    def extraire_champs_utiles(self, film):
        """Simplifie un film TMDB brut en gardant les champs utiles au projet."""
        genres_mapping = self.get_genre_mapping()
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

    def extraire_et_simplifier_populaires(self, page=1):
        """Enchaîne récupération + simplification pour une page de films populaires."""
        films_bruts = self.get_popular_movies(page=page)
        return [self.extraire_champs_utiles(film) for film in films_bruts]

    @staticmethod
    def sauvegarder_json(donnees, chemin_fichier):
        """Sauvegarde une structure Python en fichier JSON lisible."""
        with open(chemin_fichier, "w", encoding="utf-8") as fichier:
            json.dump(donnees, fichier, ensure_ascii=False, indent=2)
        print(f"{len(donnees)} film(s) sauvegardé(s) dans {chemin_fichier}")


# --- Programme principal ---

if __name__ == "__main__":
    load_dotenv()
    api_key = os.getenv("TMDB_API_KEY")

    if not api_key:
        raise SystemExit(
            "Clé API manquante. Vérifiez que TMDB_API_KEY est bien définie dans votre fichier .env"
        )

    extractor = TMDBExtractor(api_key)

    print("Récupération et simplification des films populaires (page 1)...")
    films = extractor.extraire_et_simplifier_populaires(page=1)

    print(f"{len(films)} films récupérés.")
    for film in films[:5]:
        print(f"- {film['titre']} ({film['date_sortie']}) — {film['genres']}")

    time.sleep(0.25)
    TMDBExtractor.sauvegarder_json(films, "data/raw/films_tmdb_oop.json")
