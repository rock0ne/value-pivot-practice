-- Exercise 12_05: Make the database refuse a double booking (begin)
-- The assistant's suggestion:
CREATE UNIQUE INDEX one_booking_per_slot
ON bookings (therapist, start);
