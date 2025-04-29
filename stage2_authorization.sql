-- Functions for login
-- TODO

-- Public restriction
REVOKE ALL ON airline FROM PUBLIC;
GRANT SELECT ON airline TO PUBLIC; -- Public view airline

REVOKE ALL ON airline_staff FROM PUBLIC;
GRANT INSERT ON airline_staff TO PUBLIC; -- Rublic register as airline staff

REVOKE ALL ON airplane FROM PUBLIC;
GRANT SELECT ON airplane TO PUBLIC; -- Public view airplane

REVOKE ALL ON airport FROM PUBLIC;
GRANT SELECT ON airport TO PUBLIC; -- Public view airport

REVOKE ALL ON booking_agent FROM PUBLIC;
GRANT INSERT ON booking_agentr TO PUBLIC; -- Rublic register as airline staff

REVOKE ALL ON booking_agent_work_for FROM PUBLIC;
GRANT INSERT ON booking_agent_work_for TO PUBLIC; -- Rublic register as airline staff continued

REVOKE ALL ON customer FROM PUBLIC;
GRANT INSERT ON customer TO PUBLIC; -- Rublic register as airline staff

REVOKE ALL ON flight FROM PUBLIC;
GRANT SELECT ON flight TO PUBLIC; -- Public view flight

REVOKE ALL ON permission FROM PUBLIC; -- Public has no access to permission, purchases or tickets

REVOKE ALL ON purchases FROM PUBLIC;

REVOKE ALL ON tickets FROM PUBLIC;
-- Customer Role
-- TODO


-- Booking Agent Role
--TODO


-- Airline Staff Role
-- TODO


-- Admin Additional Role
-- TODO


-- Operator Additional Role
-- TODO


-- Grant various roles to existing users
-- Customer
-- TODO


-- Booking Agent
-- TODO


-- Airline Staff
-- TODO


-- Admin
SELECT CONCAT('GRANT admin TO `', username, '`;') AS grant_statement
FROM permission
WHERE permission_type = 'Admin'
INTO @sql;

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Operator 
SELECT CONCAT('GRANT operator TO `', username, '`;') AS grant_statement
FROM permission
WHERE permission_type = 'Operator'
INTO @sql;

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Optional Trigger on updating authorization