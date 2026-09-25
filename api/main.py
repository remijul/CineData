"""
main.py
Point d'entrée de l'API CinéData.

Lancement (depuis la racine du projet, sans se déplacer dans api/) :
    uvicorn main:app --reload --app-dir api

Équivalent en se plaçant dans le dossier :
    cd api
    uvicorn main:app --reload

Documentation Swagger : http://127.0.0.1:8000/docs
"""

from fastapi import FastAPI

from routers import system, movies, rankings

TAGS_METADATA = [
    {"name": "Système", "description": "État de l'API et informations générales."},
    {"name": "Films", "description": "Liste et détail des films du catalogue."},
    {"name": "Classements", "description": "Top 10 acteurs, réalisateurs, revenus et budgets."},
]

app = FastAPI(
    title="CinéData API",
    description="API d'exposition des données du projet CinéData (Bloc 1 — Dev IA).",
    version="1.0.0",
    openapi_tags=TAGS_METADATA,
)

app.include_router(system.router)
app.include_router(movies.router)
app.include_router(rankings.router)