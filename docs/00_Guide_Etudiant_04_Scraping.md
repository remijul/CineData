# Guide étudiant — Web Scraping
## Jour 3 · Projet CinéData

---

## Introduction

Toutes les données ne sont pas disponibles via une API propre. Le web scraping consiste à extraire des informations directement depuis le HTML d'une page web. C'est une compétence complémentaire à l'extraction API, avec ses propres contraintes — notamment le respect des règles du site et la compréhension de ce qui est réellement récupérable.

Film utilisé en exemple dans ce guide : **Spider-Man: Brand New Day** — [Wikipedia (EN)](https://en.wikipedia.org/wiki/Spider-Man:_Brand_New_Day) et [AlloCiné](https://www.allocine.fr/film/fichefilm_gen_cfilm=276608.html).

---

## Concepts

Scraper une page, c'est télécharger son code HTML puis y chercher les informations voulues à l'aide de sélecteurs (balises, classes CSS). Deux notions à bien distinguer :

- **Page statique** : tout le contenu visible dans le navigateur est déjà présent dans le HTML reçu par une simple requête. C'est le cas de Wikipedia.
- **Page dynamique** : une partie du contenu est générée par du JavaScript après le chargement initial. Un simple `requests.get` ne verra pas cette partie-là. C'est le cas d'une partie du contenu d'AlloCiné.

Avant d'écrire du code, il faut donc vérifier ce qui est réellement présent dans le HTML brut (clic droit → "Afficher le code source de la page"), pas seulement ce qui est visible à l'écran (onglet "Inspecter", qui montre le résultat après exécution du JavaScript).

## Définitions

| Terme | Signification |
|---|---|
| Scraping | Extraction de données depuis le HTML d'une page web |
| `robots.txt` | Fichier publié par un site pour indiquer les règles d'exploration autorisées |
| `User-Agent` | Information envoyée avec une requête pour s'identifier auprès du serveur |
| Sélecteur | Le moyen de cibler un élément HTML précis (balise, classe CSS) |
| Infobox | Le tableau structuré d'informations d'un article Wikipedia |
| Balise meta Open Graph (`og:`) | Métadonnées d'une page (titre, description, image), utilisées pour les aperçus sur les réseaux sociaux, toujours présentes dans le HTML brut |

---

## Mise en œuvre

### 1. Scraper de façon responsable

Avant de coder :
- Consultez le `/robots.txt` du site ciblé
- Identifiez-vous avec un `User-Agent` explicite plutôt que d'usurper celui d'un navigateur
- Espacez vos requêtes (`time.sleep` entre deux appels)
- Ne scrapez que ce qu'un navigateur peut afficher librement, sans contournement d'authentification ou de protection

### 2. Suivre la démo

Ouvrez `notebooks/scraping_demo.ipynb` et exécutez les cellules dans l'ordre :
1. Téléchargement et aperçu du HTML brut de la page Wikipedia
2. Repérage de l'infobox avec `BeautifulSoup`
3. Extraction d'une seule ligne, pour comprendre la structure (`th` / `td`)
4. Généralisation à toutes les lignes de l'infobox
5. Extraction du résumé de l'article
6. **Bonus AlloCiné :** test de présence de la section "Infos techniques" dans le HTML brut, puis repli sur les balises `og:` si cette section n'est pas exploitable directement

### 3. Passer au script

La logique validée dans le notebook est reportée dans `src/scraping_wikipedia.py`, qui fournit déjà : `recuperer_page`, `extraire_infobox`, `extraire_resume`, `extraire_meta_og`, `sauvegarder_json`.

### 4. Exercice — à réaliser vous-même

1. Écrivez votre propre script de scraping pour l'article Wikipedia de votre film (celui utilisé pour l'extraction API, ou un autre de votre choix).
2. Récupérez les infos souhaitées — adaptez selon ce qui est réellement présent dans l'infobox du film choisi (tous les films n'ont pas exactement les mêmes champs, ex. un film d'animation ou étranger).
3. Récupérez le premier paragraphe du résumé.
4. **Gestion des erreurs** (même logique qu'à l'atelier API) : votre script ne doit jamais planter si la page n'a pas d'infobox, si l'URL est invalide, ou si un champ attendu est absent.
5. **Optionnel :** essayez le scraping AlloCiné sur votre propre film. Si une donnée n'apparaît pas dans le HTML brut, documentez-le plutôt que de chercher un contournement technique (hors scope de cette semaine).

### Point de vigilance

Un script qui fonctionne sur un film peut échouer sur un autre si vous supposez que tous les champs sont toujours présents. Préférez des vérifications explicites (`.get()`, tests `is None`) à un code qui suppose que la structure est toujours identique.

---

## Ressource complémentaire

**[Web Scraping avec Python (et Beautiful Soup)](https://www.datacamp.com/fr/tutorial/web-scraping-using-python)** (DataCamp, tutoriel en français) — couvre `requests` + `BeautifulSoup`, avec une ouverture vers `pandas` utile pour l'étape d'agrégation qui suit cet atelier.
