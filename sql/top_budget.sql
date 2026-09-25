-- Top 10 des films par budget, 0/NULL exclus
SELECT id, title, budget
FROM films
WHERE budget IS NOT NULL AND budget > 0
ORDER BY budget DESC
LIMIT 10;
