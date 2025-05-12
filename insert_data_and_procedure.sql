-- 1. Airline
INSERT INTO `airline` (`airline_name`) VALUES
  ('China Eastern'),
  ('Emirates');

-- 2. Airline Staff
INSERT INTO `airline_staff` (`username`, `password`, `first_name`, `last_name`, `date_of_birth`, `airline_name`) VALUES
  ('admin1', MD5('adminpass'), 'John',   'Doe',   '1985-07-12', 'China Eastern'),
  ('admin2', MD5('admin2pass'), 'John',  'Smith', '1990-03-15', 'Emirates');

-- 3. Staff Permissions
INSERT INTO `permission` (`username`, `permission_type`) VALUES
  ('admin1', 'Admin'),
  ('admin1', 'Operator');

-- 4. Airplane
INSERT INTO `airplane` (`airline_name`, `airplane_id`, `seats`) VALUES
  ('China Eastern', 1, 1),
  ('China Eastern', 2, 300),
  ('Emirates', 3, 350);

-- 5. Airport
INSERT INTO `airport` (`airport_name`, `airport_city`) VALUES
  ('DXB', 'Dubai'),
  ('JFK', 'New York'),
  ('PVG', 'Shanghai'),
  ('LAX', 'Los Angeles'),
  ('CDG', 'Paris'),
  ('HND', 'Tokyo'),
  ('SIN', 'Singapore');

-- 6. Agent
INSERT INTO `booking_agent` (`email`, `password`, `booking_agent_id`) VALUES
  ('agent1@example.com', MD5('agentpass'), 1);

-- 7. Agent's Airline Relationship
INSERT INTO `booking_agent_work_for` (`email`, `airline_name`) VALUES
  ('agent1@example.com', 'China Eastern');

-- 8. Customer
INSERT INTO `customer` (
  `email`, `name`, `password`, `building_number`,
  `street`, `city`, `state`, `phone_number`,
  `passport_number`, `passport_expiration`, `passport_country`, `date_of_birth`
) VALUES
  ('mj23@example.com', 'Michael Jordan', MD5('AirJordan'), '23',
   'Champion Drive', 'Chicago', 'Illinois', 1234567890,
   'USMJ1992', '2028-12-31', 'USA', '1963-02-17'),
  ('mamba24@example.com', 'Kobe Bryant', MD5('BlackMamba'), '24',
   'Legacy Lane', 'Los Angeles', 'California', 1111111111,
   'USKB2008', '2024-08-24', 'USA', '1978-08-23');

-- 9. Flight
INSERT INTO `flight` (
  `airline_name`, `flight_num`, `departure_airport`, `departure_time`,
  `arrival_airport`, `arrival_time`, `price`, `status`, `airplane_id`
) VALUES
  ('China Eastern', 1001, 'JFK', '2025-05-15 08:00:00', 'PVG', '2025-05-16 12:00:00', 800, 'Upcoming', 1),
  ('China Eastern', 1002, 'PVG', '2025-05-20 14:00:00', 'JFK', '2025-05-20 18:00:00', 850, 'Delayed', 2),
  ('China Eastern', 1003, 'PVG', '2025-05-01 09:30:00', 'HND', '2025-05-01 13:00:00', 600, 'Upcoming', 2),
  ('China Eastern', 1004, 'HND', '2025-05-05 11:00:00', 'CDG', '2025-05-05 18:30:00', 950, 'Upcoming', 2),
  ('China Eastern', 1005, 'HND', '2025-05-15 09:00:00', 'PVG', '2025-05-15 12:30:00', 600, 'Delayed', 1),
  ('China Eastern', 1006, 'PVG', '2025-06-01 14:00:00', 'JFK', '2025-06-01 18:00:00', 850, 'Delayed', 1),
  ('Emirates', 2001, 'DXB', '2025-05-10 06:00:00', 'JFK', '2025-05-10 14:00:00', 1200, 'In Progress', 3),
  ('Emirates', 2002, 'JFK', '2025-05-25 10:00:00', 'DXB', '2025-05-25 20:00:00', 1150, 'Upcoming', 3), -- Fixed arrival_time
  ('Emirates', 2003, 'CDG', '2025-05-10 08:00:00', 'SIN', '2025-05-10 18:00:00', 1050, 'Upcoming', 3),
  ('Emirates', 2004, 'SIN', '2025-06-10 06:00:00', 'DXB', '2025-06-10 12:00:00', 1000, 'In Progress', 3),
  ('Emirates', 2005, 'DXB', '2025-06-15 08:00:00', 'LAX', '2025-06-15 16:00:00', 1250, 'In Progress', 3);

-- 10. Ticket
INSERT INTO `ticket` (`ticket_id`, `airline_name`, `flight_num`) VALUES
  (1, 'China Eastern', 1001),
  (2, 'China Eastern', 1002),
  (3, 'Emirates', 2002),
  (4, 'China Eastern', 1003),
  (5, 'China Eastern', 1004),
  (6, 'Emirates', 2003),
  (7, 'China Eastern', 1005),
  (8, 'China Eastern', 1006),
  (9, 'Emirates', 2004),
  (10, 'Emirates', 2005);

-- 11. Purchases
INSERT INTO `purchases` (
  `ticket_id`, `customer_email`, `booking_agent_id`, `purchase_date`
) VALUES
  (1, 'mj23@example.com', NULL, '2025-04-09'),
  (2, 'mamba24@example.com', 1, '2025-04-09'),
  (3, 'mj23@example.com', NULL, '2025-04-20'),
  (4, 'mj23@example.com', 1, '2025-03-20'),
  (5, 'mamba24@example.com', 1, '2025-04-21'),
  (6, 'mamba24@example.com', NULL, '2025-04-21'),
  (7, 'mj23@example.com', 1,    '2025-03-22'),
  (8, 'mamba24@example.com', NULL, '2025-04-22'),
  (9, 'mj23@example.com', NULL, '2025-02-18'),
  (10, 'mamba24@example.com', 1,    '2025-04-22');

-- Procedures
-- 1. Upcoming tickets of a specific customer
DELIMITER //

CREATE PROCEDURE customer_get_upcoming_flights(IN p_customer_email VARCHAR(50))
BEGIN
    SELECT 
        t.ticket_id, 
        f.airline_name, 
        f.flight_num, 
        f.departure_airport, 
        f.arrival_airport, 
        f.departure_time, 
        f.arrival_time, 
        f.status, 
        f.price
    FROM Purchases p
    JOIN Ticket t ON p.ticket_id = t.ticket_id
    JOIN Flight f ON t.airline_name = f.airline_name AND t.flight_num = f.flight_num
    WHERE p.customer_email = p_customer_email AND f.status = 'Upcoming';
END //

DELIMITER ;

-- 2. Get the staff's airline name
DELIMITER //

CREATE PROCEDURE GetStaffAirlineInfo(IN p_username VARCHAR(50))
BEGIN
    SELECT airline_name FROM Airline_Staff WHERE username = p_username;
END //

DELIMITER ;