"""
extract_web_wikipedia.py
Extraction de la branche "Web scraping" du pipeline ETL CinéData.

Pour chaque film déjà extrait via extract_api_tmdb.py (tmdb_full.json) :
1. Recherche de l'article Wikipedia (EN) correspondant, via l'API de
   recherche officielle (pas de scraping d'une page de résultats)
2. Vérification par année : l'article n'est retenu que si l'année de
   sortie trouvée dans son infobox correspond (à tolérance près) à la
   date de sortie TMDB du film — évite de scraper un mauvais article
   (homonyme, remake) plutôt que de scraper "au hasard" le premier résultat
3. Extraction de l'infobox + du résumé de l'article retenu

Résultat : data/raw/wikipedia_scraping.json
Un film sans article trouvé avec confiance suffisante apparaît quand même
dans le résultat, avec url_wikipedia = null — plutôt que d'être absent
silencieusement.

Constantes lues depuis config.yaml.
Approche : programmation fonctionnelle simple.
"""

import os
import re
import json
import time

import requests
from bs4 import BeautifulSoup
import yaml


def charger_config(chemin="config.yaml"):
    """Charge le fichier de configuration du projet."""
    with open(chemin, "r", encoding="utf-8") as fichier:
        return yaml.safe_load(fichier)


CONFIG = charger_config()

API_URL = CONFIG["wikipedia"]["api_url"]
HEADERS = {"User-Agent": CONFIG["wikipedia"]["user_agent"]}
TIMEOUT = CONFIG["wikipedia"]["timeout"]
PAUSE = CONFIG["wikipedia"]["pause_entre_requetes"]
MAX_TENTATIVES = CONFIG["wikipedia"]["max_tentatives"]
MAX_CANDIDATS = CONFIG["wikipedia"]["max_candidats"]
TOLERANCE_ANNEE = CONFIG["wikipedia"]["tolerance_annee"]

DOSSIER_SORTIE = CONFIG["dossiers"]["data_brute"]
FICHIER_TMDB = CONFIG["fichiers_sortie"]["tmdb_full"]
FICHIER_SORTIE = CONFIG["fichiers_sortie"]["wikipedia_scraping"]


# --- Chargement ---

def charger_json(chemin_fichier):
    """Charge un fichier JSON et retourne son contenu."""
    with open(chemin_fichier, "r", encoding="utf-8") as fichier:
        return json.load(fichier)


def charger_films_tmdb(chemin_dossier=DOSSIER_SORTIE, nom_fichier=FICHIER_TMDB):
    """Charge la liste des films déjà extraits (id, title, release_date...)."""
    chemin = os.path.join(chemin_dossier, nom_fichier)
    return charger_json(chemin)


# --- Requête générique, avec gestion du rate limit et retry ---

def requete_avec_retry(url, params=None):
    """
    Effectue une requête GET avec :
    - gestion du rate limit (429) : respecte Retry-After si présent,
      sinon backoff progressif
    - plusieurs tentatives en cas d'erreur réseau/timeout

    Retourne l'objet Response, ou None après échec définitif (le film
    concerné est alors ignoré plutôt que de faire planter tout le script).
    """
    for tentative in range(1, MAX_TENTATIVES + 1):
        try:
            reponse = requests.get(url, params=params, headers=HEADERS, timeout=TIMEOUT)

            if reponse.status_code == 429:
                attente = int(reponse.headers.get("Retry-After", PAUSE * (2 ** tentative)))
                print(f"Rate limit atteint, pause de {attente}s...")
                time.sleep(attente)
                continue

            reponse.raise_for_status()
            return reponse

        except requests.exceptions.RequestException as erreur:
            print(f"Tentative {tentative}/{MAX_TENTATIVES} échouée pour {url} : {erreur}")
            time.sleep(PAUSE * tentative)

    print(f"Abandon après {MAX_TENTATIVES} tentatives : {url}")
    return None


# --- Recherche d'article ---

def rechercher_candidats(titre, max_candidats=MAX_CANDIDATS):
    """
    Recherche les articles Wikipedia (EN) susceptibles de correspondre au
    titre donné, via l'API de recherche officielle (endpoint `opensearch`).

    `opensearch` fonctionne par préfixe de titre : on essaie d'abord le
    titre tel quel (la plupart des articles de film n'ajoutent pas le mot
    "film" dans leur titre), puis, seulement si ça ne renvoie rien, une
    seconde tentative avec "<titre> film" pour aider sur les titres ambigus
    qui nécessitent une désambiguïsation.

    Retourne :
        list[tuple(str, str)] : [(titre_article, url), ...], ou [] en cas d'échec
    """
    for requete in (titre, f"{titre} film"):
        params = {
            "action": "opensearch",
            "search": requete,
            "limit": max_candidats,
            "namespace": 0,
            "format": "json",
        }

        reponse = requete_avec_retry(API_URL, params=params)
        if reponse is None:
            return []

        donnees = reponse.json()
        if len(donnees) < 4:
            continue

        titres_candidats = donnees[1]
        urls_candidates = donnees[3]

        if titres_candidats:
            return list(zip(titres_candidats, urls_candidates))

        time.sleep(PAUSE)  # avant la 2e tentative de requête éventuelle

    return []


# --- Extraction de page (réutilise la logique de scraping_wikipedia.py) ---

def recuperer_page(url):
    """Télécharge une page HTML et retourne son contenu texte, ou None en cas d'erreur."""
    reponse = requete_avec_retry(url)
    return reponse.text if reponse is not None else None


