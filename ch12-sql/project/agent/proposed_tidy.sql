-- What the clinic's AI agent proposed when Ruth asked it to "tidy up the duplicate bookings".
-- Written by the author to show a common failure. Read it before you run anything like it.

DELETE FROM bookings
WHERE (therapist, start) IN (
    SELECT therapist, start
    FROM bookings
    WHERE status != 'cancelled'
    GROUP BY therapist, start
    HAVING COUNT(*) > 1
);
