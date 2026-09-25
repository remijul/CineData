-- Une ligne par film, avec genres/tags/casting (acteurs + réalisateur)
-- concaténés (séparateur '|' pour pouvoir re-découper proprement côté Python,
-- chaque entité pouvant elle-même contenir des espaces, ex. "Science Fiction").
SELECT
    films.id,
    films.title,
    films.tagline,
    (
        SELECT GROUP_CONCAT(genres.nom, '|')
        FROM film_genre
        JOIN genres ON genres.id = film_genre.genre_id
        WHERE film_genre.film_id = films.id
    ) AS genres_texte,
    (
        SELECT GROUP_CONCAT(tag, '|')
        FROM film_tag
        WHERE film_tag.film_id = films.id
    ) AS tags_texte,
    (
        SELECT GROUP_CONCAT(personnes.name, '|')
        FROM film_personne
        JOIN personnes ON personnes.id = film_personne.personne_id
        WHERE film_personne.film_id = films.id
    ) AS casting_texte
FROM films;