-- Exercise 12_03: The "we miss you" list says nobody (one possible answer)
SELECT c.client_ref, c.name, c.email
FROM clients AS c
WHERE NOT EXISTS (
    SELECT 1 FROM bookings AS b
    WHERE b.client_ref = c.client_ref
      AND b.start >= '2026-10-01' AND b.status != 'cancelled')
ORDER BY c.client_ref;
