"""
extract_csv_movielens.py
Extraction de la branche "CSV MovieLens" du pipeline ETL CinéData.

Objectif : pour chaque film déjà extrait via extract_api_tmdb.py (tmdb_full.json),
calculer une note moyenne et un nombre d'avis MovieLens, plus les tags libres
associés — sans traiter l'intégralité du fichier MovieLens (100k lignes),
seulement ce qui concerne les films réellement présents dans le projet.

Constantes (dossiers, chemins de fichiers) lues depuis config.yaml.

Résultat : data/raw/movielens_avis.json

Approche : programmation fonctionnelle simple.
"""

import os
import json

import pandas as pd
import yaml


def charger_config(chemin="config.yaml"):
    """Charge le fichier de configuration du projet."""
    with open(chemin, "r", encoding="utf-8") as fichier:
        return yaml.safe_load(fichier)


CONFIG = charger_config()

DOSSIER_MOVIELENS = CONFIG["movielens"]["dossier"]
FICHIERS_MOVIELENS = CONFIG["movielens"]["fichiers"]

DOSSIER_SORTIE = CONFIG["dossiers"]["data_brute"]
FICHIER_TMDB = CONFIG["fichiers_sortie"]["tmdb_full"]
FICHIER_SORTIE = CONFIG["fichiers_sortie"]["movielens_avis"]


# --- Chargement ---

def charger_json(chemin_fichier):
    """Charge un fichier JSON et retourne son contenu."""
    with open(chemin_fichier, "r", encoding="utf-8") as fichier:
        return json.load(fichier)


def charger_ids_tmdb_extraits(chemin_dossier=DOSSIER_SORTIE, nom_fichier=FICHIER_TMDB):
    """
    Récupère l'ensemble des identifiants TMDB déjà extraits (phase API),
    pour ne traiter que les films utiles du fichier MovieLens.
    """
    chemin = os.path.join(chemin_dossier, nom_fichier)
    films_tmdb = charger_json(chemin)
    return {film["id"] for film in films_tmdb if film.get("id") is not None}


def charger_movielens(dossier=DOSSIER_MOVIELENS, fichiers=FICHIERS_MOVIELENS):
    """
    Charge les fichiers MovieLens utiles. `tags.csv` est optionnel : certaines
    versions du dataset ne l'incluent pas, ou l'étudiant peut choisir de ne
    pas l'utiliser — son absence ne doit pas faire planter le script.

    Retourne :
        tuple(DataFrame, DataFrame, DataFrame, DataFrame | None) :
        (movies, ratings, links, tags)
    """
    movies = pd.read_csv(os.path.join(dossier, fichiers["movies"]))
    ratings = pd.read_csv(os.path.join(dossier, fichiers["ratings"]))
    links = pd.read_csv(os.path.join(dossier, fichiers["links"]))

    chemin_tags = os.path.join(dossier, "tags.csv")
    tags = pd.read_csv(chemin_tags) if os.path.exists(chemin_tags) else None
    if tags is None:
        print("tags.csv non trouvé, extraction sans les tags.")

    return movies, ratings, links, tags


# --- Nettoyage / filtrage ---

def construire_mapping_tmdbid_vers_movieid(links):
    """
    Construit la correspondance tmdbId -> movieId à partir de links.csv.

    Entrée corrompue traitée : lignes sans tmdbId renseigné (film non
    référencé sur TMDB) — exclues et comptabilisées.
    """
    links_valides = links.dropna(subset=["tmdbId"])
    nb_supprimees = len(links) - len(links_valides)
    if nb_supprimees:
        print(f"{nb_supprimees} entrée(s) de links.csv sans tmdbId, exclues.")

    return dict(zip(links_valides["tmdbId"].astype(int), links_valides["movieId"].astype(int)))


def filtrer_pour_films_extraits(mapping_tmdbid_vers_movieid, ids_tmdb_extraits):
    """
    Ne garde, dans la correspondance, que les films réellement présents
    dans tmdb_full.json — pas la peine de calculer des statistiques pour
    des films hors du périmètre du projet.

    Retourne :
        dict[int, int] : {tmdbId: movieId}, restreint aux films extraits
    """
    return {
        tmdb_id: movie_id
        for tmdb_id, movie_id in mapping_tmdbid_vers_movieid.items()
        if tmdb_id in ids_tmdb_extraits
    }


def nettoyer_ratings(ratings):
    """Supprime les entrées corrompues : note manquante ou hors échelle (0.5 à 5.0)."""
    avant = len(ratings)

    ratings_propres = ratings.dropna(subset=["rating"])
    ratings_propres = ratings_propres[ratings_propres["rating"].between(0.5, 5.0)]

    nb_supprimees = avant - len(ratings_propres)
    if nb_supprimees:
        print(f"{nb_supprimees} note(s) corrompue(s) (manquante ou hors échelle), exclues.")

    return ratings_propres


# --- Agrégation ---

