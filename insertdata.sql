-- 04/22
-- 1. 航空公司
INSERT INTO `airline` (`airline_name`) VALUES
  ('China Eastern'),
  ('Emirates');

-- 2. 航空公司员工
INSERT INTO `airline_staff` (`username`, `password`, `first_name`, `last_name`, `date_of_birth`, `airline_name`) VALUES
  ('admin1', 'adminpass', 'John',   'Doe',   '1985-07-12', 'China Eastern');

-- 3. 员工权限
INSERT INTO `permission` (`username`, `permission_type`) VALUES
  ('admin1', 'Admin'),
  ('admin1', 'Operator');

-- 4. 飞机
INSERT INTO `airplane` (`airline_name`, `airplane_id`, `seats`) VALUES
  ('China Eastern', 1, 200),
  ('China Eastern', 2, 300),
  ('Emirates',        3, 350);

-- 5. 机场
INSERT INTO `airport` (`airport_name`, `airport_city`) VALUES
  ('DXB', 'Dubai'),
  ('JFK', 'New York'),
  ('PVG', 'Shanghai');

-- 6. 订票代理
INSERT INTO `booking_agent` (`email`,               `password`,   `booking_agent_id`) VALUES
  ('agent1@example.com', 'agentpass', 1);

-- 7. 代理所属航空公司
INSERT INTO `booking_agent_work_for` (`email`,               `airline_name`) VALUES
  ('agent1@example.com', 'China Eastern');

-- 8. 客户
INSERT INTO `customer` (
  `email`,               `name`,         `password`,  `building_number`,
  `street`,              `city`,         `state`,     `phone_number`,
  `passport_number`,     `passport_expiration`, `passport_country`, `date_of_birth`
) VALUES
  ('peterparker@example.com', 'Peter Parker', 'spiderman', '20',
   'Queens St', 'New York', 'NY', 1234567890,
   'P12345678', '2028-06-01', 'USA', '1995-05-20'),
  ('tonystark@example.com',   'Tony Stark',   'ironman',   '10880',
   'Malibu Point', 'Malibu', 'CA', 1111111111,
   'P87654321', '2030-12-15', 'USA', '1970-05-29');

-- 9. 航班
INSERT INTO `flight` (
  `airline_name`, `flight_num`, `departure_airport`, `departure_time`,
  `arrival_airport`, `arrival_time`, `price`, `status`, `airplane_id`
) VALUES
  ('China Eastern', 1001, 'JFK', '2025-03-15 08:00:00', 'PVG', '2025-03-16 12:00:00',  800, 'Upcoming',    1),
  ('China Eastern', 1002, 'PVG', '2025-03-20 14:00:00', 'JFK', '2025-03-20 18:00:00',  850, 'Delayed',     2),
  ('Emirates',      2001, 'DXB', '2025-04-10 06:00:00', 'JFK', '2025-04-10 14:00:00', 1200, 'In Progress', 3);

-- 10. 机票
INSERT INTO `ticket` (`ticket_id`, `airline_name`, `flight_num`) VALUES
  (1, 'China Eastern', 1001),
  (2, 'China Eastern', 1002);

-- 11. 购票记录
INSERT INTO `purchases` (
  `ticket_id`, `customer_email`, `booking_agent_id`, `purchase_date`
) VALUES
  (1, 'peterparker@example.com', NULL, '2025-04-09'),
  (2, 'tonystark@example.com',    1,    '2025-04-09');


-- 04/23 
INSERT INTO `airport` (`airport_name`, `airport_city`) VALUES
  ('LAX', 'Los Angeles'),
  ('CDG', 'Paris'),
  ('HND', 'Tokyo'),
  ('SIN', 'Singapore');

INSERT INTO `flight` (
  `airline_name`, `flight_num`, `departure_airport`, `departure_time`,
  `arrival_airport`, `arrival_time`, `price`, `status`, `airplane_id`
) VALUES
  ('Emirates', 2002, 'JFK', '2025-04-25 10:00:00', 'DXB', '2025-04-25 20:00:00', 1150, 'Upcoming', 3),
  ('China Eastern', 1003, 'PVG', '2025-05-01 09:30:00', 'HND', '2025-05-01 13:00:00', 600, 'Upcoming', 2),
  ('China Eastern', 1004, 'HND', '2025-05-05 11:00:00', 'CDG', '2025-05-05 18:30:00', 950, 'Upcoming', 2),
  ('Emirates', 2003, 'CDG', '2025-05-10 08:00:00', 'SIN', '2025-05-10 18:00:00', 1050, 'Upcoming', 3);

INSERT INTO `ticket` (`ticket_id`, `airline_name`, `flight_num`) VALUES
  (3, 'Emirates', 2002),
  (4, 'China Eastern', 1003),
  (5, 'China Eastern', 1004),
  (6, 'Emirates', 2003);


