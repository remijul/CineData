-- Liste paginée des films : id, titre, année de sortie
SELECT id, title, substr(release_date, 1, 4) AS annee
FROM films
ORDER BY id
LIMIT ? OFFSET ?;
