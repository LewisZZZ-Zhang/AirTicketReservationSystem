-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Apr 09, 2025 at 08:22 AM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `airticketsystem`
--

-- --------------------------------------------------------

--
-- Table structure for table `airline`
--

CREATE TABLE `airline` (
  `airline_name` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `airline`
--

INSERT INTO `airline` (`airline_name`) VALUES
('China Eastern'),
('Emirates');

-- --------------------------------------------------------

--
-- Table structure for table `airline_staff`
--

CREATE TABLE `airline_staff` (
  `username` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL,
  `first_name` varchar(255) NOT NULL,
  `last_name` varchar(255) NOT NULL,
  `date_of_birth` date NOT NULL,
  `airline_name` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `airline_staff`
--

INSERT INTO `airline_staff` (`username`, `password`, `first_name`, `last_name`, `date_of_birth`, `airline_name`) VALUES
('admin1', 'adminpass', 'John', 'Doe', '1985-07-12', 'China Eastern');

-- --------------------------------------------------------

--
-- Table structure for table `airline_staff_permissions`
--

CREATE TABLE `airline_staff_permissions` (
  `username` varchar(255) NOT NULL,
  `permission_type` enum('Admin','Operator') NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `airline_staff_permissions`
--

INSERT INTO `airline_staff_permissions` (`username`, `permission_type`) VALUES
('admin1', 'Admin'),
('admin1', 'Operator');

-- --------------------------------------------------------

--
-- Table structure for table `airplane`
--

CREATE TABLE `airplane` (
  `airplane_id` int(11) NOT NULL,
  `airline_name` varchar(255) DEFAULT NULL,
  `num_seats` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `airplane`
--

INSERT INTO `airplane` (`airplane_id`, `airline_name`, `num_seats`) VALUES
(1, 'China Eastern', 200),
(2, 'China Eastern', 300),
(3, 'Emirates', 350);

-- --------------------------------------------------------

--
-- Table structure for table `airport`
--

CREATE TABLE `airport` (
  `airport_name` varchar(255) NOT NULL,
  `city` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `airport`
--

INSERT INTO `airport` (`airport_name`, `city`) VALUES
('DXB', 'Dubai'),
('JFK', 'New York'),
('PVG', 'Shanghai');

-- --------------------------------------------------------

--
-- Table structure for table `booking_agent`
--

CREATE TABLE `booking_agent` (
  `email` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL,
  `booking_agent_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `booking_agent`
--

INSERT INTO `booking_agent` (`email`, `password`, `booking_agent_id`) VALUES
('agent1@example.com', 'agentpass', 1);

-- --------------------------------------------------------

--
-- Table structure for table `booking_agent_works_for`
--

CREATE TABLE `booking_agent_works_for` (
  `booking_agent_email` varchar(255) NOT NULL,
  `airline_name` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `booking_agent_works_for`
--

INSERT INTO `booking_agent_works_for` (`booking_agent_email`, `airline_name`) VALUES
('agent1@example.com', 'China Eastern');

-- --------------------------------------------------------

--
-- Table structure for table `customer`
--

CREATE TABLE `customer` (
  `email` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL,
  `building_number` varchar(10) DEFAULT NULL,
  `street` varchar(255) DEFAULT NULL,
  `city` varchar(255) DEFAULT NULL,
  `state` varchar(255) DEFAULT NULL,
  `phone_number` varchar(20) DEFAULT NULL,
  `passport_number` varchar(50) DEFAULT NULL,
  `passport_expiration` date DEFAULT NULL,
  `passport_country` varchar(255) DEFAULT NULL,
  `date_of_birth` date NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `customer`
--

INSERT INTO `customer` (`email`, `name`, `password`, `building_number`, `street`, `city`, `state`, `phone_number`, `passport_number`, `passport_expiration`, `passport_country`, `date_of_birth`) VALUES
('peterparker@example.com', 'Peter Parker', 'spiderman', '20', 'Queens St', 'New York', 'NY', '1234567890', 'P12345678', '2028-06-01', 'USA', '1995-05-20'),
('tonystark@example.com', 'Tony Stark', 'ironman', '10880', 'Malibu Point', 'Malibu', 'CA', '9876543210', 'P87654321', '2030-12-15', 'USA', '1970-05-29');

-- --------------------------------------------------------

--
-- Table structure for table `flight`
--

CREATE TABLE `flight` (
  `airline_name` varchar(255) NOT NULL,
  `flight_num` int(11) NOT NULL,
  `departure_airport` varchar(255) DEFAULT NULL,
  `departure_time` datetime NOT NULL,
  `arrival_airport` varchar(255) DEFAULT NULL,
  `arrival_time` datetime NOT NULL,
  `price` decimal(10,2) NOT NULL,
  `airplane_id` int(11) DEFAULT NULL,
  `status` enum('Upcoming','In Progress','Delayed') NOT NULL DEFAULT 'Upcoming'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `flight`
--

INSERT INTO `flight` (`airline_name`, `flight_num`, `departure_airport`, `departure_time`, `arrival_airport`, `arrival_time`, `price`, `airplane_id`, `status`) VALUES
('China Eastern', 1001, 'JFK', '2025-03-15 08:00:00', 'PVG', '2025-03-16 12:00:00', 800.00, 1, 'Upcoming'),
('China Eastern', 1002, 'PVG', '2025-03-20 14:00:00', 'JFK', '2025-03-20 18:00:00', 850.00, 2, 'Delayed'),
('Emirates', 2001, 'DXB', '2025-04-10 06:00:00', 'JFK', '2025-04-10 14:00:00', 1200.00, 3, 'In Progress');

-- --------------------------------------------------------

--
-- Table structure for table `ticket`
--

CREATE TABLE `ticket` (
  `ticket_id` int(11) NOT NULL,
  `customer_email` varchar(255) DEFAULT NULL,
  `airline_name` varchar(255) DEFAULT NULL,
  `flight_num` int(11) DEFAULT NULL,
  `booking_agent_email` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `ticket`
--

INSERT INTO `ticket` (`ticket_id`, `customer_email`, `airline_name`, `flight_num`, `booking_agent_email`) VALUES
(1, 'peterparker@example.com', 'China Eastern', 1001, NULL),
(2, 'tonystark@example.com', 'China Eastern', 1002, 'agent1@example.com');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `airline`
--
ALTER TABLE `airline`
  ADD PRIMARY KEY (`airline_name`);

--
-- Indexes for table `airline_staff`
--
ALTER TABLE `airline_staff`
  ADD PRIMARY KEY (`username`),
  ADD KEY `airline_name` (`airline_name`);

--
-- Indexes for table `airline_staff_permissions`
--
ALTER TABLE `airline_staff_permissions`
  ADD PRIMARY KEY (`username`,`permission_type`);

--
-- Indexes for table `airplane`
--
ALTER TABLE `airplane`
  ADD PRIMARY KEY (`airplane_id`),
  ADD KEY `airline_name` (`airline_name`);

--
-- Indexes for table `airport`
--
ALTER TABLE `airport`
  ADD PRIMARY KEY (`airport_name`);

--
-- Indexes for table `booking_agent`
--
ALTER TABLE `booking_agent`
  ADD PRIMARY KEY (`email`),
  ADD UNIQUE KEY `booking_agent_id` (`booking_agent_id`);

--
-- Indexes for table `booking_agent_works_for`
--
ALTER TABLE `booking_agent_works_for`
  ADD PRIMARY KEY (`booking_agent_email`,`airline_name`),
  ADD KEY `airline_name` (`airline_name`);

--
-- Indexes for table `customer`
--
ALTER TABLE `customer`
  ADD PRIMARY KEY (`email`);

--
-- Indexes for table `flight`
--
ALTER TABLE `flight`
  ADD PRIMARY KEY (`airline_name`,`flight_num`),
  ADD KEY `departure_airport` (`departure_airport`),
  ADD KEY `arrival_airport` (`arrival_airport`),
  ADD KEY `airplane_id` (`airplane_id`);

--
-- Indexes for table `ticket`
--
ALTER TABLE `ticket`
  ADD PRIMARY KEY (`ticket_id`),
  ADD KEY `customer_email` (`customer_email`),
  ADD KEY `airline_name` (`airline_name`,`flight_num`),
  ADD KEY `booking_agent_email` (`booking_agent_email`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `airplane`
--
ALTER TABLE `airplane`
  MODIFY `airplane_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `booking_agent`
--
ALTER TABLE `booking_agent`
  MODIFY `booking_agent_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `ticket`
--
ALTER TABLE `ticket`
  MODIFY `ticket_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `airline_staff`
--
ALTER TABLE `airline_staff`
  ADD CONSTRAINT `airline_staff_ibfk_1` FOREIGN KEY (`airline_name`) REFERENCES `airline` (`airline_name`) ON DELETE CASCADE;

--
-- Constraints for table `airline_staff_permissions`
--
ALTER TABLE `airline_staff_permissions`
  ADD CONSTRAINT `airline_staff_permissions_ibfk_1` FOREIGN KEY (`username`) REFERENCES `airline_staff` (`username`) ON DELETE CASCADE;

--
-- Constraints for table `airplane`
--
ALTER TABLE `airplane`
  ADD CONSTRAINT `airplane_ibfk_1` FOREIGN KEY (`airline_name`) REFERENCES `airline` (`airline_name`) ON DELETE CASCADE;

--
-- Constraints for table `booking_agent_works_for`
--
ALTER TABLE `booking_agent_works_for`
  ADD CONSTRAINT `booking_agent_works_for_ibfk_1` FOREIGN KEY (`booking_agent_email`) REFERENCES `booking_agent` (`email`) ON DELETE CASCADE,
  ADD CONSTRAINT `booking_agent_works_for_ibfk_2` FOREIGN KEY (`airline_name`) REFERENCES `airline` (`airline_name`) ON DELETE CASCADE;

--
-- Constraints for table `flight`
--
ALTER TABLE `flight`
  ADD CONSTRAINT `flight_ibfk_1` FOREIGN KEY (`airline_name`) REFERENCES `airline` (`airline_name`) ON DELETE CASCADE,
  ADD CONSTRAINT `flight_ibfk_2` FOREIGN KEY (`departure_airport`) REFERENCES `airport` (`airport_name`) ON DELETE CASCADE,
  ADD CONSTRAINT `flight_ibfk_3` FOREIGN KEY (`arrival_airport`) REFERENCES `airport` (`airport_name`) ON DELETE CASCADE,
  ADD CONSTRAINT `flight_ibfk_4` FOREIGN KEY (`airplane_id`) REFERENCES `airplane` (`airplane_id`) ON DELETE SET NULL;

--
-- Constraints for table `ticket`
--
ALTER TABLE `ticket`
  ADD CONSTRAINT `ticket_ibfk_1` FOREIGN KEY (`customer_email`) REFERENCES `customer` (`email`) ON DELETE CASCADE,
  ADD CONSTRAINT `ticket_ibfk_2` FOREIGN KEY (`airline_name`,`flight_num`) REFERENCES `flight` (`airline_name`, `flight_num`) ON DELETE CASCADE,
  ADD CONSTRAINT `ticket_ibfk_3` FOREIGN KEY (`booking_agent_email`) REFERENCES `booking_agent` (`email`) ON DELETE SET NULL;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
