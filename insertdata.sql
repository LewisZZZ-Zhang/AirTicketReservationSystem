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
