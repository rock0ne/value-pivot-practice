-- Exercise 12_05: Make the database refuse a double booking (one possible answer)
CREATE UNIQUE INDEX one_live_booking_per_slot
ON bookings (therapist, start)
WHERE status != 'cancelled';
