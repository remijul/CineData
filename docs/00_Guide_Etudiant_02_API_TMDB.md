# Guide étudiant — API REST & Script d'extraction TMDB
## Jour 2 · Projet CinéData

---

## Introduction

Vous allez construire votre premier script d'extraction automatisée de données, en interrogeant l'API TMDB (The Movie Database). C'est la brique la plus directement liée au critère C1 du référentiel : *"construction des requêtes HTTP pour la récupération des données depuis un service web (REST)"*.

À la fin de cet atelier, vous aurez un script fonctionnel qui récupère des films populaires, leurs genres, leur casting, et qui ne plante jamais même en cas d'erreur réseau ou d'API.

---

## Concepts

Une **API REST** expose des données via de simples requêtes HTTP, à des adresses (endpoints) prévisibles. Vous envoyez une requête `GET` à une URL, éventuellement avec des paramètres, et vous recevez une réponse au format JSON.

Anatomie d'une URL d'appel :
```
https://api.themoviedb.org/3/movie/popular?api_key=XXX&language=fr-FR&page=1
└────────────┬───────────┘└┬┘└──┬──┘└───────────────────┬───────────────────┘
     domaine / base URL  version  endpoint      paramètres de requête
```

Chaque réponse arrive avec un **code de statut HTTP**, qui indique si tout s'est bien passé et, sinon, pourquoi.

## Définitions

| Terme | Signification |
|---|---|
| API REST | Une interface qui expose des données via des requêtes HTTP standard |
| Endpoint | L'URL précise qui correspond à une ressource ou une action (ex. `/movie/popular`) |
| Paramètre de requête | Une valeur ajoutée après `?` dans l'URL pour filtrer/configurer la réponse |
| Paramètre de chemin | Une valeur intégrée directement dans le chemin de l'URL (ex. `/movie/{id}`) |
| JSON | Le format de données structurées renvoyé par la plupart des API REST |
| Code de statut HTTP | Un nombre qui indique le résultat de la requête |

**Codes de statut à connaître :**

| Code | Signification | Cas fréquent avec TMDB |
|---|---|---|
| 200 | OK | Tout s'est bien passé |
| 401 | Non autorisé | Clé API invalide ou manquante |
| 404 | Non trouvé | Identifiant de film inexistant |
| 429 | Trop de requêtes | Vous avez dépassé la limite de requêtes |
| 500 / 503 | Erreur serveur | Problème côté TMDB, réessayez plus tard |

---

## Mise en œuvre

### 1. Obtenir votre clé API TMDB

Voir `src/Infos_API_TMDB.md` pour la procédure complète d'inscription. Point d'attention : le champ "Application Summary" du formulaire TMDB exige une description assez détaillée (usage non commercial, non publié, but pédagogique) — une phrase trop courte est souvent rejetée.

Une fois la clé obtenue, placez-la dans votre fichier `.env` :
```
TMDB_API_KEY=votre_cle_ici
```

### 2. Explorer avec le notebook

Ouvrez `notebooks/extract_api_exploration.ipynb` et exécutez les cellules dans l'ordre. Ce notebook vous fait passer, étape par étape :
- d'un appel brut à l'API (vous voyez la réponse JSON complète)
- à des fonctions réutilisables (`get_popular_movies`, `get_genre_mapping`, `get_movie_details`)
- à un DataFrame pandas exploitable pour explorer les données

### 3. Passer au script

Une fois la logique validée dans le notebook, reportez-la dans `src/extract_api.py` (déjà fourni comme base fonctionnelle) sous forme de fonctions appelées depuis un bloc `if __name__ == "__main__":`.

### 4. Exercice — à compléter vous-même

À partir de ce que vous avez vu en démo, complétez votre script pour qu'il :

1. Récupère la liste des films populaires (déjà vu)
2. Récupère le détail de chacun des 5 premiers films (déjà vu)
3. **Nouveau — à chercher vous-même :** récupère le casting de chaque film (les 5 premiers acteurs suffisent), via l'endpoint de credits de TMDB.
   - Cherchez dans la documentation officielle ([developer.themoviedb.org/reference](https://developer.themoviedb.org/reference)) l'endpoint qui donne le casting d'un film à partir de son identifiant
   - La réponse contient une clé `cast` (liste d'acteurs), avec un nom (`name`) et un rôle (`character`) par acteur
4. **Gestion des erreurs :** votre script ne doit jamais planter, même si :
   - la clé API est invalide (401)
   - l'identifiant de film n'existe pas (404)
   - la requête met trop de temps à répondre (timeout)

   Testez volontairement chacun de ces cas (par exemple, modifiez temporairement votre clé pour simuler un 401, ou utilisez un `timeout` très court comme `timeout=0.001` pour provoquer un vrai timeout) et vérifiez que votre script affiche un message clair au lieu de planter.

### Niveaux de progression

| Niveau | Ce qui est fait |
|---|---|
| 1 | Liste + détail par film fonctionnels |
| 2 | + casting ajouté pour chaque film |
| 3 | + gestion d'erreurs testée sur au moins 2 cas différents |

---

## Ressource complémentaire

**[Documentation officielle TMDB](https://developer.themoviedb.org/docs)**, en particulier la **[référence des endpoints](https://developer.themoviedb.org/reference)** avec son explorateur interactif "Try It" (attention : dans ce menu, choisissez "Access Token Auth" plutôt que "API Key Auth", qui est buggé côté TMDB — dans votre code, vous continuez cependant à utiliser la clé en paramètre `api_key` comme montré en démo).
