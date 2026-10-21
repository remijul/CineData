-- Nombre de films correspondant à la recherche (même filtre que movies_search.sql),
-- pour calculer la pagination. Paramètres nommés : :q, :genre
SELECT COUNT(*) AS total
FROM films f
WHERE (:q = '' OR f.title LIKE '%' || :q || '%')
  AND (:genre = '' OR EXISTS (
        SELECT 1
        FROM film_genre fg
        JOIN genres g ON g.id = fg.genre_id
        WHERE fg.film_id = f.id AND g.nom = :genre
  ));
