-- Harbour Lane Physiotherapy booking database (fictional).
-- Written by the author to show mistakes that AI-written code commonly makes.

CREATE TABLE clients (
    client_ref TEXT PRIMARY KEY,
    name       TEXT NOT NULL,
    email      TEXT NOT NULL
);

CREATE TABLE bookings (
    booking_id  INTEGER PRIMARY KEY,
    therapist   TEXT NOT NULL,
    start       TEXT NOT NULL,                          -- 'YYYY-MM-DD HH:MM'
    client_ref  TEXT REFERENCES clients(client_ref),    -- NULL for a walk-in
    service     TEXT NOT NULL,
    price_pence INTEGER NOT NULL,
    status      TEXT NOT NULL,   -- booked, completed, no_show, cancelled, late_cancel
    created_at  TEXT NOT NULL    -- 'YYYY-MM-DD HH:MM:SS'
);

CREATE INDEX bookings_by_slot ON bookings (therapist, start);
