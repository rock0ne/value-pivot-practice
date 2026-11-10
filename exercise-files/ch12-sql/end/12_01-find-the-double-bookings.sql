-- Exercise 12_01: Find the double bookings (one possible answer)
SELECT therapist, start, COUNT(*) AS live_bookings
FROM bookings
WHERE status != 'cancelled'
GROUP BY therapist, start
HAVING COUNT(*) > 1
ORDER BY start;