def extraire_infobox(html):
    """Extrait les champs {label: valeur} de l'infobox d'un article Wikipedia."""
    soup = BeautifulSoup(html, "html.parser")
    infobox = soup.find("table", class_="infobox")

    if infobox is None:
        return {}

    donnees = {}
    for ligne in infobox.find_all("tr"):
        label_cell = ligne.find("th")
        valeur_cell = ligne.find("td")

        if label_cell is None or valeur_cell is None:
            continue

        label = label_cell.get_text(" ", strip=True)
        items = valeur_cell.find_all("li")
        if items:
            valeur = "; ".join(item.get_text(" ", strip=True) for item in items)
        else:
            valeur = valeur_cell.get_text(" ", strip=True)

        donnees[label] = valeur

    return donnees


def extraire_resume(html, nb_paragraphes=1):
    """Extrait les premiers paragraphes non vides du corps de l'article."""
    soup = BeautifulSoup(html, "html.parser")
    contenu = soup.find("div", class_="mw-parser-output")

    if contenu is None:
        return ""

    # Pas de recursive=False ici : Wikipedia enveloppe désormais chaque
    # section (y compris l'introduction) dans une balise <section>, donc
    # les <p> d'intro ne sont plus des enfants DIRECTS de mw-parser-output.
    # L'ordre du document place l'intro avant tout le reste, donc les
    # premiers <p> non vides rencontrés restent bien ceux du résumé.
    paragraphes = []
    for balise_p in contenu.find_all("p"):
        texte = balise_p.get_text(" ", strip=True)
        if texte:
            paragraphes.append(texte)
        if len(paragraphes) >= nb_paragraphes:
            break

    return "\n\n".join(paragraphes)


# --- Vérification par année ---

def extraire_annee_depuis_date_tmdb(date_sortie_tmdb):
    """Extrait l'année (int) d'une date TMDB au format 'YYYY-MM-DD'. None si absente/invalide."""
    if not date_sortie_tmdb or len(date_sortie_tmdb) < 4:
        return None
    try:
        return int(date_sortie_tmdb[:4])
    except ValueError:
        return None


def extraire_annee_depuis_infobox(infobox):
    """
    Cherche un champ de type "Release date" (ou variantes) dans l'infobox
    et en extrait la première année à 4 chiffres trouvée. None si absent.
    """
    for label, valeur in infobox.items():
        if label.lower().startswith("release date"):
            correspondance = re.search(r"(\d{4})", valeur)
            if correspondance:
                return int(correspondance.group(1))
    return None


def annees_concordantes(annee_infobox, annee_tmdb, tolerance=TOLERANCE_ANNEE):
    """Compare les deux années à une tolérance près. False si l'une des deux manque."""
    if annee_infobox is None or annee_tmdb is None:
        return False
    return abs(annee_infobox - annee_tmdb) <= tolerance


# --- Recherche + vérification combinées ---

def trouver_article_correspondant(titre, annee_tmdb):
    """
    Teste les candidats renvoyés par la recherche, dans l'ordre, et retourne
    le premier dont l'année de sortie (infobox) concorde avec TMDB.

    Retourne :
        dict | None : {"url": ..., "infobox": ..., "resume": ...} du candidat
        retenu, ou None si aucun candidat ne concorde (ou aucun résultat)
    """
    candidats = rechercher_candidats(titre)
    time.sleep(PAUSE)

    for titre_candidat, url in candidats:
        html = recuperer_page(url)
        time.sleep(PAUSE)

        if html is None:
            continue

        infobox = extraire_infobox(html)
        annee_infobox = extraire_annee_depuis_infobox(infobox)

        if annees_concordantes(annee_infobox, annee_tmdb):
            return {
                "url": url,
                "infobox": infobox,
                "resume": extraire_resume(html),
            }

    return None


def sauvegarder_json(donnees, chemin_fichier):
    """Sauvegarde une structure Python en fichier JSON lisible."""
    os.makedirs(os.path.dirname(chemin_fichier), exist_ok=True)
    with open(chemin_fichier, "w", encoding="utf-8") as fichier:
        json.dump(donnees, fichier, ensure_ascii=False, indent=2)
    print(f"Données sauvegardées dans {chemin_fichier}")


# --- Programme principal ---

if __name__ == "__main__":
    films_tmdb = charger_films_tmdb()
    total = len(films_tmdb)
    print(f"{total} film(s) TMDB à traiter.")

    resultats = []
    nb_trouves = 0

    for index, film in enumerate(films_tmdb, start=1):
        annee_tmdb = extraire_annee_depuis_date_tmdb(film.get("release_date"))
        article = trouver_article_correspondant(film["title"], annee_tmdb)

        if article is None:
            print(f"Aucun article Wikipedia trouvé avec confiance pour \"{film['title']}\".")
            resultats.append(
                {
                    "tmdb_id": film["id"],
                    "url_wikipedia": None,
                    "infobox": {},
                    "resume": "",
                }
            )
        else:
            nb_trouves += 1
            resultats.append(
                {
                    "tmdb_id": film["id"],
                    "url_wikipedia": article["url"],
                    "infobox": article["infobox"],
                    "resume": article["resume"],
                }
            )

        if index % 50 == 0 or index == total:
            print(f"{index}/{total} films traités, {nb_trouves} article(s) trouvé(s).")

    print(f"\nTerminé : {nb_trouves}/{total} film(s) avec un article Wikipedia identifié.")

    chemin_sortie = os.path.join(DOSSIER_SORTIE, FICHIER_SORTIE)
    sauvegarder_json(resultats, chemin_sortie)