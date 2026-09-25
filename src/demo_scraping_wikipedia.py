"""
scraping_wikipedia.py
Extraction de données film par web scraping.

Cible principale : l'infobox d'un article Wikipedia (structure HTML stable,
usage autorisé pour un usage pédagogique/non commercial).
Cible bonus : les balises meta Open Graph d'une page AlloCiné (utile car le
contenu principal de la page AlloCiné est en grande partie généré par
JavaScript et n'est pas visible via un simple requests.get — les balises
meta, elles, sont présentes dans le HTML brut).

Approche : programmation fonctionnelle simple, dans la continuité de
extract_api.py.
"""

import time
import json
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "ProjetCineData-Formation/1.0 (usage pedagogique)"
}


def recuperer_page(url):
    """Télécharge une page HTML et retourne son contenu texte, ou None en cas d'erreur."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as erreur:
        print(f"Erreur lors du téléchargement de {url} : {erreur}")
        return None

    return response.text


def extraire_infobox(html):
    """
    Extrait les champs de l'infobox d'un article Wikipedia (film).

    Structure ciblée : <table class="infobox">, avec des lignes <tr>
    contenant un <th> (le label, ex. "Directed by") et un <td> (la valeur).

    Retourne :
        dict : {label: valeur}, ou {} si aucune infobox trouvée
    """
    soup = BeautifulSoup(html, "html.parser")
    infobox = soup.find("table", class_="infobox")

    if infobox is None:
        print("Aucune infobox trouvée sur cette page")
        return {}

    donnees = {}
    for ligne in infobox.find_all("tr"):
        label_cell = ligne.find("th")
        valeur_cell = ligne.find("td")

        if label_cell is None or valeur_cell is None:
            continue  # ligne d'image ou de titre, sans label/valeur exploitable

        label = label_cell.get_text(" ", strip=True)

        # certains champs contiennent plusieurs valeurs sous forme de liste
        # (ex. plusieurs scénaristes) : on les rassemble avec un séparateur
        items = valeur_cell.find_all("li")
        if items:
            valeur = "; ".join(item.get_text(" ", strip=True) for item in items)
        else:
            valeur = valeur_cell.get_text(" ", strip=True)

        donnees[label] = valeur

    return donnees


def extraire_resume(html, nb_paragraphes=1):
    """
    Extrait les premiers paragraphes de texte de l'article (résumé/chapô).

    Paramètres :
        nb_paragraphes (int) : nombre de paragraphes non vides à conserver

    Retourne :
        str : le résumé, ou une chaîne vide si le contenu n'est pas trouvé
    """
    soup = BeautifulSoup(html, "html.parser")
    contenu = soup.find("div", class_="mw-parser-output")

    if contenu is None:
        return ""

    paragraphes = []
    for balise_p in contenu.find_all("p", recursive=False):
        texte = balise_p.get_text(" ", strip=True)
        if texte:  # les tout premiers <p> d'un article Wikipedia sont souvent vides
            paragraphes.append(texte)
        if len(paragraphes) >= nb_paragraphes:
            break

    return "\n\n".join(paragraphes)


def extraire_meta_og(html):
    """
    Extrait les balises meta Open Graph (og:title, og:description, og:image)
    d'une page. Utile pour les pages dont le contenu principal est généré en
    JavaScript (ex. AlloCiné) et donc invisible à un simple requests.get.

    Retourne :
        dict : {"titre": ..., "description": ..., "image": ...}
    """
    soup = BeautifulSoup(html, "html.parser")

    def get_meta(propriete):
        balise = soup.find("meta", property=propriete)
        return balise["content"] if balise and balise.has_attr("content") else None

    return {
        "titre": get_meta("og:title"),
        "description": get_meta("og:description"),
        "image": get_meta("og:image"),
    }


def sauvegarder_json(donnees, chemin_fichier):
    """Sauvegarde une structure Python en fichier JSON lisible."""
    with open(chemin_fichier, "w", encoding="utf-8") as fichier:
        json.dump(donnees, fichier, ensure_ascii=False, indent=2)
    print(f"Données sauvegardées dans {chemin_fichier}")


# --- Programme principal ---

if __name__ == "__main__":
    URL_WIKIPEDIA = "https://en.wikipedia.org/wiki/Spider-Man:_Brand_New_Day"
    URL_ALLOCINE = "https://www.allocine.fr/film/fichefilm_gen_cfilm=276608.html"

    print("Scraping Wikipedia (infobox + résumé)...")
    html_wiki = recuperer_page(URL_WIKIPEDIA)

    resultat = {}

    if html_wiki:
        resultat["infobox"] = extraire_infobox(html_wiki)
        resultat["resume"] = extraire_resume(html_wiki)

        print("\nChamps extraits de l'infobox :")
        for label, valeur in resultat["infobox"].items():
            print(f"- {label} : {valeur}")

    time.sleep(0.5)  # pause de politesse avant la requête suivante

    print("\nScraping AlloCiné (balises meta)...")
    html_allocine = recuperer_page(URL_ALLOCINE)

    if html_allocine:
        resultat["meta_allocine"] = extraire_meta_og(html_allocine)
        print("\nMeta extraites d'AlloCiné :")
        for label, valeur in resultat["meta_allocine"].items():
            print(f"- {label} : {valeur}")

    sauvegarder_json(resultat, "data/raw/film_scraping.json")
