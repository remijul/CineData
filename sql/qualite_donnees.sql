-- Couverture des données : nombre de films pour lesquels chaque champ est renseigné.
-- Une valeur "renseignée" = ni NULL, ni chaîne vide, ni 0 pour les montants.
SELECT
    COUNT(*) AS nb_films,
    -- TMDB
    SUM(CASE WHEN overview IS NOT NULL AND overview <> '' THEN 1 ELSE 0 END) AS avec_synopsis,
    SUM(CASE WHEN tagline  IS NOT NULL AND tagline  <> '' THEN 1 ELSE 0 END) AS avec_slogan,
    SUM(CASE WHEN budget   IS NOT NULL AND budget   > 0   THEN 1 ELSE 0 END) AS avec_budget,
    SUM(CASE WHEN revenue  IS NOT NULL AND revenue  > 0   THEN 1 ELSE 0 END) AS avec_revenu,
    SUM(CASE WHEN runtime  IS NOT NULL AND runtime  > 0   THEN 1 ELSE 0 END) AS avec_duree,
    SUM(CASE WHEN poster_path IS NOT NULL AND poster_path <> '' THEN 1 ELSE 0 END) AS avec_affiche,
    -- MovieLens
    SUM(CASE WHEN note_moyenne_movielens IS NOT NULL THEN 1 ELSE 0 END) AS avec_note_movielens,
    (SELECT COUNT(DISTINCT film_id) FROM film_tag) AS avec_tags,
    -- Wikipédia
    SUM(CASE WHEN resume_wikipedia      IS NOT NULL AND resume_wikipedia      <> '' THEN 1 ELSE 0 END) AS avec_resume_wikipedia,
    SUM(CASE WHEN url_wikipedia         IS NOT NULL AND url_wikipedia         <> '' THEN 1 ELSE 0 END) AS avec_url_wikipedia,
    SUM(CASE WHEN musique               IS NOT NULL AND musique               <> '' THEN 1 ELSE 0 END) AS avec_musique,
    SUM(CASE WHEN societes_production   IS NOT NULL AND societes_production   <> '' THEN 1 ELSE 0 END) AS avec_societes
FROM films;