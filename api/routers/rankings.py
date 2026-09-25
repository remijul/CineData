"""
routers/rankings.py
Endpoints de classement : top acteurs, réalisateurs, revenus, budgets.
"""

from fastapi import APIRouter

from schemas import PersonneClassement, FilmClassementRevenue, FilmClassementBudget
from database import executer_fichier_sql

router = APIRouter(tags=["Classements"])


@router.get(
    "/top_actor/",
    response_model=list[PersonneClassement],
    summary="Top 10 des acteurs",
)
def top_acteurs():
    """Top 10 des acteurs par nombre de films dans la base."""
    resultats = executer_fichier_sql("top_actor.sql")
    return [PersonneClassement(**ligne) for ligne in resultats]


@router.get(
    "/top_director/",
    response_model=list[PersonneClassement],
    summary="Top 10 des réalisateurs",
)
def top_realisateurs():
    """Top 10 des réalisateurs par nombre de films dans la base."""
    resultats = executer_fichier_sql("top_director.sql")
    return [PersonneClassement(**ligne) for ligne in resultats]


@router.get(
    "/top_revenue/",
    response_model=list[FilmClassementRevenue],
    summary="Top 10 des films par chiffre d'affaires",
)
def top_revenue():
    """Top 10 des films au chiffre d'affaires le plus élevé (0/NULL exclus)."""
    resultats = executer_fichier_sql("top_revenue.sql")
    return [FilmClassementRevenue(**ligne) for ligne in resultats]


@router.get(
    "/top_budget/",
    response_model=list[FilmClassementBudget],
    summary="Top 10 des films par budget",
)
def top_budget():
    """Top 10 des films au budget le plus élevé (0/NULL exclus)."""
    resultats = executer_fichier_sql("top_budget.sql")
    return [FilmClassementBudget(**ligne) for ligne in resultats]