-- Exercise 12_01: Find the double bookings (begin)
-- The assistant's booking code checks the slot is free before it books.
-- Don't trust that. Ask the data what actually happened.
SELECT therapist, start, status
FROM bookings
ORDER BY therapist, start
LIMIT 20;
