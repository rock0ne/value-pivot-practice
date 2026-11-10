#!/bin/bash
# Chapter 12 cross-engine claims on PostgreSQL 17 (container ch12-pg17).
P="docker exec -i ch12-pg17 psql -U postgres -d clinic -v ON_ERROR_STOP=0"
echo "##### PG version"; $P -tAc "select version()"

echo "##### CLAIM 3: BETWEEN on a timestamp column with '2026-12-31'"
$P <<'SQL'
\set QUIET on
DROP TABLE IF EXISTS t; CREATE TABLE t(start timestamp);
INSERT INTO t VALUES ('2026-12-15 10:00'), ('2026-12-31 09:00');
\set QUIET off
SELECT '2026-12-31'::timestamp AS what_the_date_becomes;
SELECT count(*) AS rows_between_1_and_31_dec FROM t WHERE start BETWEEN '2026-12-01' AND '2026-12-31';
SELECT count(*) AS rows_half_open FROM t WHERE start >= '2026-12-01' AND start < '2027-01-01';
SELECT '2026-12-31 09:00' BETWEEN '2026-12-01' AND '2026-12-31' AS text_between_like_sqlite;
SQL

echo "##### CLAIM 2a: partial unique index syntax; fails on live clash data"
$P <<'SQL'
\set QUIET on
DROP TABLE IF EXISTS bookings;
CREATE TABLE bookings(booking_id serial PRIMARY KEY, therapist text NOT NULL, start text NOT NULL, status text NOT NULL);
INSERT INTO bookings(therapist,start,status) VALUES
 ('Bethan','2026-11-02 11:00','booked'), ('Bethan','2026-11-02 11:00','booked'),
 ('Bethan','2026-11-10 10:00','completed'), ('Bethan','2026-11-10 10:00','booked'),
 ('Bethan','2026-11-03 09:00','cancelled'), ('Bethan','2026-11-03 09:00','booked');
\set QUIET off
CREATE UNIQUE INDEX live_slot ON bookings (therapist, start) WHERE status != 'cancelled';
SQL
echo "##### CLAIM 2b: CREATE UNIQUE INDEX CONCURRENTLY failing leaves an INVALID index"
$P -c "CREATE UNIQUE INDEX CONCURRENTLY live_slot ON bookings (therapist, start) WHERE status != 'cancelled';"
$P -c "SELECT indexrelid::regclass AS index_name, indisvalid FROM pg_index WHERE indexrelid = 'live_slot'::regclass;"
$P -c "DROP INDEX live_slot;"
echo "##### CLAIM 2c: after resolving the clashes the partial index builds; cancelled duplicates allowed, live ones refused, rebook works"
$P <<'SQL'
UPDATE bookings SET status='cancelled' WHERE booking_id IN (2,4);
CREATE UNIQUE INDEX live_slot ON bookings (therapist, start) WHERE status != 'cancelled';
INSERT INTO bookings(therapist,start,status) VALUES ('Bethan','2026-11-02 11:00','booked');
INSERT INTO bookings(therapist,start,status) VALUES ('Bethan','2026-11-03 09:00','cancelled');
UPDATE bookings SET status='cancelled' WHERE booking_id=6;
INSERT INTO bookings(therapist,start,status) VALUES ('Bethan','2026-11-03 09:00','booked');
SELECT count(*) AS live_rows_at_0900_on_3_nov FROM bookings WHERE start='2026-11-03 09:00' AND status!='cancelled';
SQL

echo "##### CLAIM 2d: exclusion constraint with btree_gist for overlapping appointments"
$P <<'SQL'
CREATE EXTENSION IF NOT EXISTS btree_gist;
DROP TABLE IF EXISTS appts;
CREATE TABLE appts(therapist text, start timestamptz, finish timestamptz,
  EXCLUDE USING gist (therapist WITH =, tstzrange(start, finish) WITH &&));
INSERT INTO appts VALUES ('Bethan','2026-11-20 10:00+00','2026-11-20 11:00+00');
INSERT INTO appts VALUES ('Bethan','2026-11-20 10:30+00','2026-11-20 11:00+00');
INSERT INTO appts VALUES ('Bethan','2026-11-20 11:00+00','2026-11-20 11:30+00');
SELECT count(*) AS appts_kept FROM appts;
SQL

echo "##### CLAIM 1a: READ COMMITTED, two transactions each check then insert -> both succeed"
$P -c "DROP INDEX live_slot; DELETE FROM bookings WHERE start='2027-01-14 15:00';"
TX='BEGIN; SELECT count(*) AS seen FROM bookings WHERE therapist=$$Bethan$$ AND start=$$2027-01-14 15:00$$ AND status!=$$cancelled$$; SELECT pg_sleep(3); INSERT INTO bookings(therapist,start,status) VALUES ($$Bethan$$,$$2027-01-14 15:00$$,$$booked$$); COMMIT;'
( echo "$TX" | $P -q 2>&1 | sed 's/^/  front-desk: /' ) &
( sleep 1; echo "$TX" | $P -q 2>&1 | sed 's/^/  website:    /' ) &
wait
$P -c "SELECT count(*) AS live_bookings_for_slot FROM bookings WHERE start='2027-01-14 15:00' AND status!='cancelled';"

echo "##### CLAIM 1b: SERIALIZABLE, same two transactions -> one fails with a serialization error"
$P -c "DELETE FROM bookings WHERE start='2027-01-14 15:00';"
TXS="${TX/BEGIN;/BEGIN ISOLATION LEVEL SERIALIZABLE;}"
( echo "$TXS" | $P -q 2>&1 | sed 's/^/  front-desk: /' ) &
( sleep 1; echo "$TXS" | $P -q 2>&1 | sed 's/^/  website:    /' ) &
wait
$P -c "SELECT count(*) AS live_bookings_for_slot FROM bookings WHERE start='2027-01-14 15:00' AND status!='cancelled';"
echo "##### done"
