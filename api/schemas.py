"""
schemas.py
Modèles Pydantic de l'API — définissent la forme des données en entrée/sortie
et sont validés automatiquement par FastAPI.

Approche volontairement simple : des classes à plat (attributs typés),
pas d'héritage ni de validateurs personnalisés — cohérent avec une
introduction encore récente à la POO.
"""

from typing import Optional
from pydantic import BaseModel


# --- Système ---

class InfoResponse(BaseModel):
    nom: str
    version: str
    description: str


class HealthResponse(BaseModel):
    status: str


# --- Films ---

class FilmResume(BaseModel):
    """Un film dans la liste paginée movie/."""
    id: int
    title: str
    annee: Optional[str] = None


class PaginationMeta(BaseModel):
    page: int
    par_page: int
    total: int
    total_pages: int


class MoviesListResponse(BaseModel):
    pagination: PaginationMeta
    resultats: list[FilmResume]


class MembreEquipe(BaseModel):
    """Un réalisateur ou un acteur associé à un film."""
    id: int
    name: str
    role: str
    personnage: Optional[str] = None


class FilmDetail(BaseModel):
    """Détail complet d'un film, pour movie/{id}."""
    id: int
    title: str
    original_title: Optional[str] = None
    original_language: Optional[str] = None
    release_date: Optional[str] = None
    popularity: Optional[float] = None
    vote_average: Optional[float] = None
    vote_count: Optional[int] = None
    adult: Optional[bool] = None
    overview: Optional[str] = None
    budget: Optional[int] = None
    homepage: Optional[str] = None
    revenue: Optional[int] = None
    runtime: Optional[int] = None
    status: Optional[str] = None
    tagline: Optional[str] = None
    resume_wikipedia: Optional[str] = None
    url_wikipedia: Optional[str] = None
    musique: Optional[str] = None
    societes_production: Optional[str] = None
    note_moyenne_movielens: Optional[float] = None
    nombre_avis_movielens: Optional[int] = None
    genres: list[str] = []
    equipe: list[MembreEquipe] = []
    tags: list[str] = []


# --- Classements ---

class PersonneClassement(BaseModel):
    id: int
    name: str
    nombre_films: int


class FilmClassementRevenue(BaseModel):
    id: int
    title: str
    revenue: int


class FilmClassementBudget(BaseModel):
    id: int
    title: str
    budget: int