"""
routers/movies.py
Endpoints films : liste paginée et détail par identifiant.
"""

import math

from fastapi import APIRouter, HTTPException, Query

from schemas import FilmResume, MoviesListResponse, PaginationMeta, FilmDetail, MembreEquipe
from database import executer_fichier_sql

router = APIRouter(tags=["Films"])

PAR_PAGE = 10


@router.get("/movie/", response_model=MoviesListResponse, summary="Liste paginée des films")
def liste_films(page: int = Query(1, ge=1, description="Numéro de page, à partir de 1")):
    """
    Retourne les films par pages de 10 (id, titre, année de sortie).
    """
    offset = (page - 1) * PAR_PAGE

    resultats = executer_fichier_sql("movies_list.sql", (PAR_PAGE, offset))
    total = executer_fichier_sql("movies_count.sql")[0]["total"]
    total_pages = math.ceil(total / PAR_PAGE) if total else 0

    return MoviesListResponse(
        pagination=PaginationMeta(page=page, par_page=PAR_PAGE, total=total, total_pages=total_pages),
        resultats=[FilmResume(**ligne) for ligne in resultats],
    )


@router.get("/movie/{film_id}", response_model=FilmDetail, summary="Détail d'un film")
def detail_film(film_id: int):
    """
    Retourne toutes les informations disponibles pour un film : ses champs
    de base, ses genres, son équipe (réalisateur(s)/acteurs) et ses tags.
    """
    films = executer_fichier_sql("movie_detail.sql", (film_id,))
    if not films:
        raise HTTPException(status_code=404, detail=f"Film {film_id} non trouvé")

    film = films[0]
    genres = [ligne["nom"] for ligne in executer_fichier_sql("movie_genres.sql", (film_id,))]
    equipe = [MembreEquipe(**ligne) for ligne in executer_fichier_sql("movie_equipe.sql", (film_id,))]
    tags = [ligne["tag"] for ligne in executer_fichier_sql("movie_tags.sql", (film_id,))]

    return FilmDetail(**film, genres=genres, equipe=equipe, tags=tags)