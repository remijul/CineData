# Guide étudiant — POO, Introduction
## Jour 2 · Projet CinéData

---

## Introduction

Vous connaissez déjà la programmation fonctionnelle (des fonctions qui s'enchaînent) — c'est ce que vous avez utilisé pour `extract_api.py`. Cet atelier vous fait découvrir une autre façon de structurer du code : la programmation orientée objet (POO). Ce n'est pas obligatoire cette semaine, mais vous en aurez besoin bientôt (Phase 5) — l'idée est de comprendre le principe avant que ça devienne indispensable.

---

## Concepts

Une fonction ne "retient" rien d'un appel à l'autre : si vous l'appelez deux fois, elle refait tout le travail depuis le début. Un **objet**, lui, peut conserver un **état** — une information gardée en mémoire entre deux appels de ses méthodes.

Exemple concret dans ce projet : la correspondance des genres TMDB (id → nom) ne change jamais pendant l'exécution du script. En fonctionnel, chaque appel à la fonction qui la récupère refait l'appel réseau. En orienté objet, un objet peut la récupérer une seule fois et la garder en cache.

## Définitions

| Terme | Signification |
|---|---|
| Classe | Le plan de construction (définit quels attributs et méthodes auront les objets) |
| Objet / instance | Un exemplaire concret construit à partir d'une classe |
| `__init__` | La méthode spéciale exécutée à la création d'un objet (le constructeur) |
| `self` | À l'intérieur d'une classe, désigne l'objet lui-même |
| Attribut | Une donnée stockée dans un objet (ex. `self.api_key`) |
| Méthode | Une fonction qui appartient à une classe |
| État | Une information qu'un objet conserve entre deux appels de ses méthodes |

---

## Mise en œuvre

### 1. Observer le problème en version fonctionnelle

Ouvrez `src/extract_api.py` et repérez la fonction `get_genre_mapping()`. Posez-vous la question : si cette fonction est appelée plusieurs fois dans le script, refait-elle le même travail à chaque fois ? (Réponse : oui — rien ne lui permet de savoir qu'elle l'a déjà fait.)

### 2. Suivre la démo comparative

Ouvrez `notebooks/poo_demo_comparative.ipynb` et exécutez les cellules dans l'ordre :
1. Une fonction `get_genre_mapping_fonction()` appelée deux fois — observez qu'elle refait l'appel réseau à chaque fois
2. Une première classe minimale `TMDBExtractorDemo`, avec mise en cache
3. Le même objet, appelé deux fois — cette fois, l'appel réseau n'a lieu qu'une fois
4. Deux instances avec des configurations différentes (langues différentes), pour voir que chaque objet garde son propre état indépendamment des autres

### 3. Regarder la classe complète

`src/extract_api_oop.py` reprend exactement la logique de `extract_api.py`, réorganisée en classe `TMDBExtractor`. Comparez les deux fichiers côte à côte :
- Quelles fonctions sont devenues des méthodes ?
- Qu'est-ce qui est stocké dans `__init__` et qui n'existait pas avant ?
- Où voit-on concrètement le bénéfice du cache (`self._genres_mapping`) ?

### 4. Exercice optionnel (bonus)

Ce n'est **pas un prérequis** cette semaine. Si vous voulez vous entraîner :

> Refactorez votre propre script `extract_api.py` en une classe `TMDBExtractor`, sur le modèle vu en démo. Essayez d'ajouter une méthode qui n'existait pas dans la version fonctionnelle (par exemple, une méthode qui enchaîne plusieurs étapes en une seule, comme `extraire_et_simplifier_populaires`).

Vous pouvez comparer votre résultat avec `src/extract_api_oop.py` une fois votre propre version terminée.

### Point de repère

La version fonctionnelle n'est pas "moins bonne" — elle convient très bien à un script simple exécuté une fois. La POO devient intéressante quand il faut garder un état, gérer plusieurs configurations en parallèle, ou quand un projet grossit.

---

## Ressource complémentaire

**[Découvrez la programmation orientée objet avec Python](https://openclassrooms.com/fr/courses/4302126-decouvrez-la-programmation-orientee-objet-avec-python)** (OpenClassrooms, cours en libre accès, ~12h). Va bien au-delà de ce qui est vu en atelier (héritage, structuration de code) — à utiliser en approfondissement, pas comme pré-requis pour cette semaine.
