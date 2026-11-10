-- Exercise 12_03: The "we miss you" list says nobody (begin)
SELECT client_ref, name, email
FROM clients
WHERE client_ref NOT IN (
    SELECT client_ref FROM bookings
    WHERE start >= '2026-10-01' AND status != 'cancelled')
ORDER BY client_ref;
