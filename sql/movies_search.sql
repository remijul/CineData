-- Catalogue : recherche par titre et filtre par genre, avec pagination.
-- Paramètres NOMMÉS (dictionnaire Python) : :q, :genre, :limit, :offset
--   * :q     = texte cherché dans le titre ('' = pas de filtre)
--   * :genre = nom exact d'un genre ('' = pas de filtre)
SELECT
    f.id,
    f.title,
    substr(f.release_date, 1, 4) AS annee,
    f.vote_average,
    (
        SELECT GROUP_CONCAT(g.nom, ', ')
        FROM film_genre fg
        JOIN genres g ON g.id = fg.genre_id
        WHERE fg.film_id = f.id
    ) AS genres
FROM films f
WHERE (:q = '' OR f.title LIKE '%' || :q || '%')
  AND (:genre = '' OR EXISTS (
        SELECT 1
        FROM film_genre fg
        JOIN genres g ON g.id = fg.genre_id
        WHERE fg.film_id = f.id AND g.nom = :genre
  ))
ORDER BY f.title
LIMIT :limit OFFSET :offset;
