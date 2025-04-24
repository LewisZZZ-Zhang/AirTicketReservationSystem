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


-- 04/23 还没有加，我要去问问
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

