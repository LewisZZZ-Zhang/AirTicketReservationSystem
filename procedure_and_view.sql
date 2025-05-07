-- VIEWs and Procedures for the database system. 
-- Needs to be inserted into the Db system beforehead, or the server would not be able to fetch some data properly.


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



-- Views



