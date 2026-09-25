# Guide étudiant — Modélisation des données & Base de données (Load)
## Jour 3 · Projet CinéData — Version alignée sur le pipeline ETL

---

## Introduction

Vous avez déjà réalisé les étapes **Extract** (vos scripts `extract_api_tmdb.py`, `extract_csv_movielens.py`, `extract_web_wikipedia.py`) et **Transform** (`transform.py`, qui a produit votre `data/processed/films_transformes.json`). Cet atelier correspond à l'étape **Load** : concevoir où et comment ces données vivent en base, puis les y charger.

Vous travaillez à partir de vos propres données, déjà en main — pas d'un exemple fictif.

---

## Concepts

Modéliser, c'est répondre à deux questions à partir de ce que vous avez réellement extrait :
1. Quelles sont les **entités** distinctes dans vos données ?
2. Comment se **relient**-elles, et selon quelle **cardinalité** ?

Un point souvent contre-intuitif, déjà vu à l'atelier POO sous un autre angle (l'état porté par un objet) : parfois, une information n'appartient ni à l'une ni à l'autre entité, mais à **la relation elle-même**. Dans vos données, le champ `character` (le rôle joué) associé à chaque personne de votre `equipe` en est un exemple direct.

Un second point à observer : deux champs qui viennent de la même source (MovieLens, par exemple) peuvent appeler des traitements différents selon leur cardinalité réelle — un champ qui contient toujours une seule valeur par film reste une colonne, un champ qui contient une liste mérite sa propre table.

## Définitions

| Terme | Signification |
|---|---|
| Entité | Une "chose" du domaine à modéliser (ex. Film, Genre, Personne) |
| Attribut | Une caractéristique d'une entité |
| Relation | Un lien entre deux entités |
| Cardinalité | La quantité d'éléments liés dans chaque sens d'une relation (1-N, N-N...) |
| Table d'association | Une table intermédiaire qui matérialise une relation N-N, et peut porter ses propres attributs |
| Étape Load (ETL) | La dernière étape du pipeline : charger des données déjà transformées dans leur système de stockage final |

---

## Mise en œuvre

### 1. Repérer les entités dans vos propres données

Ouvrez votre `data/processed/films_transformes.json` et repérez :
- Les champs simples, toujours une seule valeur par film (`title`, `budget`, `runtime`, `overview`...) → attributs directs de Film
- Les champs qui sont des listes (`genres`, `equipe`, `tags`) → candidats à une relation N-N ou 1-N
- Les champs déjà agrégés en une seule valeur par film (`note_moyenne_movielens`, `nombre_avis_movielens`) → restent des colonnes simples, même s'ils viennent d'une source qui produit par ailleurs une liste (`tags`)

### 2. Le cas de l'association avec attribut

Regardez un élément de votre liste `equipe` : il contient `character` (le rôle joué) en plus de `name`, `id`, `known_for_department`. Ce `character` n'est ni un attribut de la personne seule (elle joue des rôles différents selon les films), ni du film seul — c'est un attribut de **cette apparition précise**. Votre table d'association entre film et personne peut donc porter elle-même des colonnes (`role`, `personnage`), pas seulement les deux clés étrangères.

### 3. Concevoir votre schéma

Formalisez votre schéma logique (entités, attributs, relations, cardinalités) — un schéma simple et justifié suffit, pas besoin du formalisme Merise complet cette semaine. Écrivez-le en SQL dans votre `sql/schema.sql`.

Un exemple de résolution de ce même exercice vous sera présenté en atelier — à prendre comme un point de comparaison, pas comme un corrigé à reproduire à l'identique. Si votre raisonnement diverge (nommage différent, regroupement différent, champs gardés ou écartés différemment), c'est tout à fait acceptable tant que la logique de cardinalité est cohérente.

### 4. Charger vos données (étape Load)

Adaptez un script (type `db.py`/`load.py`) qui :
- crée vos tables à partir de votre `schema.sql`
- lit votre `films_transformes.json`
- insère chaque film, ses genres, son équipe (avec rôle et personnage), ses tags

### 5. Vérifier

Interrogez votre base pour confirmer que les relations fonctionnent : par exemple, lister tous les films d'un genre donné, ou afficher le casting complet d'un film via une jointure. Si le résultat est incohérent (doublons, valeurs manquantes inattendues), c'est souvent le signe d'un souci dans le Transform en amont plutôt que dans le Load lui-même — un bon réflexe de débogage à garder.

### Point de vigilance

Certains de vos films peuvent avoir des champs vides selon votre historique d'extraction (`equipe`, `tags`, champs Wikipedia) — votre script de chargement doit gérer ces absences sans planter (`.get()` plutôt qu'un accès direct qui suppose que tout est toujours présent).

---

## Ressources complémentaires

**[Modélisez vos bases de données](https://openclassrooms.com/fr/courses/6938711-modelisez-vos-bases-de-donnees)** (OpenClassrooms, ~8h) — pour approfondir le formalisme Merise.

**[Documentation officielle du module `sqlite3`](https://docs.python.org/fr/3/library/sqlite3.html)** — référence syntaxe pour vos scripts de chargement.