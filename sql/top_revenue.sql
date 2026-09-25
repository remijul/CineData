-- Top 10 des films par chiffre d'affaires (revenue), 0/NULL exclus
SELECT id, title, revenue
FROM films
WHERE revenue IS NOT NULL AND revenue > 0
ORDER BY revenue DESC
LIMIT 10;
