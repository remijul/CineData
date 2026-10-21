"""
enrichir_affiches.py
Script de reprise : ajoute le champ `poster_path` (chemin relatif de l'affiche
TMDB) aux films DÉJÀ extraits, sans relancer toute l'extraction.

Pourquoi un script de reprise plutôt que relancer extract_api_tmdb.py ?
La liste « films populaires » de TMDB évolue chaque jour : relancer
l'extraction complète changerait l'ensemble des films. Or les données
MovieLens et Wikipédia ont été collectées pour les films d'origine, et
seraient désynchronisées. Ici on garde exactement les mêmes films et on
complète chacun avec un appel à /movie/{id}.

Le script est relançable : un film qui a déjà son champ `poster_path` est
ignoré (utile si l'exécution est interrompue ou si un appel a échoué).

Après ce script, rejouer la suite du pipeline :
    python src/transform.py
    (supprimer data/cinedata.db)
    python src/load.py
    python src/precompute_recommandation.py

Les constantes (URL, langue, pause, fichier de sortie) viennent de
extract_api_tmdb.py, donc de config.yaml : pas de valeur dupliquée.
"""

import json
import os
import shutil
import time

from extract_api_tmdb import (
    API_KEY,
    BASE_URL,
    LANGUE,
    PAUSE,
    DOSSIER_SORTIE,
    FICHIER_SORTIE,
    appeler_api,
)


def charger_json(chemin_fichier):
    """Charge un fichier JSON et retourne son contenu."""
    with open(chemin_fichier, "r", encoding="utf-8") as fichier:
        return json.load(fichier)


def sauvegarder_json(donnees, chemin_fichier):
    """Sauvegarde une structure Python en fichier JSON lisible."""
    with open(chemin_fichier, "w", encoding="utf-8") as fichier:
        json.dump(donnees, fichier, ensure_ascii=False, indent=2)


def ajouter_affiche(film):
    """
    Ajoute `poster_path` à un film grâce à /movie/{id}.
    Retourne True si le champ a été renseigné (même à None : TMDB n'a pas
    d'affiche pour ce film), False si l'appel a échoué.
    """
    donnees = appeler_api(f"{BASE_URL}/movie/{film['id']}", params={"language": LANGUE})
    if donnees is None:
        return False
    film["poster_path"] = donnees.get("poster_path")
    return True


def enrichir_films(films):
    """
    Complète chaque film qui n'a pas encore le champ `poster_path`.
    Retourne le nombre de films traités et la liste des identifiants en échec.
    """
    a_traiter = [film for film in films if "poster_path" not in film]
    echecs = []

    for index, film in enumerate(a_traiter, start=1):
        if not ajouter_affiche(film):
            echecs.append(film["id"])

        if index % 50 == 0 or index == len(a_traiter):
            print(f"{index}/{len(a_traiter)} films traités.")

        time.sleep(PAUSE)

    return len(a_traiter), echecs


if __name__ == "__main__":
    if not API_KEY:
        raise SystemExit(
            "Clé API manquante. Vérifiez que TMDB_API_KEY est bien définie dans votre fichier .env"
        )

    chemin = os.path.join(DOSSIER_SORTIE, FICHIER_SORTIE)
    films = charger_json(chemin)
    print(f"{len(films)} film(s) chargé(s) depuis {chemin}.")

    # Copie de sécurité avant de modifier le fichier brut
    shutil.copy(chemin, chemin + ".bak")

    nb_traites, echecs = enrichir_films(films)
    sauvegarder_json(films, chemin)

    nb_avec_affiche = sum(1 for film in films if film.get("poster_path"))
    print(f"{nb_traites} film(s) enrichi(s) ; {nb_avec_affiche}/{len(films)} avec une affiche.")
    if echecs:
        print(f"{len(echecs)} échec(s) (relancer le script pour réessayer) : {echecs}")