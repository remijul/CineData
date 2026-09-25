"""
routers/system.py
Endpoints système : info et health.
"""

from fastapi import APIRouter

from schemas import InfoResponse, HealthResponse
from database import executer_fichier_sql

router = APIRouter(tags=["Système"])


@router.get("/info", response_model=InfoResponse, summary="Informations sur l'API")
def info():
    """Renvoie le nom, la version et une description de l'API."""
    return InfoResponse(
        nom="CinéData API",
        version="1.0.0",
        description="API d'exposition des données du projet CinéData (films, genres, équipe, classements).",
    )


@router.get("/health", response_model=HealthResponse, summary="État de santé de l'API")
def health():
    """Vérifie que l'API répond et que la base de données est accessible."""
    try:
        executer_fichier_sql("movies_count.sql")
        return HealthResponse(status="ok")
    except Exception:
        return HealthResponse(status="degraded")