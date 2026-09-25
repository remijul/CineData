-- Tags MovieLens associés à un film
SELECT tag
FROM film_tag
WHERE film_id = ?;
