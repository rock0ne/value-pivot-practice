-- Exercise 12_02: December was £648 short (begin)
SELECT COALESCE(SUM(CASE status
           WHEN 'completed'   THEN price_pence
           WHEN 'no_show'     THEN price_pence / 2
           WHEN 'late_cancel' THEN price_pence / 2
           ELSE 0 END), 0) AS revenue_pence
FROM bookings
WHERE start BETWEEN '2026-12-01' AND '2026-12-31';
