"""
moteur_recommandation.py
Charge l'artefact de recommandation pré-calculé (voir
src/precompute_recommandation.py) et expose recommander() pour l'API.

Le calcul (TF-IDF + cosine similarity) n'est PAS refait ici : il est trop
coûteux pour être relancé à chaque requête, voire à chaque démarrage de
l'API. Ce module se contente de charger un fichier déjà calculé et de le
consulter — même logique qu'un modèle ML chargé avec joblib.load() plutôt
que ré-entraîné à chaque appel.
"""

import joblib
import pandas as pd

from config import RACINE_PROJET, CONFIG

CHEMIN_ARTEFACT = RACINE_PROJET / CONFIG["recommandation"]["artefact"]

_artefact = joblib.load(CHEMIN_ARTEFACT)
MATRICE_SIMILARITE = _artefact["matrice_similarite"]
METADATA = _artefact["metadata"]
INDEX_PAR_ID = _artefact["index_par_id"]


def recommander(film_id, top_n=None):
    """
    Retourne les top_n films les plus proches d'un film donné (par id TMDB),
    ou None si le film n'existe pas dans l'artefact (la route traduit ça
    en 404).
    """
    if top_n is None:
        top_n = CONFIG["recommandation"]["top_n"]

    if film_id not in INDEX_PAR_ID:
        return None

    idx = INDEX_PAR_ID[film_id]
    scores = list(enumerate(MATRICE_SIMILARITE[idx]))
    scores = sorted(scores, key=lambda paire: paire[1], reverse=True)
    scores = [(i, s) for i, s in scores if i != idx][:top_n]

    resultats = []
    for i, score in scores:
        film = METADATA.iloc[i]
        # Une valeur manquante lue depuis pandas est un NaN (un float), pas None :
        # `if not x` ne l'attrape pas, il faut pd.isna().
        affiche = film.get("poster_path")
        duree = film["runtime"]
        resultats.append(
            {
                "id": int(film["id"]),
                "title": film["title"],
                "genres": film["genres"],
                "runtime": None if pd.isna(duree) else int(duree),
                "release_date": film["release_date"],
                "poster_path": None if pd.isna(affiche) else affiche,
                "actors": film["actors"],
                "directors": film["directors"],
                "score_similarite": round(float(score), 3),
            }
        )

    return resultats