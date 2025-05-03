-- 这个是一些可以直接调用的 view 和 procedure

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

CREATE PROCEDURE GetStaffAirlineName(
    IN p_username VARCHAR(50),
    OUT p_airline_name VARCHAR(50)
)
BEGIN
    SELECT airline_name INTO p_airline_name
    FROM Airline_Staff
    WHERE username = p_username;
END //

DELIMITER ;



-- Views
-- SQL Commands
-- 查看每个用户的所有机票
SELECT 
    Customer.email AS customer_email,
    Ticket.ticket_id,
    Flight.airline_name,
    Flight.flight_num,
    Flight.departure_airport,
    Flight.arrival_airport,
    Flight.departure_time,
    Flight.arrival_time,
    Flight.status,
    Flight.price
FROM Purchases
JOIN Customer ON Purchases.customer_email = Customer.email
JOIN Ticket ON Purchases.ticket_id = Ticket.ticket_id
JOIN Flight ON Ticket.airline_name = Flight.airline_name AND Ticket.flight_num = Flight.flight_num
ORDER BY Customer.email, Flight.departure_time;


-- 机票剩余
SELECT 
    a.seats - IFNULL(COUNT(p.ticket_id), 0) AS remaining_seats
FROM flight f
JOIN airplane a 
    ON f.airline_name = a.airline_name AND f.airplane_id = a.airplane_id
LEFT JOIN ticket t 
    ON f.airline_name = t.airline_name AND f.flight_num = t.flight_num
LEFT JOIN purchases p 
    ON t.ticket_id = p.ticket_id
WHERE f.airline_name = 'Emirates' AND f.flight_num = 2004
GROUP BY a.seats;

-- 每月花销
SELECT DATE_FORMAT(Purchases.purchase_date, '%%Y-%%m') AS month, SUM(Flight.price) AS monthly_spent
FROM Purchases
JOIN Ticket ON Purchases.ticket_id = Ticket.ticket_id
JOIN Flight ON Ticket.airline_name = Flight.airline_name AND Ticket.flight_num = Flight.flight_num
WHERE Purchases.customer_email = 
    AND DATE(Purchases.purchase_date) >= %s
    AND DATE(Purchases.purchase_date) <= %s
GROUP BY month
ORDER BY month

SELECT 
    DATE_FORMAT(p.purchase_date, '%Y-%m') AS month,
    SUM(f.price) AS total_spending
FROM 
    purchases p
JOIN 
    ticket t ON p.ticket_id = t.ticket_id
JOIN 
    flight f ON t.airline_name = f.airline_name AND t.flight_num = f.flight_num
WHERE 
    p.customer_email = 'tonystark@example.com'
GROUP BY 
    month
ORDER BY 
    month;


