CREATE TABLE `airline` (
  `airline_name` varchar(50) NOT NULL,
  PRIMARY KEY(`airline_name`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `airline_staff`
--

CREATE TABLE `airline_staff` (
  `username` varchar(50) NOT NULL,
  `password` varchar(50) NOT NULL,
  `first_name` varchar(50) NOT NULL,
  `last_name` varchar(50) NOT NULL,
  `date_of_birth` date NOT NULL,
  `airline_name` varchar(50) NOT NULL,
  PRIMARY KEY(`username`),
  FOREIGN KEY(`airline_name`) REFERENCES `airline`(`airline_name`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

CREATE TABLE `permission` (
    `username` varchar(50) NOT NULL,
    `permission_type` varchar(50) NOT NULL,
    PRIMARY KEY(`username`, `permission_type`),
    FOREIGN KEY(`username`) REFERENCES `airline_staff`(`username`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Table structure for table `airplane`
--

CREATE TABLE `airplane` (
  `airline_name` varchar(50) NOT NULL,
  `airplane_id` int(11) NOT NULL,
  `seats` int(11) NOT NULL,
  PRIMARY KEY(`airline_name`, `airplane_id`),
  FOREIGN KEY(`airline_name`) REFERENCES `airline`(`airline_name`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `airport`
--

CREATE TABLE `airport` (
  `airport_name` varchar(50) NOT NULL,
  `airport_city` varchar(50) NOT NULL,
  PRIMARY KEY(`airport_name`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `booking_agent`
--

CREATE TABLE `booking_agent` (
  `email` varchar(50) NOT NULL,
  `password` varchar(50) NOT NULL,
  `booking_agent_id` int(11) NOT NULL,
  PRIMARY KEY(`email`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE `booking_agent_work_for` (
  `email` varchar(50) NOT NULL,
  `airline_name` varchar(50) NOT NULL,
  PRIMARY KEY(`email`,`airline_name`),
  FOREIGN KEY(`email`) REFERENCES `booking_agent`(`email`),
  FOREIGN KEY(`airline_name`) REFERENCES `airline`(`airline_name`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `customer`
--

CREATE TABLE `customer` (
  `email` varchar(50) NOT NULL,
  `name` varchar(50) NOT NULL,
  `password` varchar(50) NOT NULL,
  `building_number` varchar(30) NOT NULL,
  `street` varchar(30) NOT NULL,
  `city` varchar(30) NOT NULL,
  `state` varchar(30) NOT NULL,
  `phone_number` int(11) NOT NULL,
  `passport_number` varchar(30) NOT NULL,
  `passport_expiration` date NOT NULL,
  `passport_country` varchar(50) NOT NULL,
  `date_of_birth` date NOT NULL,
  PRIMARY KEY(`email`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `flight`
--

CREATE TABLE `flight` (
  `airline_name` varchar(50) NOT NULL,
  `flight_num` int(11) NOT NULL,
  `departure_airport` varchar(50) NOT NULL,
  `departure_time` datetime NOT NULL,
  `arrival_airport` varchar(50) NOT NULL,
  `arrival_time` datetime NOT NULL,
  `price` decimal(10,0) NOT NULL,
  `status` varchar(50) NOT NULL,
  `airplane_id` int(11) NOT NULL,
  PRIMARY KEY(`airline_name`, `flight_num`),
  FOREIGN KEY(`airline_name`, `airplane_id`) REFERENCES `airplane`(`airline_name`, `airplane_id`),
  FOREIGN KEY(`departure_airport`) REFERENCES `airport`(`airport_name`),
  FOREIGN KEY(`arrival_airport`) REFERENCES `airport`(`airport_name`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;


-- --------------------------------------------------------

--
-- Table structure for table `ticket`
--

CREATE TABLE `ticket` (
  `ticket_id` int(11) NOT NULL,
  `airline_name` varchar(50) NOT NULL,
  `flight_num` int(11) NOT NULL,
  PRIMARY KEY(`ticket_id`),
  FOREIGN KEY(`airline_name`, `flight_num`) REFERENCES `flight`(`airline_name`, `flight_num`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;


-- --------------------------------------------------------

--
-- Table structure for table `purchases`
--

CREATE TABLE `purchases` (
  `ticket_id` int(11) NOT NULL,
  `customer_email` varchar(50) NOT NULL,
  `booking_agent_id` int(11),
  `purchase_date` date NOT NULL,
  PRIMARY KEY(`ticket_id`, `customer_email`),
  FOREIGN KEY(`ticket_id`) REFERENCES `ticket`(`ticket_id`),
  FOREIGN KEY(`customer_email`) REFERENCES `customer`(`email`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;



-- 0507

DELIMITER //
CREATE PROCEDURE PurchaseTicket(
    IN p_airline_name VARCHAR(255),
    IN p_flight_num VARCHAR(255),
    IN p_customer_email VARCHAR(255),
    OUT p_result VARCHAR(255)
)
BEGIN
    DECLARE remaining INT DEFAULT 0;
    DECLARE new_ticket_id INT DEFAULT 0;

    -- 检查剩余座位
    SELECT a.seats - IFNULL(COUNT(p.ticket_id), 0)
      INTO remaining
      FROM Flight f
      JOIN Airplane a ON f.airline_name = a.airline_name AND f.airplane_id = a.airplane_id
      LEFT JOIN Ticket t ON f.airline_name = t.airline_name AND f.flight_num = t.flight_num
      LEFT JOIN Purchases p ON t.ticket_id = p.ticket_id
     WHERE f.airline_name = p_airline_name AND f.flight_num = p_flight_num
     GROUP BY a.seats;

    IF remaining > 0 THEN
        -- 新 ticket_id
        SELECT IFNULL(MAX(ticket_id), 0) + 1 INTO new_ticket_id FROM Ticket;
        -- 插入 Ticket
        INSERT INTO Ticket(ticket_id, airline_name, flight_num)
        VALUES (new_ticket_id, p_airline_name, p_flight_num);
        -- 插入 Purchases
        INSERT INTO Purchases(ticket_id, customer_email, purchase_date)
        VALUES (new_ticket_id, p_customer_email, CURDATE());
        SET p_result = 'success';
    ELSE
        SET p_result = 'no_ticket';
    END IF;
END //
DELIMITER ;