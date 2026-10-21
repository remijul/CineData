"""
routers/pages.py
Pages HTML du site CinéData (gabarits Jinja2).

Ces routes ne sont pas des endpoints d'API : elles renvoient du HTML, pas
du JSON, et n'apparaissent donc pas dans Swagger (include_in_schema=False).

Accès aux données : on réutilise directement les fonctions de l'API
(detail_film, top_revenue...) et les mêmes fichiers .sql — le site et l'API
partagent la même source, il n'y a aucune requête dupliquée.
"""

import math
import os
from datetime import datetime

from fastapi import APIRouter, HTTPException, Request
from fastapi.templating import Jinja2Templates

from config import RACINE_PROJET, CHEMIN_DB
from database import executer_fichier_sql
from filtres_jinja import enregistrer_filtres
from moteur_recommandation import recommander
from assistant_llm import generer_argumentaire, ErreurLLM
from routers.movies import detail_film, PAR_PAGE
from routers.rankings import top_acteurs, top_realisateurs, top_revenue, top_budget
from routers.system import health

router = APIRouter(include_in_schema=False)

# Les gabarits sont à la racine du projet (comme sql/ et data/), chemin calculé
# depuis le projet et non depuis le dossier de lancement.
templates = Jinja2Templates(directory=str(RACINE_PROJET / "templates"))
enregistrer_filtres(templates.env)

# Champs de la page « Qualité des données », regroupés par source :
# (libellé affiché, colonne du résultat de qualite_donnees.sql)
GROUPES_QUALITE = [
    ("TMDB", [
        ("Synopsis", "avec_synopsis"),
        ("Slogan", "avec_slogan"),
        ("Durée", "avec_duree"),
        ("Affiche", "avec_affiche"),
        ("Budget", "avec_budget"),
        ("Revenus", "avec_revenu"),
    ]),
    ("MovieLens", [
        ("Note moyenne", "avec_note_movielens"),
        ("Tags", "avec_tags"),
    ]),
    ("Wikipédia", [
        ("Résumé", "avec_resume_wikipedia"),
        ("Lien de l'article", "avec_url_wikipedia"),
        ("Musique", "avec_musique"),
        ("Sociétés de production", "avec_societes"),
    ]),
]


def page_erreur(request, code, titre, message):
    """Page d'erreur HTML (à la place du JSON {"detail": ...} de l'API)."""
    return templates.TemplateResponse(
        request,
        "erreur.html",
        {"code": code, "titre": titre, "message": message},
        status_code=code,
    )


# --- 1. Accueil ---

@router.get("/", name="accueil")
def accueil(request: Request):
    stats = executer_fichier_sql("stats_accueil.sql")[0]
    top_films = top_revenue()[:5]
    return templates.TemplateResponse(
        request, "accueil.html", {"stats": stats, "top_films": top_films}
    )


# --- 2. Catalogue (recherche, filtre par genre, pagination) ---

@router.get("/catalogue", name="catalogue")
def catalogue(request: Request, q: str = "", genre: str = "", page: int = 1):
    q = q.strip()
    page = max(page, 1)
    filtres = {"q": q, "genre": genre}

    total = executer_fichier_sql("movies_search_count.sql", filtres)[0]["total"]
    total_pages = math.ceil(total / PAR_PAGE) if total else 0

    films = executer_fichier_sql(
        "movies_search.sql",
        {**filtres, "limit": PAR_PAGE, "offset": (page - 1) * PAR_PAGE},
    )
    genres = [ligne["nom"] for ligne in executer_fichier_sql("genres_liste.sql")]

    return templates.TemplateResponse(
        request,
        "catalogue.html",
        {
            "films": films,
            "genres": genres,
            "q": q,
            "genre": genre,
            "page": page,
            "total": total,
            "total_pages": total_pages,
        },
    )


# --- 3. Fiche film (avec 4. films similaires) ---

@router.get("/film/{film_id}", name="fiche_film")
def fiche_film(request: Request, film_id: int):
    try:
        film = detail_film(film_id)
    except HTTPException:
        return page_erreur(request, 404, "Film introuvable", f"Aucun film ne porte l'identifiant {film_id}.")

    realisateurs = [m for m in film.equipe if m.role == "Réalisateur"]
    acteurs = [m for m in film.equipe if m.role == "Acteur"]
    similaires = recommander(film_id) or []

    return templates.TemplateResponse(
        request,
        "film.html",
        {
            "film": film,
            "realisateurs": realisateurs,
            "acteurs": acteurs,
            "similaires": similaires,
        },
    )


# --- 5. Avis du critique (page dédiée : l'appel au LLM prend plusieurs secondes) ---

@router.get("/film/{film_id}/avis", name="avis_film")
def avis_film(request: Request, film_id: int):
    try:
        film = detail_film(film_id)
    except HTTPException:
        return page_erreur(request, 404, "Film introuvable", f"Aucun film ne porte l'identifiant {film_id}.")

    films_recommandes = recommander(film_id)
    if films_recommandes is None:
        return page_erreur(
            request, 503, "Recommandations indisponibles",
            "Ce film n'est pas dans le moteur de recommandation (le précalcul est-il à jour ?).",
        )

    contexte = {"film": film, "films_recommandes": films_recommandes, "argumentaire": None, "erreur": None}
    try:
        contexte["argumentaire"] = generer_argumentaire(film.title, films_recommandes)
        code = 200
    except ErreurLLM as erreur:
        contexte["erreur"] = str(erreur)
        code = 503

    return templates.TemplateResponse(request, "avis.html", contexte, status_code=code)


# --- 6. Classements ---

@router.get("/classements", name="classements")
def classements(request: Request):
    return templates.TemplateResponse(
        request,
        "classements.html",
        {
            "acteurs": top_acteurs(),
            "realisateurs": top_realisateurs(),
            "revenus": top_revenue(),
            "budgets": top_budget(),
        },
    )


# --- 7. Qualité des données ---

@router.get("/qualite-donnees", name="qualite_donnees")
def qualite_donnees(request: Request):
    ligne = executer_fichier_sql("qualite_donnees.sql")[0]
    nb_films = ligne["nb_films"]

    couverture = []
    for source, champs in GROUPES_QUALITE:
        lignes = []
        for libelle, colonne in champs:
            nb = ligne[colonne] or 0
            lignes.append(
                {
                    "champ": libelle,
                    "nb": nb,
                    "pourcentage": round(100 * nb / nb_films) if nb_films else 0,
                }
            )
        couverture.append({"source": source, "lignes": lignes})

    derniere_maj = datetime.fromtimestamp(os.path.getmtime(CHEMIN_DB))

    return templates.TemplateResponse(
        request,
        "qualite_donnees.html",
        {
            "nb_films": nb_films,
            "couverture": couverture,
            "derniere_maj": derniere_maj,
            "etat_api": health().status,
        },
    )