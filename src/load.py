"""
load.py
Étape "Load" du pipeline ETL CinéData.

Charge le fichier JSON déjà transformé (transform.py) et l'insère dans la
base SQLite. Ne contient aucune logique de fusion/nettoyage — uniquement
de l'écriture, à partir de données déjà prêtes.

Entrée :
    data/transformed/films_transformes.json

Sortie :
    data/cinedata.db (tables films / genres / film_genre / personnes /
    film_personne / film_tag)

Approche : programmation fonctionnelle simple.
"""

import os
import json
import yaml

from db import (
    creer_connexion,
    creer_tables,
    inserer_film,
    associer_film_genre,
    associer_film_personne,
    inserer_tag,
)


def charger_config(chemin="config.yaml"):
    """Charge le fichier de configuration du projet."""
    with open(chemin, "r", encoding="utf-8") as fichier:
        return yaml.safe_load(fichier)


CONFIG = charger_config()

DOSSIER_TRANSFORME = CONFIG["dossiers"]["data_transformee"]
CHEMIN_FILMS_TRANSFORMES = os.path.join(DOSSIER_TRANSFORME, CONFIG["fichiers_sortie"]["films_transformes"])


def charger_json(chemin_fichier):
    """Charge un fichier JSON et retourne son contenu."""
    with open(chemin_fichier, "r", encoding="utf-8") as fichier:
        return json.load(fichier)


def charger_film_en_base(connexion, film):
    """
    Insère un film déjà transformé et ses données associées (genres,
    équipe, tags) dans la base. Pure écriture, aucune transformation.
    """
    film_id = film["id"]

    inserer_film(connexion, film)

    for nom_genre in film.get("genres", []):
        associer_film_genre(connexion, film_id, nom_genre)

    for personne in film.get("equipe", []):
        associer_film_personne(connexion, film_id, personne)

    for tag in film.get("tags", []):
        inserer_tag(connexion, film_id, tag)


# --- Programme principal ---

if __name__ == "__main__":
    films_transformes = charger_json(CHEMIN_FILMS_TRANSFORMES)
    print(f"{len(films_transformes)} film(s) transformé(s) à charger en base.")

    connexion = creer_connexion()
    creer_tables(connexion)

    for film in films_transformes:
        charger_film_en_base(connexion, film)

    connexion.commit()
    connexion.close()

    print(f"{len(films_transformes)} film(s) chargé(s) en base avec succès.")