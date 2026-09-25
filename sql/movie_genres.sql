-- Genres d'un film
SELECT genres.nom
FROM film_genre
JOIN genres ON genres.id = film_genre.genre_id
WHERE film_genre.film_id = ?;
