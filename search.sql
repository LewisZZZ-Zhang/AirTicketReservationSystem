-- 这个是一些sql语句，方便快速查看一些数据
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
