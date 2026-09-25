-- Une ligne par film : champs de base + genres/tags/casting concaténés
-- (séparateur '|') pour construire le "soup" TF-IDF, et acteurs/réalisateurs
-- séparés pour l'enrichissement du résultat de l'API.
SELECT
    films.id,
    films.title,
    films.tagline,
    films.runtime,
    films.release_date,
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
    ) AS casting_texte,
    (
        SELECT GROUP_CONCAT(personnes.name, '|')
        FROM film_personne
        JOIN personnes ON personnes.id = film_personne.personne_id
        WHERE film_personne.film_id = films.id AND film_personne.role = 'Acteur'
    ) AS actors_texte,
    (
        SELECT GROUP_CONCAT(personnes.name, '|')
        FROM film_personne
        JOIN personnes ON personnes.id = film_personne.personne_id
        WHERE film_personne.film_id = films.id AND film_personne.role = 'Réalisateur'
    ) AS directors_texte
FROM films;