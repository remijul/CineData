"""
routers/recommendation.py
Endpoints de recommandation :
- /recommendation/{film_id}           : similarité de contenu (genres, tags,
  casting, tagline), calculée hors ligne par src/precompute_recommandation.py
- /enhanced_recommendation/{film_id}  : mêmes films, accompagnés d'un
  argumentaire rédigé par un LLM (assistant_llm.py)
"""

from fastapi import APIRouter, HTTPException

from schemas import FilmRecommande, RecommandationEnrichie
from moteur_recommandation import recommander, METADATA, INDEX_PAR_ID
from assistant_llm import generer_argumentaire, ErreurLLM

router = APIRouter(tags=["Recommandation"])


@router.get(
    "/recommendation/{film_id}",
    response_model=list[FilmRecommande],
    summary="Films recommandés à partir d'un film",
)
def recommendation(film_id: int):
    """
    Retourne les films les plus proches d'un film donné (similarité de
    contenu), avec titre, genres, durée, date de sortie, acteurs et
    réalisateurs.
    """
    resultats = recommander(film_id)

    if resultats is None:
        raise HTTPException(status_code=404, detail=f"Film {film_id} non trouvé")

    return resultats


@router.get(
    "/enhanced_recommendation/{film_id}",
    response_model=RecommandationEnrichie,
    summary="Recommandation argumentée par un LLM",
    responses={
        404: {"description": "Film non trouvé"},
        503: {"description": "Service LLM indisponible, saturé ou non configuré"},
    },
)
def enhanced_recommendation(film_id: int):
    """
    Même sélection de films que `/recommendation/{film_id}`, accompagnée
    d'un argumentaire rédigé par un LLM (Mistral) sur le ton d'une critique
    de cinéma.

    Le LLM ne choisit pas les films : il commente ceux retenus par le moteur
    de similarité. La liste structurée est renvoyée avec le texte pour qu'on
    puisse vérifier ce qui lui a été fourni.
    """
    films = recommander(film_id)

    if films is None:
        raise HTTPException(status_code=404, detail=f"Film {film_id} non trouvé")

    titre_source = METADATA.iloc[INDEX_PAR_ID[film_id]]["title"]

    try:
        argumentaire = generer_argumentaire(titre_source, films)
    except ErreurLLM as erreur:
        raise HTTPException(status_code=503, detail=str(erreur))

    return {
        "film_source": titre_source,
        "argumentaire": argumentaire,
        "films_recommandes": films,
    }