-- Peter Parker 购买航班 2002 和 1003
INSERT INTO `purchases` (`ticket_id`, `customer_email`, `booking_agent_id`, `purchase_date`) VALUES
  (3, 'peterparker@example.com', NULL, '2025-04-20'),
  (4, 'peterparker@example.com', 1,    '2025-04-20');

-- Tony Stark 购买航班 1004 和 2003
INSERT INTO `purchases` (`ticket_id`, `customer_email`, `booking_agent_id`, `purchase_date`) VALUES
  (5, 'tonystark@example.com', 1,    '2025-04-21'),
  (6, 'tonystark@example.com', NULL, '2025-04-21');

INSERT INTO `flight` (
  `airline_name`, `flight_num`, `departure_airport`, `departure_time`,
  `arrival_airport`, `arrival_time`, `price`, `status`, `airplane_id`
) VALUES
  ('China Eastern', 1005, 'HND', '2025-05-15 09:00:00', 'PVG', '2025-05-15 12:30:00', 600, 'Delayed', 1),
  ('China Eastern', 1006, 'PVG', '2025-06-01 14:00:00', 'JFK', '2025-06-01 18:00:00', 850, 'Delayed', 1),
  ('Emirates', 2004, 'SIN', '2025-06-10 06:00:00', 'DXB', '2025-06-10 12:00:00', 1000, 'In Progress', 3),
  ('Emirates', 2005, 'DXB', '2025-06-15 08:00:00', 'LAX', '2025-06-15 16:00:00', 1250, 'In Progress', 3);


INSERT INTO `ticket` (`ticket_id`, `airline_name`, `flight_num`) VALUES
  (7, 'China Eastern', 1005),
  (8, 'China Eastern', 1006),
  (9, 'Emirates', 2004),
  (10, 'Emirates', 2005);

  -- Peter Parker 继续购票：1005 和 2004
INSERT INTO `purchases` (`ticket_id`, `customer_email`, `booking_agent_id`, `purchase_date`) VALUES
  (7, 'peterparker@example.com', 1,    '2025-04-22'),
  (9, 'peterparker@example.com', NULL, '2025-04-22');

-- Tony Stark 继续购票：1006 和 2005
INSERT INTO `purchases` (`ticket_id`, `customer_email`, `booking_agent_id`, `purchase_date`) VALUES
  (8, 'tonystark@example.com', NULL, '2025-04-22'),
  (10, 'tonystark@example.com', 1,    '2025-04-22');

-- 5/3 加密
ALTER TABLE Customer MODIFY password VARCHAR(32);
ALTER TABLE Booking_Agent MODIFY password VARCHAR(32);
ALTER TABLE Airline_Staff MODIFY password VARCHAR(32);

UPDATE Customer SET password = MD5(password);
UPDATE Booking_Agent SET password = MD5(password);
UPDATE Airline_Staff SET password = MD5(password);

--5/4 new data
-- New airlines
INSERT INTO `airline` (`airline_name`) VALUES
  ('Qatar Airways'),
  ('Singapore Airlines'),
  ('Lufthansa');


-- New airline staff
INSERT INTO `airline_staff` (`username`, `password`, `first_name`, `last_name`, `date_of_birth`, `airline_name`) VALUES
  ('qatar_admin', MD5('qatar123'), 'Alice', 'Johnson', '1980-01-15', 'Qatar Airways'),
  ('singapore_admin', MD5('singapore123'), 'Bob', 'Smith', '1985-03-22', 'Singapore Airlines'),
  ('lufthansa_admin', MD5('lufthansa123'), 'Charlie', 'Brown', '1990-07-10', 'Lufthansa');


-- Permissions for new airline staff
INSERT INTO `permission` (`username`, `permission_type`) VALUES
  ('qatar_admin', 'Admin'),
  ('qatar_admin', 'Operator'),
  ('singapore_admin', 'Admin'),
  ('singapore_admin', 'Operator'),
  ('lufthansa_admin', 'Admin'),
  ('lufthansa_admin', 'Operator');


-- New airplanes
INSERT INTO `airplane` (`airline_name`, `airplane_id`, `seats`) VALUES
  ('Qatar Airways', 4, 300),
  ('Singapore Airlines', 5, 350),
  ('Lufthansa', 6, 280);


-- New airports
INSERT INTO `airport` (`airport_name`, `airport_city`) VALUES
  ('DOH', 'Doha'),
  ('SIN', 'Singapore'),
  ('FRA', 'Frankfurt');


