"""
filtres_jinja.py
Filtres personnalisés pour les gabarits Jinja2 (mise en forme des valeurs).

Un filtre est une simple fonction : Jinja lui passe la valeur à gauche du
symbole |, et affiche ce qu'elle retourne.

    {{ film.budget | dollars }}      ->  "63 000 000 $"

Convention de ce module : une valeur manquante (None, 0, chaîne vide) donne
une chaîne VIDE. Dans le gabarit, on enchaîne alors avec le filtre standard
default, qui remplace une valeur vide par un texte :

    {{ film.budget | dollars | default("Non renseigné", true) }}
"""

from config import CONFIG

MOIS = [
    "janvier", "février", "mars", "avril", "mai", "juin",
    "juillet", "août", "septembre", "octobre", "novembre", "décembre",
]

# Espace insécable : évite qu'un montant soit coupé en fin de ligne
ESPACE = " "


def dollars(valeur):
    """63000000 -> '63 000 000 $'. Budget et revenus TMDB sont en dollars US."""
    if not valeur:
        return ""
    return f"{int(valeur):,}".replace(",", ESPACE) + f"{ESPACE}$"


def date_fr(valeur):
    """'2002-05-01' -> '1 mai 2002'. Retourne la valeur telle quelle si le format est inattendu."""
    if not valeur:
        return ""
    try:
        annee, mois, jour = str(valeur).split("-")
        return f"{int(jour)} {MOIS[int(mois) - 1]} {annee}"
    except (ValueError, IndexError):
        return str(valeur)


def annee(valeur):
    """'2002-05-01' -> '2002'."""
    return str(valeur)[:4] if valeur else ""


def duree(minutes):
    """121 -> '2 h 01'. 45 -> '45 min'."""
    if not minutes:
        return ""
    minutes = int(minutes)
    if minutes < 60:
        return f"{minutes} min"
    return f"{minutes // 60} h {minutes % 60:02d}"


def url_affiche(chemin_affiche):
    """
    Construit l'URL complète d'une affiche à partir du chemin relatif fourni
    par TMDB (ex. '/abc123.jpg'). Retourne None s'il n'y a pas d'affiche,
    ce qui déclenche le visuel de remplacement dans le gabarit.

    L'adresse de base et la taille viennent de config.yaml (section tmdb) ;
    la base de données ne stocke que le chemin relatif, jamais l'URL complète.
    """
    # isinstance : une valeur manquante venant de pandas est un NaN (un float),
    # qui est « vrai » dans un if ; seule une vraie chaîne non vide est acceptée.
    if not isinstance(chemin_affiche, str) or not chemin_affiche:
        return None
    base = CONFIG["tmdb"].get("image_base_url", "https://image.tmdb.org/t/p/")
    taille = CONFIG["tmdb"].get("taille_affiche", "w342")
    return f"{base}{taille}{chemin_affiche}"


def enregistrer_filtres(environnement):
    """Déclare les filtres auprès de l'environnement Jinja2."""
    environnement.filters["dollars"] = dollars
    environnement.filters["date_fr"] = date_fr
    environnement.filters["annee"] = annee
    environnement.filters["duree"] = duree
    environnement.filters["url_affiche"] = url_affiche