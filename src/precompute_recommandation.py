"""
precompute_recommandation.py
Calcule et sauvegarde sur disque la matrice de similarité de contenu
(genres + tags + casting + tagline), pour que l'API n'ait jamais à la
recalculer à la volée.

À relancer chaque fois que la base change significativement (nouveaux
films chargés) — même logique qu'un modèle ML qu'on ré-entraîne après
une mise à jour du jeu de données, plutôt que de le recalculer à chaque
requête.

Résultat : data/models/recommandation.joblib (chemin configurable dans
config.yaml, section `recommandation.artefact`).
"""

import os
import sqlite3

import joblib
import pandas as pd
import yaml
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def charger_config(chemin="config.yaml"):
    """Charge le fichier de configuration du projet."""
    with open(chemin, "r", encoding="utf-8") as fichier:
        return yaml.safe_load(fichier)


CONFIG = charger_config()

CHEMIN_DB = CONFIG["database"]["chemin"]
DOSSIER_SQL = os.path.dirname(CONFIG["database"]["schema"])
NOM_FICHIER_SQL = CONFIG["recommandation"]["sql"]
CHEMIN_ARTEFACT = CONFIG["recommandation"]["artefact"]


def charger_donnees():
    """Exécute recommandation_donnees.sql et retourne le résultat en DataFrame."""
    connexion = sqlite3.connect(CHEMIN_DB)
    connexion.row_factory = sqlite3.Row

    with open(os.path.join(DOSSIER_SQL, NOM_FICHIER_SQL), "r", encoding="utf-8") as fichier:
        requete = fichier.read()

    lignes = connexion.execute(requete).fetchall()
    connexion.close()

    return pd.DataFrame([dict(ligne) for ligne in lignes])


def coller_entites(texte):
    """
    Colle les entités multi-mots séparées par '|' en tokens sans espace,
    pour la vectorisation TF-IDF (évite qu'un terme comme "Science Fiction"
    soit découpé en deux tokens séparés).
    """
    if pd.isna(texte) or not texte:
        return ""
    return " ".join(entite.replace(" ", "").lower() for entite in texte.split("|") if entite)


def diviser_en_liste(texte):
    """Transforme une chaîne '|'-séparée en liste Python, pour l'affichage dans l'API."""
    if pd.isna(texte) or not texte:
        return []
    return [entite for entite in texte.split("|") if entite]


def construire_soup(ligne):
    """Concatène genres + tags + casting (acteurs + réalisateur) + tagline."""
    genres = coller_entites(ligne["genres_texte"])
    tags = coller_entites(ligne["tags_texte"])
    casting = coller_entites(ligne["casting_texte"])
    tagline = "" if pd.isna(ligne["tagline"]) else str(ligne["tagline"]).lower()

    return " ".join([genres, tags, casting, tagline]).strip()


def calculer_similarite(df):
    """Vectorise le soup en TF-IDF et retourne la matrice de similarité cosinus."""
    vectorizer = TfidfVectorizer(stop_words="english")
    matrice_tfidf = vectorizer.fit_transform(df["soup"])
    return cosine_similarity(matrice_tfidf)


def construire_metadata(df):
    """Champs à renvoyer par l'API pour chaque film recommandé."""
    metadata = pd.DataFrame(
        {
            "id": df["id"],
            "title": df["title"],
            "genres": df["genres_texte"].apply(diviser_en_liste),
            "runtime": df["runtime"],
            "release_date": df["release_date"],
            "actors": df["actors_texte"].apply(diviser_en_liste),
            "directors": df["directors_texte"].apply(diviser_en_liste),
        }
    )
    return metadata.reset_index(drop=True)


if __name__ == "__main__":
    print("Chargement des données...")
    df = charger_donnees()
    print(f"{len(df)} film(s) chargé(s).")

    df["soup"] = df.apply(construire_soup, axis=1)

    print("Calcul de la matrice de similarité (TF-IDF + cosine similarity)...")
    matrice_similarite = calculer_similarite(df)

    metadata = construire_metadata(df)
    index_par_id = pd.Series(metadata.index, index=metadata["id"])

    artefact = {
        "matrice_similarite": matrice_similarite,
        "metadata": metadata,
        "index_par_id": index_par_id,
    }

    os.makedirs(os.path.dirname(CHEMIN_ARTEFACT), exist_ok=True)
    joblib.dump(artefact, CHEMIN_ARTEFACT)
    print(f"Artefact sauvegardé dans {CHEMIN_ARTEFACT}")