def calculer_statistiques_avis(ratings, mapping_tmdbid_vers_movieid):
    """
    Calcule, pour chaque film du mapping, la note moyenne et le nombre
    d'avis MovieLens.

    Retourne :
        dict[int, dict] : {tmdbId: {"note_moyenne_movielens": ..., "nombre_avis_movielens": ...}}
    """
    movieids_pertinents = set(mapping_tmdbid_vers_movieid.values())
    ratings_filtres = ratings[ratings["movieId"].isin(movieids_pertinents)]

    statistiques = (
        ratings_filtres.groupby("movieId")["rating"]
        .agg(note_moyenne_movielens="mean", nombre_avis_movielens="count")
        .round({"note_moyenne_movielens": 2})
    )

    movieid_vers_tmdbid = {v: k for k, v in mapping_tmdbid_vers_movieid.items()}

    resultat = {}
    for movie_id, ligne in statistiques.iterrows():
        tmdb_id = movieid_vers_tmdbid.get(movie_id)
        if tmdb_id is not None:
            resultat[tmdb_id] = {
                "note_moyenne_movielens": ligne["note_moyenne_movielens"],
                "nombre_avis_movielens": int(ligne["nombre_avis_movielens"]),
            }

    return resultat


def regrouper_tags(tags, mapping_tmdbid_vers_movieid):
    """
    Regroupe les tags libres par film, dédupliqués et normalisés en minuscules.

    Retourne :
        dict[int, list[str]] : {tmdbId: [tag1, tag2, ...]}, ou {} si tags.csv absent
    """
    if tags is None:
        return {}

    movieids_pertinents = set(mapping_tmdbid_vers_movieid.values())
    tags_filtres = tags[tags["movieId"].isin(movieids_pertinents)].dropna(subset=["tag"])

    movieid_vers_tmdbid = {v: k for k, v in mapping_tmdbid_vers_movieid.items()}

    resultat = {}
    for movie_id, groupe in tags_filtres.groupby("movieId"):
        tmdb_id = movieid_vers_tmdbid.get(movie_id)
        if tmdb_id is not None:
            tags_uniques = sorted({str(tag).strip().lower() for tag in groupe["tag"]})
            resultat[tmdb_id] = tags_uniques

    return resultat


def assembler_resultat(statistiques_avis, tags_par_film, ids_tmdb_cibles):
    """
    Construit la liste finale, une entrée par film ciblé (même les films
    sans avis MovieLens correspondant apparaissent, avec des valeurs nulles
    plutôt que d'être silencieusement absents du résultat).
    """
    resultat = []
    for tmdb_id in sorted(ids_tmdb_cibles):
        stats = statistiques_avis.get(tmdb_id, {"note_moyenne_movielens": None, "nombre_avis_movielens": 0})
        resultat.append(
            {
                "tmdb_id": tmdb_id,
                "note_moyenne_movielens": stats["note_moyenne_movielens"],
                "nombre_avis_movielens": stats["nombre_avis_movielens"],
                "tags": tags_par_film.get(tmdb_id, []),
            }
        )
    return resultat


def sauvegarder_json(donnees, chemin_fichier):
    """Sauvegarde une structure Python en fichier JSON lisible."""
    os.makedirs(os.path.dirname(chemin_fichier), exist_ok=True)
    with open(chemin_fichier, "w", encoding="utf-8") as fichier:
        json.dump(donnees, fichier, ensure_ascii=False, indent=2)
    print(f"Données sauvegardées dans {chemin_fichier}")


# --- Programme principal ---

if __name__ == "__main__":
    ids_tmdb_extraits = charger_ids_tmdb_extraits()
    print(f"{len(ids_tmdb_extraits)} film(s) TMDB déjà extraits, à enrichir.")

    movies_ml, ratings_ml, links_ml, tags_ml = charger_movielens()
    print(f"MovieLens : {len(movies_ml)} films, {len(ratings_ml)} notes au total.")

    mapping_complet = construire_mapping_tmdbid_vers_movieid(links_ml)
    mapping_cible = filtrer_pour_films_extraits(mapping_complet, ids_tmdb_extraits)
    print(f"{len(mapping_cible)} film(s) trouvés à la fois dans TMDB et MovieLens.")

    ratings_propres = nettoyer_ratings(ratings_ml)

    statistiques_avis = calculer_statistiques_avis(ratings_propres, mapping_cible)
    tags_par_film = regrouper_tags(tags_ml, mapping_cible)

    resultat = assembler_resultat(statistiques_avis, tags_par_film, ids_tmdb_extraits)

    nb_avec_avis = sum(1 for film in resultat if film["nombre_avis_movielens"] > 0)
    print(f"{nb_avec_avis}/{len(resultat)} film(s) ont au moins un avis MovieLens.")

    chemin_sortie = os.path.join(DOSSIER_SORTIE, FICHIER_SORTIE)
    sauvegarder_json(resultat, chemin_sortie)