-- New flights
INSERT INTO `flight` (
  `airline_name`, `flight_num`, `departure_airport`, `departure_time`,
  `arrival_airport`, `arrival_time`, `price`, `status`, `airplane_id`
) VALUES
  ('Qatar Airways', 3001, 'DOH', '2025-07-01 08:00:00', 'JFK', '2025-07-01 16:00:00', 1200, 'Upcoming', 4),
  ('Singapore Airlines', 4001, 'SIN', '2025-07-05 10:00:00', 'LHR', '2025-07-05 18:00:00', 1100, 'Upcoming', 5),
  ('Lufthansa', 5001, 'FRA', '2025-07-10 12:00:00', 'ORD', '2025-07-10 16:00:00', 950, 'Upcoming', 6);
INSERT INTO `flight` (
  `airline_name`, `flight_num`, `departure_airport`, `departure_time`,
  `arrival_airport`, `arrival_time`, `price`, `status`, `airplane_id`
) VALUES
  ('Qatar Airways', 3002, 'DOH', '2025-07-10 09:00:00', 'LHR', '2025-07-10 15:00:00', 1000, 'Upcoming', 4),
  ('Qatar Airways', 3003, 'LHR', '2025-07-15 11:00:00', 'DOH', '2025-07-15 17:00:00', 950, 'Upcoming', 4),
  ('Singapore Airlines', 4002, 'SIN', '2025-07-20 08:00:00', 'ORD', '2025-07-20 18:00:00', 1200, 'Upcoming', 5),
  ('Singapore Airlines', 4003, 'ORD', '2025-07-25 10:00:00', 'SIN', '2025-07-25 20:00:00', 1150, 'Upcoming', 5),
  ('Lufthansa', 5002, 'FRA', '2025-08-01 06:00:00', 'JFK', '2025-08-01 12:00:00', 1300, 'Upcoming', 6),
  ('Lufthansa', 5003, 'JFK', '2025-08-05 14:00:00', 'FRA', '2025-08-05 20:00:00', 1250, 'Upcoming', 6);


-- New tickets
INSERT INTO `ticket` (`ticket_id`, `airline_name`, `flight_num`) VALUES
  (11, 'Qatar Airways', 3001),
  (12, 'Singapore Airlines', 4001),
  (13, 'Lufthansa', 5001);
INSERT INTO `ticket` (`ticket_id`, `airline_name`, `flight_num`) VALUES
  (14, 'Qatar Airways', 3002),
  (15, 'Qatar Airways', 3003),
  (16, 'Singapore Airlines', 4002),
  (17, 'Singapore Airlines', 4003),
  (18, 'Lufthansa', 5002),
  (19, 'Lufthansa', 5003);


-- New customers
INSERT INTO `customer` (
  `email`, `name`, `password`, `building_number`, `street`, `city`, `state`, `phone_number`,
  `passport_number`, `passport_expiration`, `passport_country`, `date_of_birth`
) VALUES
  ('brucewayne@example.com', 'Bruce Wayne', MD5('batman123'), '1007', 'Wayne Manor', 'Gotham', 'NJ', 9876543210, 'P98765432', '2035-01-01', 'USA', '1980-02-19'),
  ('dianaprince@example.com', 'Diana Prince', MD5('wonderwoman123'), '300', 'Amazon St', 'Themyscira', 'NA', 1231231234, 'P12312312', '2030-05-15', 'GRC', '1990-03-22');


-- New booking agents
INSERT INTO `booking_agent` (`email`, `password`, `booking_agent_id`) VALUES
  ('agent2@example.com', MD5('agentpass2'), 2),
  ('agent3@example.com', MD5('agentpass3'), 3);


-- New purchases
INSERT INTO `purchases` (`ticket_id`, `customer_email`, `booking_agent_id`, `purchase_date`) VALUES
  (11, 'brucewayne@example.com', NULL, '2025-06-15'),
  (12, 'dianaprince@example.com', 2, '2025-06-16'),
  (13, 'brucewayne@example.com', 3, '2025-06-17');
INSERT INTO `purchases` (`ticket_id`, `customer_email`, `booking_agent_id`, `purchase_date`) VALUES
  (14, 'brucewayne@example.com', NULL, '2025-07-01'),
  (15, 'dianaprince@example.com', 2, '2025-07-02'),
  (16, 'brucewayne@example.com', 3, '2025-07-03'),
  (17, 'dianaprince@example.com', NULL, '2025-07-04'),
  (18, 'brucewayne@example.com', 2, '2025-07-05'),
  (19, 'dianaprince@example.com', 3, '2025-07-06');


-- Booking agents working for airlines
INSERT INTO `booking_agent_work_for` (`email`, `airline_name`) VALUES
  ('agent2@example.com', 'Qatar Airways'),
  ('agent2@example.com', 'Singapore Airlines'),
  ('agent3@example.com', 'Lufthansa'),
  ('agent3@example.com', 'Emirates');