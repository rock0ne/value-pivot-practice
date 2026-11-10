-- Exercise 12_04: Your turn: the loyalty card (begin)
SELECT c.client_ref, c.name, COUNT(*) AS visits
FROM clients AS c
LEFT JOIN bookings AS b
  ON b.client_ref = c.client_ref
 AND b.status = 'completed'
 AND b.start >= '2026-12-01' AND b.start < '2027-01-01'
GROUP BY c.client_ref, c.name
ORDER BY c.client_ref;
