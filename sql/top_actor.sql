-- Top 10 des acteurs par nombre de films dans la base
SELECT personnes.id, personnes.name, COUNT(*) AS nombre_films
FROM film_personne
JOIN personnes ON personnes.id = film_personne.personne_id
WHERE film_personne.role = 'Acteur'
GROUP BY personnes.id, personnes.name
ORDER BY nombre_films DESC
LIMIT 10;
