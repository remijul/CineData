# Fiche de cadrage — Projet 1, Phase 4
## "CinéData" — Collecte, agrégation et mise à disposition de données cinéma

---

## 1. Contexte

Vous intégrez la Phase 4 du parcours Développeur d'application IA, en alternance. Après la formation Data Analyst (OpenClassrooms), vous savez explorer, nettoyer et visualiser des données. Ce projet vous fait passer à l'étape suivante : **automatiser** la collecte de données depuis plusieurs sources, les **structurer**, les **stocker**, et les **mettre à disposition** d'autres composants applicatifs via une API.

Ce premier projet mobilise le **Bloc de compétences 1** du référentiel Dev IA : *"Réaliser la collecte, le stockage et la mise à disposition des données d'un projet en intelligence artificielle"*.

**Durée :** 1 semaine (5 jours), avec possibilité de prolongation d'une semaine pour approfondissement.

---

## 2. Objectif du projet

Vous constituez, pour le compte d'un commanditaire fictif ("CinéData", un service de recommandation de films en devenir), un **jeu de données cinéma unifié**, à partir de trois sources hétérogènes, que vous rendez accessible via une API REST.

Ce jeu de données a vocation, dans une phase ultérieure (non couverte cette semaine), à alimenter un moteur de recommandation basé sur l'IA — gardez cet usage final en tête dans vos choix de modélisation.

---

## 3. Sources de données à mobiliser

Vous devez extraire et croiser **au minimum ces trois sources** :

| Source | Type | Exemple |
|---|---|---|
| **API TMDB** (The Movie Database) | Service web REST | Films populaires, détails, genres, casting — nécessite une clé API gratuite (inscription sur themoviedb.org) |
| **Fichier de données** | CSV | Jeu de données type MovieLens (films + notes utilisateurs) ou tout catalogue CSV équivalent que vous choisissez |
| **Scraping léger** | Page web | Page Wikipédia d'un film ou d'une franchise (infobox : réalisateur, budget, box-office...) — privilégier Wikipédia, plus permissif que les sites commerciaux pour un usage pédagogique |

**Consigne de scraping responsable :** limitez la fréquence de vos requêtes, identifiez-vous via un `User-Agent`, et ne scrapez que ce dont vous avez réellement besoin.

---

## 4. Livrables attendus

1. **Un dépôt Git** versionné, avec historique de commits explicite, `.gitignore` propre (aucune clé API commitée), et README de présentation.
2. **Scripts d'extraction et d'agrégation**, fonctionnels de bout en bout :
   - extraction API TMDB
   - lecture du fichier CSV
   - scraping de la page cible
   - agrégation en un jeu de données unique, avec gestion des entrées corrompues/manquantes et homogénéisation des formats (dates, unités, identifiants)
3. **Un schéma de données** (modèle logique, entités/relations/cardinalités) justifiant vos choix de structuration.
4. **Une base de données** (SQLite ou PostgreSQL) créée à partir de ce schéma, alimentée par un script d'import.
5. **Une API REST** (FastAPI) exposant au minimum :
   - la liste des films (avec filtres simples : genre, année...)
   - le détail d'un film
   - une documentation Swagger fonctionnelle (générée automatiquement par FastAPI)
6. **Une courte note technique** (1-2 pages) : choix effectués, difficultés rencontrées, ce que vous feriez différemment avec plus de temps.

---

## 5. Ce qui n'est PAS exigé cette semaine

- Une modélisation Merise complète et formalisée avec tous les niveaux (conceptuel/logique/physique) — un schéma logique clair suffit.
- Une authentification sur l'API.
- Un code entièrement en programmation orientée objet — vous découvrez la POO cette semaine, son usage reste **optionnel** (bonus pour les profils à l'aise).
- La conformité RGPD complète (registre des traitements) — on se contente d'un traitement responsable des données (pas de données personnelles identifiantes collectées).

---

## 6. Déroulé de la semaine

| Jour | Contenu |
|---|---|
| **J1** | Appropriation du référentiel (REAC), lancement et cadrage du projet, atelier Git |
| **J2** | Atelier POO (introduction), atelier script API TMDB, puis réalisation en autonomie |
| **J3** | Atelier scraping, atelier modélisation des données, puis réalisation en autonomie |
| **J4** | Atelier FastAPI, puis réalisation en autonomie |
| **J5** | Finalisation en autonomie, restitution |

---

## 7. Modalités de restitution (J5)

Présentation de 10-15 minutes par étudiant ou binôme :
- démonstration du pipeline d'extraction → agrégation → stockage → API (via Swagger ou requêtes de test)
- retour sur les choix de modélisation
- un point de difficulté technique et comment il a été résolu

---

## 8. Compétences du référentiel mobilisées

Ce projet vous permet de travailler C1 à C5 du Bloc 1 (voir grille d'évaluation associée). Gardez une trace de votre travail (commits, README, note technique) : c'est ce qui permettra d'objectiver l'acquisition de ces compétences.
