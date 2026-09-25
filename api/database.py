"""
database.py
Accès à la base SQLite pour l'API.

Une seule fonction d'entrée : executer_fichier_sql(). Elle ouvre sa propre
connexion, exécute le fichier .sql demandé (dossier sql/), et la referme —
les routes n'ont jamais à gérer de connexion elles-mêmes. Volontairement
simple (pas de pool de connexions, pas de dépendance FastAPI Depends/yield) :
SQLite supporte très bien une connexion courte par requête, et ça évite
d'ajouter un concept avancé pour un gain minime sur ce projet.
"""

import sqlite3

from config import CHEMIN_DB, CHEMIN_SQL


def executer_fichier_sql(nom_fichier, params=()):
    """
    Exécute le contenu d'un fichier .sql (dans sql/) avec les paramètres
    donnés, et retourne les résultats sous forme de liste de dicts.

    Paramètres :
        nom_fichier (str) : nom du fichier .sql, ex. "movies_list.sql"
        params (tuple) : valeurs pour les "?" du fichier SQL, dans l'ordre

    Retourne :
        list[dict] : une entrée par ligne de résultat
    """
    chemin_fichier = CHEMIN_SQL / nom_fichier
    with open(chemin_fichier, "r", encoding="utf-8") as fichier:
        requete_sql = fichier.read()

    connexion = sqlite3.connect(CHEMIN_DB)
    connexion.row_factory = sqlite3.Row

    try:
        curseur = connexion.execute(requete_sql, params)
        lignes = curseur.fetchall()
        return [dict(ligne) for ligne in lignes]
    finally:
        connexion.close()