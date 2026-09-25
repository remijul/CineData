-- Équipe d'un film : réalisateur(s) et acteurs, avec rôle et personnage joué
SELECT personnes.id, personnes.name, film_personne.role, film_personne.personnage
FROM film_personne
JOIN personnes ON personnes.id = film_personne.personne_id
WHERE film_personne.film_id = ?;
