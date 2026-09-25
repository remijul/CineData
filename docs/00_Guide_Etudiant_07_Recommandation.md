# Guide étudiant — Système de recommandation & intégration API
## Ouverture IA · Projet CinéData

---

## Introduction

Vous avez déjà construit une API qui expose vos données. Cet atelier ajoute un vrai composant d'intelligence artificielle "classique" (sans LLM) : un moteur de recommandation par similarité de contenu, exposé via une route `/recommendation/{film_id}`. C'est l'occasion de comprendre un principe central quand on expose un modèle via une API : le calcul lourd doit être fait **avant**, pas à chaque requête.

---

## Concepts

Un moteur de recommandation **par similarité de contenu** compare des films entre eux à partir de leurs caractéristiques (genres, casting, tags, tagline), sans avoir besoin des goûts d'autres utilisateurs (contrairement à un système collaboratif) ni d'un LLM. On transforme le texte descriptif de chaque film en vecteur numérique (**TF-IDF**), puis on mesure à quel point deux vecteurs "pointent dans la même direction" (**similarité cosinus**) : plus deux films partagent de termes significatifs, plus leur score est élevé.

Point clé pour l'intégration API : ce calcul est coûteux à l'échelle de tous les films. On ne le refait pas à chaque requête — on le calcule **une fois** (comme on entraînerait un modèle ML), on sauvegarde le résultat sur disque, et l'API se contente de le charger et de le consulter.

## Définitions

| Terme | Signification |
|---|---|
| TF-IDF | Une façon de transformer du texte en vecteur numérique, qui donne plus de poids aux mots rares et discriminants qu'aux mots très fréquents |
| Similarité cosinus | Une mesure de proximité entre deux vecteurs, entre 0 (rien en commun) et 1 (identiques) |
| "Soup" de texte | La concaténation de plusieurs champs (genres, tags, casting, tagline) en un seul texte par film, pour une vectorisation unique |
| Précalcul (artefact) | Un résultat de calcul sauvegardé sur disque (ici via `joblib`), chargé tel quel plutôt que recalculé |

---

## Mise en œuvre

### 1. Extraire les données (depuis la base, pas l'API)

Écrivez une requête SQL qui retourne, par film : titre, tagline, genres/tags/casting concaténés (pour construire le soup), et les champs à afficher dans le résultat final (genre, durée, date de sortie, acteurs, réalisateurs — séparés du soup).

### 2. Construire le soup et vectoriser

Dans un notebook d'abord (comme `notebooks/recommandation_demo.ipynb`) :
- concaténez genres + tags + casting + tagline en un texte par film
- collez les entités multi-mots sans espace (`"Tom Hanks"` → `"tomhanks"`) pour éviter les fausses proximités
- vectorisez avec `TfidfVectorizer`, calculez la matrice de similarité avec `cosine_similarity`
- écrivez une fonction `recommander(film_id, top_n=5)` qui retourne les films les plus proches

**Point de vigilance :** une valeur manquante lue depuis une colonne pandas peut être `NaN` (float) et pas `None` — et `NaN` est "vrai" dans un `if`, donc `if not texte:` ne l'intercepte pas. Utilisez `pd.isna(texte)` pour vérifier une valeur manquante.

### 3. Séparer précalcul et service (étape Load, version modèle)

Une fois le notebook validé, transposez-le en deux fichiers distincts :
- **Un script de précalcul** (`src/precompute_...py`) : charge les données, construit le soup, calcule la matrice de similarité, sauvegarde le résultat (`joblib.dump`) dans un fichier sur disque
- **Un module côté API** : charge cet artefact **au niveau module** (donc une seule fois, au démarrage de l'API), et expose une fonction `recommander()` qui consulte l'artefact déjà chargé

**Point de vigilance nommage :** donnez à ce module un nom clairement différent du fichier de route qui l'utilisera (`routers/recommendation.py`) — un nom presque identique à une lettre près est une source d'erreur réelle, pas juste théorique.

### 4. Exposer via l'API

Créez la route `/recommendation/{film_id}` : appelle `recommander()`, retourne un modèle Pydantic listant les films recommandés avec titre, genre, durée, date de sortie, acteurs, réalisateurs. Gérez le cas d'un identifiant inconnu avec une `HTTPException(404, ...)`.

### Rappel important

Si vous rechargez votre base (relancez votre script Load), **relancez aussi le script de précalcul** — sinon l'API continue de servir un résultat basé sur d'anciennes données, sans erreur visible.

---

## Ressource complémentaire

**[Documentation scikit-learn — `TfidfVectorizer`](https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html)** et **[`cosine_similarity`](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.pairwise.cosine_similarity.html)** — pour ajuster les paramètres si vous voulez affiner votre moteur.
