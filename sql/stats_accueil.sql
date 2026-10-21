-- Chiffres clés de la page d'accueil (une seule ligne de résultat).
-- Les années vides ou absentes sont ignorées ; une note à 0 (aucun vote)
-- est exclue de la moyenne grâce à NULLIF.
SELECT
    (SELECT COUNT(*) FROM films)     AS nb_films,
    (SELECT COUNT(*) FROM personnes) AS nb_personnes,
    (SELECT COUNT(*) FROM genres)    AS nb_genres,
    MIN(CASE WHEN release_date <> '' THEN substr(release_date, 1, 4) END) AS annee_min,
    MAX(CASE WHEN release_date <> '' THEN substr(release_date, 1, 4) END) AS annee_max,
    ROUND(AVG(NULLIF(vote_average, 0)), 1) AS note_moyenne
FROM films;
