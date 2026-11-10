#!/bin/bash
# Chapter 12 cross-engine claims on MySQL 8.4 (container ch12-mysql84).
M="docker exec -i ch12-mysql84 mysql -uroot -pch12 clinic --table --force"
echo "##### MySQL version"; $M -N -e "select version()" 2>/dev/null

echo "##### CLAIM 3: BETWEEN on a DATETIME column with '2026-12-31'"
$M 2>&1 <<'SQL' | grep -v "Using a password"
DROP TABLE IF EXISTS t; CREATE TABLE t(start DATETIME);
INSERT INTO t VALUES ('2026-12-15 10:00'), ('2026-12-31 09:00');
SELECT CAST('2026-12-31' AS DATETIME) AS what_the_date_becomes;
SELECT count(*) AS rows_between_1_and_31_dec FROM t WHERE start BETWEEN '2026-12-01' AND '2026-12-31';
SELECT count(*) AS rows_half_open FROM t WHERE start >= '2026-12-01' AND start < '2027-01-01';
SELECT '2026-12-31 09:00' BETWEEN '2026-12-01' AND '2026-12-31' AS text_between_like_sqlite;
SQL

echo "##### CLAIM 2a: MySQL has no partial index (WHERE clause is a syntax error)"
$M 2>&1 <<'SQL' | grep -v "Using a password"
DROP TABLE IF EXISTS bookings;
CREATE TABLE bookings(booking_id INT AUTO_INCREMENT PRIMARY KEY, therapist VARCHAR(40) NOT NULL, start VARCHAR(16) NOT NULL, status VARCHAR(16) NOT NULL);
INSERT INTO bookings(therapist,start,status) VALUES
 ('Bethan','2026-11-02 11:00','booked'), ('Bethan','2026-11-02 11:00','booked'),
 ('Bethan','2026-11-03 09:00','cancelled'), ('Bethan','2026-11-03 09:00','booked');
CREATE UNIQUE INDEX live_slot ON bookings (therapist, start) WHERE status != 'cancelled';
SQL

echo "##### CLAIM 2b: generated column NULL for cancelled rows + unique index as the workaround; fails on clash data, then works"
$M 2>&1 <<'SQL' | grep -v "Using a password"
ALTER TABLE bookings ADD live_key VARCHAR(60) AS (IF(status <> 'cancelled', CONCAT(therapist, '|', start), NULL)) STORED, ADD UNIQUE INDEX live_slot (live_key);
UPDATE bookings SET status='cancelled' WHERE booking_id=2;
ALTER TABLE bookings ADD live_key VARCHAR(60) AS (IF(status <> 'cancelled', CONCAT(therapist, '|', start), NULL)) STORED, ADD UNIQUE INDEX live_slot (live_key);
INSERT INTO bookings(therapist,start,status) VALUES ('Bethan','2026-11-02 11:00','booked');
INSERT INTO bookings(therapist,start,status) VALUES ('Bethan','2026-11-03 09:00','cancelled');
UPDATE bookings SET status='cancelled' WHERE booking_id=4;
INSERT INTO bookings(therapist,start,status) VALUES ('Bethan','2026-11-03 09:00','booked');
SELECT count(*) AS live_rows_at_0900_on_3_nov FROM bookings WHERE start='2026-11-03 09:00' AND status!='cancelled';
SELECT count(*) AS cancelled_rows_same_slot FROM bookings WHERE start='2026-11-03 09:00' AND status='cancelled';
SQL

echo "##### CLAIM 1: default REPEATABLE READ, two transactions each check then insert -> both succeed (no index on live_key)"
$M -e "ALTER TABLE bookings DROP INDEX live_slot; DELETE FROM bookings WHERE start='2027-01-14 15:00';" 2>&1 | grep -v "Using a password"
TX="SELECT @@transaction_isolation AS isolation; START TRANSACTION; SELECT count(*) AS seen FROM bookings WHERE therapist='Bethan' AND start='2027-01-14 15:00' AND status!='cancelled'; DO SLEEP(3); INSERT INTO bookings(therapist,start,status) VALUES ('Bethan','2027-01-14 15:00','booked'); COMMIT;"
( echo "$TX" | $M 2>&1 | grep -v "Using a password" | sed 's/^/  front-desk: /' ) &
( sleep 1; echo "$TX" | $M 2>&1 | grep -v "Using a password" | sed 's/^/  website:    /' ) &
wait
$M -e "SELECT count(*) AS live_bookings_for_slot FROM bookings WHERE start='2027-01-14 15:00' AND status!='cancelled';" 2>&1 | grep -v "Using a password"
echo "##### done"
