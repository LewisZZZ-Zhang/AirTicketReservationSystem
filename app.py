from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
from datetime import datetime, timedelta
import uuid

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # 用于会话加密
# 每次启动时生成一个新的版本号；重启后版本号变了，所有旧 session 都会被清除
# app.config['SESSION_VERSION'] = str(uuid.uuid4())

# @app.before_request
# def invalidate_old_sessions():
#     if session.get('session_version') != app.config['SESSION_VERSION']:
#         session.clear()
#         # 将新的版本号写入 session，以后请求才会跳过清除
#         session['session_version'] = app.config['SESSION_VERSION']

# 数据库连接配置
# db_config = {
#     'host': 'localhost',
#     'user': 'root',
#     'password': '',
#     'database': 'airticketreservationsystem'
# }

# # 获取数据库连接
# def get_db_connection():
#     return mysql.connector.connect(**db_config)
from db import get_db_connection

@app.route('/')
def home():
    if 'username' in session and session['user_type'] == 'customer':
        # 获取当前登录用户的 email
        customer_email = session['username']

        # 查询该顾客的机票信息
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT 
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
            JOIN Ticket ON Purchases.ticket_id = Ticket.ticket_id
            JOIN Flight ON Ticket.airline_name = Flight.airline_name AND Ticket.flight_num = Flight.flight_num
            WHERE Purchases.customer_email = %s and Flight.status = 'Upcoming'
        """, (customer_email,))
        tickets = cursor.fetchall()
        cursor.close()
        conn.close()

        # 渲染主页并显示机票信息
        return render_template('index.html', tickets=tickets)

    # 如果用户未登录或不是顾客，显示默认主页
    return render_template('index.html', tickets=None)

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/login/customer', methods=['GET', 'POST'])
def login_customer():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT * FROM Customer 
            WHERE email = %s AND password = MD5(%s)
        """, (email, password))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user:
            session['username'] = email
            session['user_type'] = 'customer'
            flash('Customer login successful!')
            return redirect(url_for('home'))
        else:
            flash('Invalid login credentials.')
            return redirect(url_for('login_customer'))

    return render_template('login_customer.html')


@app.route('/login/agent', methods=['GET', 'POST'])
def login_agent():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT * FROM Booking_Agent
            WHERE email = %s AND password = MD5(%s)
        """, (email, password))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user: 
            session['username'] = email
            session['user_type'] = 'agent'
            flash('Booking Agent login successful!')
            return redirect(url_for('agent_home'))
        else:
            flash('Invalid login credentials.')
            return redirect(url_for('login_agent'))

    return render_template('login_agent.html')


@app.route('/login/staff', methods=['GET', 'POST'])
def login_staff():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT * FROM Airline_Staff 
            WHERE username = %s AND password = MD5(%s)
        """, (username, password))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user: 
            session['username'] = username
            session['user_type'] = 'staff'
            flash('Airline Staff login successful!')
            return redirect(url_for('staff_home'))
        else:
            flash('Invalid login credentials.')
            return redirect(url_for('login_staff'))

    return render_template('login_staff.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/register/agent', methods=['GET', 'POST'])
def register_agent():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        booking_agent_id = request.form['booking_agent_id']

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO Booking_Agent (email, password, booking_agent_id)
                VALUES (%s, MD5(%s), %s)
            """, (email, password, booking_agent_id))

            conn.commit()
            flash('Booking Agent registered successfully!')
            return redirect(url_for('login'))
        except mysql.connector.Error as err:
            flash(f"Error: {err}")
        finally:
            cursor.close()
            conn.close()

    return render_template('register_agent.html')


@app.route('/register/staff', methods=['GET', 'POST'])
def register_staff():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        date_of_birth = request.form['date_of_birth']
        airline_name = request.form['airline_name']

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO Airline_Staff (username, password, first_name, last_name, date_of_birth, airline_name)
                VALUES (%s, MD5(%s), %s, %s, %s, %s)
            """, (username, password, first_name, last_name, date_of_birth, airline_name))

            conn.commit()
            flash('Airline Staff registered successfully!')
            return redirect(url_for('login'))
        except mysql.connector.Error as err:
            flash(f"Error: {err}")
        finally:
            cursor.close()
            conn.close()

    return render_template('register_staff.html')

@app.route('/register/customer', methods=['GET', 'POST'])
def register_customer():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        dob = request.form['date_of_birth']
        passport_number = request.form['passport_number']
        passport_expiration = request.form['passport_expiration']
        passport_country = request.form['passport_country']
        building_number = request.form['building_number']
        street = request.form['street']
        city = request.form['city']
        state = request.form['state']
        phone_number = request.form['phone_number']

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO Customer (
                    name, email, password, date_of_birth, building_number,
                    street, city, state, phone_number, passport_number,
                    passport_expiration, passport_country
                )
                VALUES (%s, %s,MD5(%s), %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (name, email, password, dob, building_number, street, city, state,
                  phone_number, passport_number, passport_expiration, passport_country))

            conn.commit()
            flash('Customer registered successfully!')
            return redirect(url_for('login'))
        except mysql.connector.Error as err:
            flash(f"Error: {err}")
        finally:
            cursor.close()
            conn.close()

    return render_template('register_customer.html')

# @app.route('/logout')
# def logout():
#     session.clear()
#     flash('Logged out successfully!')
#     return redirect(url_for('home'))


@app.route('/search_flights', methods=['GET','POST'])
def search_flights():
    if request.method == 'GET':
        # 如果是 GET 请求，直接渲染搜索页面
        return render_template('search_flights.html', flights=None, from_location='', to_location='', date='')

    from_location = request.form.get('from_location', '').strip()
    to_location = request.form.get('to_location', '').strip()
    date = request.form.get('date', '').strip()
    # print(from_location,to_location,date)

    query = "SELECT * FROM Flight WHERE 1=1"  # 基础查询
    params = []

    # 动态添加查询条件
    if from_location:
        query += " AND departure_airport = %s"
        params.append(from_location)
    if to_location:
        query += " AND arrival_airport = %s"
        params.append(to_location)
    if date:
        query += " AND DATE(departure_time) = %s"
        params.append(date)

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query, params)  # 动态查询
    flights = cursor.fetchall()
    cursor.close()
    conn.close()
    # print("result:",flights)
    return render_template('search_flights.html', flights=flights, from_location=from_location, to_location=to_location, date=date)

# @app.route('/purchase_ticket', methods=['POST'])
# def purchase_ticket():
#     if 'username' not in session or session['user_type'] != 'customer':
#         flash('Please log in to purchase tickets.')
#         return redirect(url_for('login'))

#     customer_email = session['username']
#     airline_name = request.form['airline_name']
#     flight_num = request.form['flight_num']

#     conn = get_db_connection()
#     cursor = conn.cursor()

#     try:
#         # 检查是否还有可用票
#         cursor.execute("""
#             SELECT 
#                 a.seats - IFNULL(COUNT(p.ticket_id), 0) AS remaining_seats
#             FROM flight f
#             JOIN airplane a 
#                 ON f.airline_name = a.airline_name AND f.airplane_id = a.airplane_id
#             LEFT JOIN ticket t 
#                 ON f.airline_name = t.airline_name AND f.flight_num = t.flight_num
#             LEFT JOIN purchases p 
#                 ON t.ticket_id = p.ticket_id
#             WHERE f.airline_name = %s AND f.flight_num = %s
#             GROUP BY a.seats;
#         """, (airline_name, flight_num))
#         result = cursor.fetchone()
#         # print(flight_num, result)
#         if result and result[0] > 0:
#             print("OK to purchase")
#             cursor.execute("SELECT MAX(ticket_id) FROM ticket")
#             max_id = cursor.fetchone()[0] or 0
#             new_ticket_id = max_id + 1

#             # 插入新的 ticket
#             cursor.execute("""
#                 INSERT INTO ticket (ticket_id, airline_name, flight_num)
#                 VALUES (%s, %s, %s)
#             """, (new_ticket_id, airline_name, flight_num))

#             # 插入购票记录
#             cursor.execute("""
#                 INSERT INTO Purchases (ticket_id, customer_email, purchase_date)
#                 VALUES (%s, %s, %s)
#             """, (new_ticket_id, customer_email, datetime.now().strftime('%Y-%m-%d')))
#             conn.commit()
#             flash('Ticket purchased successfully!')
#         else:
#             flash('No available tickets for this flight. **Error1**')
#     except mysql.connector.Error as err:
#         flash(f"Error: {err}")
#     finally:
#         cursor.close()
#         conn.close()

#     return redirect(url_for('search_flights'))

# DELIMITER //
# CREATE PROCEDURE PurchaseTicket(
#     IN p_airline_name VARCHAR(255),
#     IN p_flight_num VARCHAR(255),
#     IN p_customer_email VARCHAR(255),
#     OUT p_result VARCHAR(255)
# )
# BEGIN
#     DECLARE remaining INT DEFAULT 0;
#     DECLARE new_ticket_id INT DEFAULT 0;
#     SELECT a.seats - IFNULL(COUNT(p.ticket_id), 0)
#       INTO remaining
#       FROM Flight f
#       JOIN Airplane a ON f.airline_name = a.airline_name AND f.airplane_id = a.airplane_id
#       LEFT JOIN Ticket t ON f.airline_name = t.airline_name AND f.flight_num = t.flight_num
#       LEFT JOIN Purchases p ON t.ticket_id = p.ticket_id
#      WHERE f.airline_name = p_airline_name AND f.flight_num = p_flight_num
#      GROUP BY a.seats;

#     IF remaining > 0 THEN
#         SELECT IFNULL(MAX(ticket_id), 0) + 1 INTO new_ticket_id FROM Ticket;
#         INSERT INTO Ticket(ticket_id, airline_name, flight_num)
#         VALUES (new_ticket_id, p_airline_name, p_flight_num);
#         INSERT INTO Purchases(ticket_id, customer_email, purchase_date)
#         VALUES (new_ticket_id, p_customer_email, CURDATE());
#         SET p_result = 'success';
#     ELSE
#         SET p_result = 'no_ticket';
#     END IF;
# END //
# DELIMITER ;

@app.route('/purchase_ticket', methods=['POST'])
def purchase_ticket():
    if 'username' not in session or session['user_type'] != 'customer':
        flash('Please log in to purchase tickets.')
        return redirect(url_for('login'))

    customer_email = session['username']
    airline_name = request.form['airline_name']
    flight_num = request.form['flight_num']

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # 调用存储过程
        result = ""
        args = (airline_name, flight_num, customer_email, result)
        result_args = cursor.callproc('PurchaseTicket', args)
        # 存储过程的OUT参数在result_args的最后一个
        purchase_result = result_args[-1]

        if purchase_result == 'success':
            flash('Ticket purchased successfully!')
        elif purchase_result == 'no_ticket':
            flash('No available tickets for this flight.')
        else:
            flash('Unknown error occurred.')
        conn.commit()
    except mysql.connector.Error as err:
        flash(f"Error: {err}")
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('search_flights'))

@app.route('/check_status', methods=['GET','POST'])
def check_status():
    if request.method == 'GET':
        # 如果是 GET 请求，直接渲染搜索页面
        return render_template('check_status.html', flights=None, from_location='', to_location='', date='')
    flight_num = request.form.get('flight_num', '').strip()
    departure_date = request.form.get('departure_date', '').strip()
    arrival_date = request.form.get('arrival_date', '').strip()

    query = "SELECT * FROM Flight WHERE 1=1"  # 基础查询
    params = []

    # 动态添加查询条件
    if flight_num:
        query += " AND flight_num = %s"
        params.append(flight_num)
    if departure_date:
        query += " AND DATE(departure_time) = %s"
        params.append(departure_date)
    if arrival_date:
        query += " AND DATE(arrival_time) = %s"
        params.append(arrival_date)

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query, params)  # 动态查询
    status_results = cursor.fetchall()
    cursor.close()
    conn.close()

    # if status_results:
    #     flash(f"Found {len(status_results)} flight(s) matching your criteria.")
    # else:
    #     flash("No flights found matching your criteria.")

    return render_template(
        'check_status.html',
        status_results=status_results,
        flight_num=flight_num,
        departure_date=departure_date,
        arrival_date=arrival_date
    )



@app.route('/view_all_tickets', methods=['GET', 'POST'])
def view_all_tickets():
    if 'username' not in session or session['user_type'] != 'customer':
        flash('Please log in as a customer to view your tickets.')
        return redirect(url_for('login_customer'))

    customer_email = session['username']
    start_date = request.form.get('start_date', '').strip()
    end_date = request.form.get('end_date', '').strip()
    from_location = request.form.get('from_location', '').strip()
    to_location = request.form.get('to_location', '').strip()

    query = """
        SELECT 
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
        JOIN Ticket ON Purchases.ticket_id = Ticket.ticket_id
        JOIN Flight ON Ticket.airline_name = Flight.airline_name AND Ticket.flight_num = Flight.flight_num
        WHERE Purchases.customer_email = %s
    """
    params = [customer_email]

    # 动态添加筛选条件
    if start_date:
        query += " AND DATE(Flight.departure_time) >= %s"
        params.append(start_date)
    if end_date:
        query += " AND DATE(Flight.departure_time) <= %s"
        params.append(end_date)
    if from_location:
        query += " AND (Flight.departure_airport = %s OR Flight.departure_city = %s)"
        params.extend([from_location, from_location])
    if to_location:
        query += " AND (Flight.arrival_airport = %s OR Flight.arrival_city = %s)"
        params.extend([to_location, to_location])

    # 默认按 status 排序
    query += """
        ORDER BY 
            FIELD(Flight.status, 'Upcoming', 'Delayed', 'In progress'),
            Flight.departure_time
    """

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query, params)
    tickets = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('all_tickets.html', tickets=tickets)

# ...existing code...

# ...existing code...

@app.route('/user_home', methods=['GET', 'POST'])
def user_home():
    if 'username' not in session or session['user_type'] != 'customer':
        flash('Please log in as a customer to view your dashboard.')
        return redirect(url_for('login_customer'))

    customer_email = session['username']

    today = datetime.today()
    default_start = (today - timedelta(days=180)).replace(day=1)
    default_end = today

    # 获取用户选择的起止年月
    start_month = request.form.get('start_month')
    end_month = request.form.get('end_month')

    if start_month:
        start_date = datetime.strptime(start_month, '%Y-%m')
    else:
        start_date = default_start

    if end_month:
        end_date = datetime.strptime(end_month, '%Y-%m')
        next_month = (end_date.replace(day=28) + timedelta(days=4)).replace(day=1)
        end_date = next_month - timedelta(days=1)
    else:
        end_date = default_end

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # 查询半年内总花销
    cursor.execute("""
        SELECT SUM(Flight.price) AS total_spent
        FROM Purchases
        JOIN Ticket ON Purchases.ticket_id = Ticket.ticket_id
        JOIN Flight ON Ticket.airline_name = Flight.airline_name AND Ticket.flight_num = Flight.flight_num
        WHERE Purchases.customer_email = %s
          AND DATE(Purchases.purchase_date) >= %s
          AND DATE(Purchases.purchase_date) <= %s
    """, (customer_email, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))
    total_spent = cursor.fetchone()['total_spent'] or 0

    # 查询去年总花销
    last_year_start = (today - timedelta(days=365)).strftime('%Y-%m-%d')
    last_year_end = today.strftime('%Y-%m-%d')
    cursor.execute("""
        SELECT SUM(Flight.price) AS last_year_spent
        FROM Purchases
        JOIN Ticket ON Purchases.ticket_id = Ticket.ticket_id
        JOIN Flight ON Ticket.airline_name = Flight.airline_name AND Ticket.flight_num = Flight.flight_num
        WHERE Purchases.customer_email = %s
          AND DATE(Purchases.purchase_date) >= %s
          AND DATE(Purchases.purchase_date) <= %s
    """, (customer_email, last_year_start, last_year_end))
    last_year_spent = cursor.fetchone()['last_year_spent'] or 0

    # 查询最近半年总花销
    last_half_year_start = (today - timedelta(days=180)).strftime('%Y-%m-%d')
    last_half_year_end = today.strftime('%Y-%m-%d')
    cursor.execute("""
        SELECT SUM(Flight.price) AS last_half_year_spent
        FROM Purchases
        JOIN Ticket ON Purchases.ticket_id = Ticket.ticket_id
        JOIN Flight ON Ticket.airline_name = Flight.airline_name AND Ticket.flight_num = Flight.flight_num
        WHERE Purchases.customer_email = %s
          AND DATE(Purchases.purchase_date) >= %s
          AND DATE(Purchases.purchase_date) <= %s
    """, (customer_email, last_half_year_start, last_half_year_end))
    last_half_year_spent = cursor.fetchone()['last_half_year_spent'] or 0

    # 查询每月花销
    cursor.execute("""
        SELECT DATE_FORMAT(Purchases.purchase_date, '%Y-%m') AS month, SUM(Flight.price) AS monthly_spent
        FROM Purchases
        JOIN Ticket ON Purchases.ticket_id = Ticket.ticket_id
        JOIN Flight ON Ticket.airline_name = Flight.airline_name AND Ticket.flight_num = Flight.flight_num
        WHERE Purchases.customer_email = %s
            AND DATE(Purchases.purchase_date) >= %s
            AND DATE(Purchases.purchase_date) <= %s
        GROUP BY month
        ORDER BY month
    """, (customer_email, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))
    monthly_data = cursor.fetchall()
    cursor.close()
    conn.close()

    # 构造柱状图数据
    months = []
    monthly_spent = []
    current = start_date
    while current <= end_date:
        m = current.strftime('%Y-%m')
        months.append(m)
        found = next((item['monthly_spent'] for item in monthly_data if item['month'] == m), 0)
        monthly_spent.append(float(found) if found else 0)
        if current.month == 12:
            current = current.replace(year=current.year+1, month=1)
        else:
            current = current.replace(month=current.month+1)

    return render_template(
        'user_home.html',
        total_spent=total_spent,
        last_year_spent=last_year_spent,
        last_half_year_spent=last_half_year_spent,
        months=months,
        monthly_spent=monthly_spent,
        start_month=start_date.strftime('%Y-%m'),
        end_month=end_date.strftime('%Y-%m')
    )
# ...existing code...

@app.route('/staff/staff_home')
def staff_home():
    if 'username' not in session or session['user_type'] != 'staff':
        flash('Please log in as airline staff to view this page.')
        return redirect(url_for('login_staff'))
    return render_template('staff_home.html')

# ...existing code...
@app.route('/staff/view_my_flights', methods=['GET', 'POST'])
def view_my_flights():
    if 'username' not in session or session['user_type'] != 'staff':
        flash('Please log in as airline staff to view flights.')
        return redirect(url_for('login_staff'))

    username = session['username']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    # 获取员工所属航空公司
    cursor.execute("SELECT airline_name FROM Airline_Staff WHERE username = %s", (username,))
    staff = cursor.fetchone()
    if not staff:
        flash('Staff not found.')
        cursor.close()
        conn.close()
        return redirect(url_for('staff_home'))
    airline_name = staff['airline_name']

    # 默认时间范围：未来30天
    today = datetime.today().date()
    default_start = today
    default_end = today + timedelta(days=30)

    # 获取筛选条件
    start_date = request.form.get('start_date', default_start.strftime('%Y-%m-%d'))
    end_date = request.form.get('end_date', default_end.strftime('%Y-%m-%d'))
    from_location = request.form.get('from_location', '').strip()
    to_location = request.form.get('to_location', '').strip()
    selected_flight_num = request.form.get('selected_flight_num', '').strip()

    query = """
        SELECT 
            Flight.airline_name, Flight.flight_num, Flight.departure_airport, 
            Flight.arrival_airport, Flight.departure_time, Flight.arrival_time, 
            Flight.status, Flight.price
        FROM Flight
        WHERE Flight.airline_name = %s
          AND DATE(Flight.departure_time) >= %s
          AND DATE(Flight.departure_time) <= %s
    """
    params = [airline_name, start_date, end_date]

    if from_location:
        query += " AND (Flight.departure_airport = %s OR Flight.departure_airport IN (SELECT airport_name FROM Airport WHERE airport_city = %s))"
        params.extend([from_location, from_location])
    if to_location:
        query += " AND (Flight.arrival_airport = %s OR Flight.arrival_airport IN (SELECT airport_name FROM Airport WHERE airport_city = %s))"
        params.extend([to_location, to_location])

    query += " ORDER BY Flight.departure_time"

    cursor.execute(query, params)
    flights = cursor.fetchall()

    # 如果选择了某个航班，查询该航班所有乘客
    customers = []
    if selected_flight_num:
        cursor.execute("""
            SELECT DISTINCT Customer.email, Customer.name
            FROM Ticket
            JOIN Purchases ON Ticket.ticket_id = Purchases.ticket_id
            JOIN Customer ON Purchases.customer_email = Customer.email
            WHERE Ticket.airline_name = %s AND Ticket.flight_num = %s
        """, (airline_name, selected_flight_num))
        customers = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        'staff_view_my_flights.html',
        flights=flights,
        start_date=start_date,
        end_date=end_date,
        from_location=from_location,
        to_location=to_location,
        selected_flight_num=selected_flight_num,
        customers=customers
    )


@app.route('/staff/create_flight', methods=['GET', 'POST'])
def create_flight():
    if 'username' not in session or session['user_type'] != 'staff':
        flash('You are not authorized to create flights. ERROR 1')
        return redirect(url_for('login_staff'))

    username = session['username']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Verify if the user is an airline staff
    cursor.execute("SELECT airline_name FROM Airline_Staff WHERE username = %s", (username,))
    staff = cursor.fetchone()
    if not staff:
        flash('You are not authorized to create flights. ERROR 2')
        cursor.close()
        conn.close()
        return redirect(url_for('staff_home'))

    airline_name = staff['airline_name']

    cursor.execute("SELECT 1 FROM Permission WHERE username = %s AND permission_type = 'admin'", (username,))
    if not cursor.fetchone():
        flash('You do not have admin permission to create flights.')
        cursor.close()
        conn.close()
        return redirect(url_for('staff_home'))

    if request.method == 'POST':
        # Get flight details from the form
        flight_num = request.form['flight_num']
        departure_airport = request.form['departure_airport']
        departure_time = request.form['departure_time']
        arrival_airport = request.form['arrival_airport']
        arrival_time = request.form['arrival_time']
        price = request.form['price']
        airplane_id = request.form['airplane_id']
        
        # Validate input data
        if not all([flight_num, departure_airport, departure_time, arrival_airport, arrival_time, price, airplane_id]):
            flash('All fields are required.')
            cursor.close()
            conn.close()
            return redirect(url_for('create_flight'))

            # Check if departure time is earlier than arrival time
        if datetime.fromisoformat(departure_time) >= datetime.fromisoformat(arrival_time):
            flash('Departure time must be earlier than arrival time.')
            cursor.close()
            conn.close()
            return redirect(url_for('create_flight'))

        # Check if departure and arrival airports exist
        cursor.execute("SELECT 1 FROM Airport WHERE airport_name = %s", (departure_airport,))
        if not cursor.fetchone():
            flash(f"Departure airport '{departure_airport}' does not exist.")
            cursor.close()
            conn.close()
            return redirect(url_for('create_flight'))

        cursor.execute("SELECT 1 FROM Airport WHERE airport_name = %s", (arrival_airport,))
        if not cursor.fetchone():
            flash(f"Arrival airport '{arrival_airport}' does not exist.")
            cursor.close()
            conn.close()
            return redirect(url_for('create_flight'))

        # Check if airplane exists and belongs to the airline
        cursor.execute("""
            SELECT 1 FROM Airplane 
            WHERE airplane_id = %s AND airline_name = %s
        """, (airplane_id, airline_name))
        if not cursor.fetchone():
            flash(f"Airplane ID '{airplane_id}' does not exist or does not belong to your airline.")
            cursor.close()
            conn.close()
            return redirect(url_for('create_flight'))

        try:
            # Insert the new flight into the database
            cursor.execute("""
                INSERT INTO Flight (airline_name, flight_num, departure_airport, departure_time, 
                                    arrival_airport, arrival_time, price, airplane_id, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'Upcoming')
            """, (airline_name, flight_num, departure_airport, departure_time, 
                  arrival_airport, arrival_time, price, airplane_id))
            conn.commit()
            flash('Flight created successfully!')
            return redirect(url_for('staff_home'))
        except mysql.connector.Error as err:
            flash(f"Error: {err}")
        finally:
            cursor.close()
            conn.close()

    cursor.close()
    conn.close()
    return render_template('staff_create_new_flight.html', airline_name=airline_name)

@app.route('/staff/change_flight_status', methods=['GET', 'POST'])
def change_flight_status():
    # 权限检查：必须为staff且有Operator权限
    if 'username' not in session or session['user_type'] != 'staff':
        flash('Please log in as airline staff to change flight status.')
        return redirect(url_for('login_staff'))

    username = session['username']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # 检查是否有Operator权限
    cursor.execute(
        "SELECT 1 FROM Permission WHERE username = %s AND permission_type = 'Operator'",
        (username,)
    )
    has_operator = cursor.fetchone()
    if not has_operator:
        cursor.close()
        conn.close()
        flash('You do not have permission to change flight status.')
        return redirect(url_for('staff_home'))

    # 获取该员工所属航空公司
    cursor.execute("SELECT airline_name FROM Airline_Staff WHERE username = %s", (username,))
    staff = cursor.fetchone()
    if not staff:
        cursor.close()
        conn.close()
        flash('Staff not found.')
        return redirect(url_for('staff_home'))
    airline_name = staff['airline_name']

    # 处理表单提交
    if request.method == 'POST':
        flight_num = request.form.get('flight_num')
        new_status = request.form.get('new_status')
        # 检查航班是否属于该航空公司
        cursor.execute(
            "SELECT status FROM Flight WHERE airline_name = %s AND flight_num = %s",
            (airline_name, flight_num)
        )
        flight = cursor.fetchone()
        if not flight:
            flash('Flight not found or does not belong to your airline.')
        elif new_status not in ['Upcoming', 'In Progress', 'Delayed']:
            flash('Invalid status.')
        else:
            try:
                cursor.execute(
                    "UPDATE Flight SET status = %s WHERE airline_name = %s AND flight_num = %s",
                    (new_status, airline_name, flight_num)
                )
                conn.commit()
                flash('Flight status updated successfully!')
            except mysql.connector.Error as err:
                flash(f"Error: {err}")

    # 查询该航空公司所有航班
    cursor.execute(
        "SELECT flight_num, departure_airport, arrival_airport, departure_time, arrival_time, status FROM Flight WHERE airline_name = %s ORDER BY departure_time DESC",
        (airline_name,)
    )
    flights = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('staff_change_flight_status.html', airline_name=airline_name, flights=flights)

@app.route('/staff/add_airplane', methods=['GET', 'POST'])
def add_airplane():
    # 权限检查：必须为staff且有Admin权限
    if 'username' not in session or session['user_type'] != 'staff':
        flash('Please log in as airline staff to add airplanes.')
        return redirect(url_for('login_staff'))

    username = session['username']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # 检查是否有Admin权限
    cursor.execute(
        "SELECT 1 FROM Permission WHERE username = %s AND permission_type = 'Admin'",
        (username,)
    )
    has_admin = cursor.fetchone()
    if not has_admin:
        cursor.close()
        conn.close()
        flash('You do not have permission to add airplanes.')
        return redirect(url_for('staff_home'))

    # 获取该员工所属航空公司
    cursor.execute("SELECT airline_name FROM Airline_Staff WHERE username = %s", (username,))
    staff = cursor.fetchone()
    if not staff:
        cursor.close()
        conn.close()
        flash('Staff not found.')
        return redirect(url_for('staff_home'))
    airline_name = staff['airline_name']

    # 处理表单提交
    if request.method == 'POST':
        airplane_id = request.form.get('airplane_id')
        seats = request.form.get('seats')
        try:
            cursor.execute(
                "INSERT INTO Airplane (airline_name, airplane_id, seats) VALUES (%s, %s, %s)",
                (airline_name, airplane_id, seats)
            )
            conn.commit()
            flash('Airplane added successfully!')
        except mysql.connector.Error as err:
            flash(f"Error: {err}")

    # 查询该航空公司所有飞机
    cursor.execute(
        "SELECT airplane_id, seats FROM Airplane WHERE airline_name = %s ORDER BY airplane_id",
        (airline_name,)
    )
    airplanes = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('staff_add_airplane.html', airline_name=airline_name, airplanes=airplanes)

@app.route('/staff/add_airport', methods=['GET', 'POST'])
def add_airport():
    # 权限检查：必须为staff且有Admin权限
    if 'username' not in session or session['user_type'] != 'staff':
        flash('Please log in as airline staff to add airports.')
        return redirect(url_for('login_staff'))

    username = session['username']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # 检查是否有Admin权限
    cursor.execute(
        "SELECT 1 FROM Permission WHERE username = %s AND permission_type = 'Admin'",
        (username,)
    )
    has_admin = cursor.fetchone()
    if not has_admin:
        cursor.close()
        conn.close()
        flash('You do not have permission to add airports.')
        return redirect(url_for('staff_home'))

    # 获取该员工所属航空公司
    cursor.execute("SELECT airline_name FROM Airline_Staff WHERE username = %s", (username,))
    staff = cursor.fetchone()
    if not staff:
        cursor.close()
        conn.close()
        flash('Staff not found.')
        return redirect(url_for('staff_home'))
    airline_name = staff['airline_name']

    if request.method == 'POST':
        airport_name = request.form.get('airport_name', '').strip()
        airport_city = request.form.get('airport_city', '').strip()
        if not airport_name or not airport_city:
            flash('Airport name and city are required.')
        else:
            try:
                cursor.execute(
                    "INSERT INTO Airport (airport_name, airport_city) VALUES (%s, %s)",
                    (airport_name, airport_city)
                )
                conn.commit()
                flash(f"Airport '{airport_name}' added successfully!")
            except mysql.connector.Error as err:
                flash(f"Error: {err}")

    # 查询所有机场，方便展示
    cursor.execute("SELECT airport_name, airport_city FROM Airport ORDER BY airport_name")
    airports = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template(
        'staff_add_airport.html',
        airline_name=airline_name,
        airports=airports
    )

@app.route('/staff/view_booking_agents', methods=['GET', 'POST'])
def staff_view_booking_agents():
    if 'username' not in session or session['user_type'] != 'staff':
        flash('Please log in as airline staff to view this page.')
        return redirect(url_for('login_staff'))

    username = session['username']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # 获取staff所属航空公司
    cursor.execute("SELECT airline_name FROM Airline_Staff WHERE username = %s", (username,))
    staff = cursor.fetchone()
    if not staff:
        flash('Staff not found.')
        cursor.close()
        conn.close()
        return redirect(url_for('staff_home'))
    airline_name = staff['airline_name']

    # Top 5 agents by ticket sales (past month)
    cursor.execute("""
        SELECT ba.email, COUNT(*) AS tickets_sold
        FROM Booking_Agent ba
        JOIN Booking_Agent_Work_For bawf ON ba.email = bawf.email
        JOIN Purchases p ON ba.booking_agent_id = p.booking_agent_id
        JOIN Ticket t ON p.ticket_id = t.ticket_id
        WHERE bawf.airline_name = %s
          AND t.airline_name = %s
          AND p.purchase_date >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH)
        GROUP BY ba.email
        ORDER BY tickets_sold DESC
        LIMIT 5
    """, (airline_name, airline_name))
    top_agents_month = cursor.fetchall()

    # Top 5 agents by ticket sales (past year)
    cursor.execute("""
        SELECT ba.email, COUNT(*) AS tickets_sold
        FROM Booking_Agent ba
        JOIN Booking_Agent_Work_For bawf ON ba.email = bawf.email
        JOIN Purchases p ON ba.booking_agent_id = p.booking_agent_id
        JOIN Ticket t ON p.ticket_id = t.ticket_id
        WHERE bawf.airline_name = %s
          AND t.airline_name = %s
          AND p.purchase_date >= DATE_SUB(CURDATE(), INTERVAL 1 YEAR)
        GROUP BY ba.email
        ORDER BY tickets_sold DESC
        LIMIT 5
    """, (airline_name, airline_name))
    top_agents_year = cursor.fetchall()

    # Top 5 agents by commission (past year)
    cursor.execute("""
        SELECT ba.email, SUM(f.price * 0.1) AS total_commission
        FROM Booking_Agent ba
        JOIN Booking_Agent_Work_For bawf ON ba.email = bawf.email
        JOIN Purchases p ON ba.booking_agent_id = p.booking_agent_id
        JOIN Ticket t ON p.ticket_id = t.ticket_id
        JOIN Flight f ON t.airline_name = f.airline_name AND t.flight_num = f.flight_num
        WHERE bawf.airline_name = %s
          AND f.airline_name = %s
          AND p.purchase_date >= DATE_SUB(CURDATE(), INTERVAL 1 YEAR)
        GROUP BY ba.email
        ORDER BY total_commission DESC
        LIMIT 5
    """, (airline_name, airline_name))
    top_agents_commission = cursor.fetchall()

    # All agents for this airline, with sorting
    sort_by = request.args.get('sort_by', 'email')
    order = request.args.get('order', 'asc')
    if sort_by not in ['email', 'tickets_sold', 'total_commission']:
        sort_by = 'email'
    if order not in ['asc', 'desc']:
        order = 'asc'

    cursor.execute(f"""
        SELECT ba.email,
            COUNT(p.ticket_id) AS tickets_sold,
            IFNULL(SUM(f.price * 0.1), 0) AS total_commission
        FROM Booking_Agent ba
        JOIN Booking_Agent_Work_For bawf ON ba.email = bawf.email
        LEFT JOIN Purchases p ON ba.booking_agent_id = p.booking_agent_id
        LEFT JOIN Ticket t ON p.ticket_id = t.ticket_id AND t.airline_name = %s
        LEFT JOIN Flight f ON t.airline_name = f.airline_name AND t.flight_num = f.flight_num
        WHERE bawf.airline_name = %s
        GROUP BY ba.email
        ORDER BY {sort_by} {order.upper()}
    """, (airline_name, airline_name))
    all_agents = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        'staff_view_booking_agents.html',
        top_agents_month=top_agents_month,
        top_agents_year=top_agents_year,
        top_agents_commission=top_agents_commission,
        all_agents=all_agents,
        sort_by=sort_by,
        order=order
    )



@app.route('/staff/view_frequent_customers', methods=['GET', 'POST'])
def staff_view_frequent_customers():
    if 'username' not in session or session['user_type'] != 'staff':
        flash('Please log in as airline staff to view this page.')
        return redirect(url_for('login_staff'))

    username = session['username']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # 获取staff所属航空公司
    cursor.execute("SELECT airline_name FROM Airline_Staff WHERE username = %s", (username,))
    staff = cursor.fetchone()
    if not staff:
        flash('Staff not found.')
        cursor.close()
        conn.close()
        return redirect(url_for('staff_home'))
    airline_name = staff['airline_name']

    # 查询过去一年内最常乘坐该航空公司航班的客户
    cursor.execute("""
        SELECT c.email, c.name, COUNT(*) AS flight_count
        FROM Purchases p
        JOIN Ticket t ON p.ticket_id = t.ticket_id
        JOIN Customer c ON p.customer_email = c.email
        WHERE t.airline_name = %s
          AND p.purchase_date >= DATE_SUB(CURDATE(), INTERVAL 1 YEAR)
        GROUP BY c.email, c.name
        ORDER BY flight_count DESC
        LIMIT 1
    """, (airline_name,))
    most_frequent = cursor.fetchone()

    # 如果选择了某个客户，显示其所有航班
    customer_email = request.form.get('customer_email', '') if request.method == 'POST' else ''
    customer_flights = []
    if customer_email:
        cursor.execute("""
            SELECT f.flight_num, f.departure_airport, f.arrival_airport, f.departure_time, f.arrival_time, f.status
            FROM Purchases p
            JOIN Ticket t ON p.ticket_id = t.ticket_id
            JOIN Flight f ON t.airline_name = f.airline_name AND t.flight_num = f.flight_num
            WHERE t.airline_name = %s AND p.customer_email = %s
            ORDER BY f.departure_time DESC
        """, (airline_name, customer_email))
        customer_flights = cursor.fetchall()

    # 也可以列出所有过去一年乘坐过该航司的客户，供选择
    cursor.execute("""
        SELECT DISTINCT c.email, c.name
        FROM Purchases p
        JOIN Ticket t ON p.ticket_id = t.ticket_id
        JOIN Customer c ON p.customer_email = c.email
        WHERE t.airline_name = %s
          AND p.purchase_date >= DATE_SUB(CURDATE(), INTERVAL 1 YEAR)
        ORDER BY c.name
    """, (airline_name,))
    all_customers = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        'staff_view_frequent_customers.html',
        most_frequent=most_frequent,
        all_customers=all_customers,
        customer_email=customer_email,
        customer_flights=customer_flights
    )


@app.route('/staff/view_reports', methods=['GET', 'POST'])
def staff_view_reports():
    if 'username' not in session or session['user_type'] != 'staff':
        flash('Please log in as airline staff to view reports.')
        return redirect(url_for('login_staff'))

    username = session['username']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # 获取staff所属航空公司
    cursor.execute("SELECT airline_name FROM Airline_Staff WHERE username = %s", (username,))
    staff = cursor.fetchone()
    if not staff:
        flash('Staff not found.')
        cursor.close()
        conn.close()
        return redirect(url_for('staff_home'))
    airline_name = staff['airline_name']

    # 获取筛选条件
    today = datetime.today()
    default_start = (today - timedelta(days=30)).strftime('%Y-%m-%d')
    default_end = today.strftime('%Y-%m-%d')
    start_date = request.form.get('start_date', default_start)
    end_date = request.form.get('end_date', default_end)

    # 总票数（自定义区间）
    cursor.execute("""
        SELECT COUNT(*) AS total_tickets
        FROM Purchases
        JOIN Ticket ON Purchases.ticket_id = Ticket.ticket_id
        WHERE Ticket.airline_name = %s
          AND DATE(Purchases.purchase_date) BETWEEN %s AND %s
    """, (airline_name, start_date, end_date))
    total_tickets = cursor.fetchone()['total_tickets']

    # 上月票数
    cursor.execute("""
        SELECT COUNT(*) AS last_month_tickets
        FROM Purchases
        JOIN Ticket ON Purchases.ticket_id = Ticket.ticket_id
        WHERE Ticket.airline_name = %s
          AND Purchases.purchase_date >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH)
    """, (airline_name,))
    last_month_tickets = cursor.fetchone()['last_month_tickets']

    # 上年票数
    cursor.execute("""
        SELECT COUNT(*) AS last_year_tickets
        FROM Purchases
        JOIN Ticket ON Purchases.ticket_id = Ticket.ticket_id
        WHERE Ticket.airline_name = %s
          AND Purchases.purchase_date >= DATE_SUB(CURDATE(), INTERVAL 1 YEAR)
    """, (airline_name,))
    last_year_tickets = cursor.fetchone()['last_year_tickets']

    # 按月统计自定义区间每月票数
    cursor.execute("""
        SELECT DATE_FORMAT(Purchases.purchase_date, '%Y-%m') AS month, COUNT(*) AS tickets_sold
        FROM Purchases
        JOIN Ticket ON Purchases.ticket_id = Ticket.ticket_id
        WHERE Ticket.airline_name = %s
          AND Purchases.purchase_date BETWEEN %s AND %s
        GROUP BY month
        ORDER BY month
    """, (airline_name, start_date, end_date))
    monthly_data = cursor.fetchall()

    cursor.close()
    conn.close()

    # 构造柱状图数据（补全所有月份）
    months = []
    tickets_per_month = []
    # 计算起止月
    start = datetime.strptime(start_date, '%Y-%m-%d').replace(day=1)
    end = datetime.strptime(end_date, '%Y-%m-%d').replace(day=1)
    current = start
    while current <= end:
        m = current.strftime('%Y-%m')
        months.append(m)
        found = next((item['tickets_sold'] for item in monthly_data if item['month'] == m), 0)
        tickets_per_month.append(int(found) if found else 0)
        # 下个月
        if current.month == 12:
            current = current.replace(year=current.year+1, month=1)
        else:
            current = current.replace(month=current.month+1)

    return render_template(
        'staff_view_reports.html',
        total_tickets=total_tickets,
        last_month_tickets=last_month_tickets,
        last_year_tickets=last_year_tickets,
        start_date=start_date,
        end_date=end_date,
        months=months,
        tickets_per_month=tickets_per_month
    )

@app.route('/staff/view_revenue_comparison')
def staff_view_revenue_comparison():
    if 'username' not in session or session['user_type'] != 'staff':
        flash('Please log in as airline staff to view revenue comparison.')
        return redirect(url_for('login_staff'))

    username = session['username']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # 获取staff所属航空公司
    cursor.execute("SELECT airline_name FROM Airline_Staff WHERE username = %s", (username,))
    staff = cursor.fetchone()
    if not staff:
        flash('Staff not found.')
        cursor.close()
        conn.close()
        return redirect(url_for('staff_home'))
    airline_name = staff['airline_name']

    # 过去一个月
    cursor.execute("""
        SELECT
            SUM(CASE WHEN Purchases.booking_agent_id IS NULL THEN Flight.price ELSE 0 END) AS direct_revenue,
            SUM(CASE WHEN Purchases.booking_agent_id IS NOT NULL THEN Flight.price ELSE 0 END) AS indirect_revenue
        FROM Purchases
        JOIN Ticket ON Purchases.ticket_id = Ticket.ticket_id
        JOIN Flight ON Ticket.airline_name = Flight.airline_name AND Ticket.flight_num = Flight.flight_num
        WHERE Ticket.airline_name = %s
          AND Purchases.purchase_date >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH)
    """, (airline_name,))
    month_data = cursor.fetchone()

    # 过去一年
    cursor.execute("""
        SELECT
            SUM(CASE WHEN Purchases.booking_agent_id IS NULL THEN Flight.price ELSE 0 END) AS direct_revenue,
            SUM(CASE WHEN Purchases.booking_agent_id IS NOT NULL THEN Flight.price ELSE 0 END) AS indirect_revenue
        FROM Purchases
        JOIN Ticket ON Purchases.ticket_id = Ticket.ticket_id
        JOIN Flight ON Ticket.airline_name = Flight.airline_name AND Ticket.flight_num = Flight.flight_num
        WHERE Ticket.airline_name = %s
          AND Purchases.purchase_date >= DATE_SUB(CURDATE(), INTERVAL 1 YEAR)
    """, (airline_name,))
    year_data = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template(
        'staff_view_revenue_comparison.html',
        month_data=month_data,
        year_data=year_data
    )

@app.route('/staff/view_top_destinations')
def staff_view_top_destinations():
    if 'username' not in session or session['user_type'] != 'staff':
        flash('Please log in as airline staff to view this page.')
        return redirect(url_for('login_staff'))

    username = session['username']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # 获取staff所属航空公司
    cursor.execute("SELECT airline_name FROM Airline_Staff WHERE username = %s", (username,))
    staff = cursor.fetchone()
    if not staff:
        flash('Staff not found.')
        cursor.close()
        conn.close()
        return redirect(url_for('staff_home'))
    airline_name = staff['airline_name']

    # Top 3 destinations in last 3 months
    cursor.execute("""
        SELECT f.arrival_airport, ap.airport_city, COUNT(*) AS flights_count
        FROM Flight f
        JOIN Airport ap ON f.arrival_airport = ap.airport_name
        WHERE f.airline_name = %s
          AND f.arrival_time >= DATE_SUB(CURDATE(), INTERVAL 3 MONTH)
        GROUP BY f.arrival_airport, ap.airport_city
        ORDER BY flights_count DESC
        LIMIT 3
    """, (airline_name,))
    top3_last3months = cursor.fetchall()

    # Top 3 destinations in last year
    cursor.execute("""
        SELECT f.arrival_airport, ap.airport_city, COUNT(*) AS flights_count
        FROM Flight f
        JOIN Airport ap ON f.arrival_airport = ap.airport_name
        WHERE f.airline_name = %s
          AND f.arrival_time >= DATE_SUB(CURDATE(), INTERVAL 1 YEAR)
        GROUP BY f.arrival_airport, ap.airport_city
        ORDER BY flights_count DESC
        LIMIT 3
    """, (airline_name,))
    top3_lastyear = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        'staff_view_top_destinations.html',
        top3_last3months=top3_last3months,
        top3_lastyear=top3_lastyear
    )

@app.route('/staff/grant_permission', methods=['GET', 'POST'])
def staff_grant_permission():
    # 只有有Admin权限的staff才能操作
    if 'username' not in session or session['user_type'] != 'staff':
        flash('Please log in as airline staff to grant permissions.')
        return redirect(url_for('login_staff'))

    username = session['username']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # 检查是否有Admin权限
    cursor.execute(
        "SELECT 1 FROM Permission WHERE username = %s AND permission_type = 'Admin'",
        (username,)
    )
    has_admin = cursor.fetchone()
    if not has_admin:
        cursor.close()
        conn.close()
        flash('You do not have admin permission to grant permissions.')
        return redirect(url_for('staff_home'))

    # 获取该员工所属航空公司
    cursor.execute("SELECT airline_name FROM Airline_Staff WHERE username = %s", (username,))
    staff = cursor.fetchone()
    if not staff:
        cursor.close()
        conn.close()
        flash('Staff not found.')
        return redirect(url_for('staff_home'))
    airline_name = staff['airline_name']

    # 获取同航空公司其他staff列表
    cursor.execute("""
        SELECT username FROM Airline_Staff
        WHERE airline_name = %s AND username != %s
    """, (airline_name, username))
    other_staffs = cursor.fetchall()

    # 支持的权限类型
    permission_types = ['Admin', 'Operator']

    if request.method == 'POST':
        target_username = request.form.get('target_username')
        permission_type = request.form.get('permission_type')

        # 检查目标staff是否属于同一航空公司
        cursor.execute("""
            SELECT 1 FROM Airline_Staff WHERE username = %s AND airline_name = %s
        """, (target_username, airline_name))
        if not cursor.fetchone():
            flash('Target staff not found or not in your airline.')
        elif permission_type not in permission_types:
            flash('Invalid permission type.')
        else:
            try:
                cursor.execute("""
                    INSERT IGNORE INTO Permission (username, permission_type)
                    VALUES (%s, %s)
                """, (target_username, permission_type))
                conn.commit()
                flash(f"Granted {permission_type} permission to {target_username}.")
            except mysql.connector.Error as err:
                flash(f"Error: {err}")

    # 查询所有staff及其权限
    cursor.execute("""
        SELECT s.username, GROUP_CONCAT(p.permission_type) AS permissions
        FROM Airline_Staff s
        LEFT JOIN Permission p ON s.username = p.username
        WHERE s.airline_name = %s
        GROUP BY s.username
        ORDER BY s.username
    """, (airline_name,))
    staff_permissions = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        'staff_grant_permission.html',
        other_staffs=other_staffs,
        permission_types=permission_types,
        staff_permissions=staff_permissions
    )


@app.route('/staff/add_booking_agent', methods=['GET', 'POST'])
def staff_add_booking_agent():
    # 只有有Admin权限的staff才能操作
    if 'username' not in session or session['user_type'] != 'staff':
        flash('Please log in as airline staff to add booking agents.')
        return redirect(url_for('login_staff'))

    username = session['username']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # 检查是否有Admin权限
    cursor.execute(
        "SELECT 1 FROM Permission WHERE username = %s AND permission_type = 'Admin'",
        (username,)
    )
    has_admin = cursor.fetchone()
    if not has_admin:
        cursor.close()
        conn.close()
        flash('You do not have admin permission to add booking agents.')
        return redirect(url_for('staff_home'))

    # 获取该员工所属航空公司
    cursor.execute("SELECT airline_name FROM Airline_Staff WHERE username = %s", (username,))
    staff = cursor.fetchone()
    if not staff:
        cursor.close()
        conn.close()
        flash('Staff not found.')
        return redirect(url_for('staff_home'))
    airline_name = staff['airline_name']

    if request.method == 'POST':
        agent_email = request.form.get('agent_email')
        # 检查该邮箱是否为已注册的booking agent
        cursor.execute("SELECT 1 FROM Booking_Agent WHERE email = %s", (agent_email,))
        if not cursor.fetchone():
            flash('This email is not registered as a booking agent.')
        else:
            try:
                cursor.execute("""
                    INSERT IGNORE INTO Booking_Agent_Work_For (email, airline_name)
                    VALUES (%s, %s)
                """, (agent_email, airline_name))
                conn.commit()
                flash(f"Booking agent {agent_email} added to airline {airline_name}.")
            except mysql.connector.Error as err:
                flash(f"Error: {err}")

    # 查询该航空公司所有代理
    cursor.execute("""
        SELECT bawf.email
        FROM Booking_Agent_Work_For bawf
        WHERE bawf.airline_name = %s
        ORDER BY bawf.email
    """, (airline_name,))
    agents = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        'staff_add_booking_agent.html',
        airline_name=airline_name,
        agents=agents
    )

#4/27 agent
@app.route('/agent/home')
def agent_home():
    if 'username' not in session or session['user_type'] != 'agent':
        flash('Please log in as a booking agent to view this page.')
        return redirect(url_for('login_agent'))
    return render_template('agent_home.html')


@app.route('/agent/view_flights', methods=['GET', 'POST'])
def agent_view_flights():
    if 'username' not in session or session['user_type'] != 'agent':
        flash('Please log in as a booking agent to view flights.')
        return redirect(url_for('login_agent'))

    agent_email = session['username']
    start_date = request.form.get('start_date', '').strip()
    end_date = request.form.get('end_date', '').strip()
    from_location = request.form.get('from_location', '').strip()
    to_location = request.form.get('to_location', '').strip()

    query = """
        SELECT 
            Flight.airline_name, 
            Flight.flight_num, 
            Flight.departure_airport, 
            Flight.arrival_airport, 
            Flight.departure_time, 
            Flight.arrival_time, 
            Flight.status, 
            Flight.price
        FROM Purchases
        JOIN Ticket ON Purchases.ticket_id = Ticket.ticket_id
        JOIN Flight ON Ticket.airline_name = Flight.airline_name AND Ticket.flight_num = Flight.flight_num
        WHERE Purchases.booking_agent_id = (
            SELECT booking_agent_id FROM Booking_Agent WHERE email = %s
        )
    """
    params = [agent_email]

    # Add filters dynamically
    if start_date:
        query += " AND DATE(Flight.departure_time) >= %s"
        params.append(start_date)
    if end_date:
        query += " AND DATE(Flight.departure_time) <= %s"
        params.append(end_date)
    if from_location:
        query += " AND Flight.departure_airport = %s"
        params.append(from_location)
    if to_location:
        query += " AND Flight.arrival_airport = %s"
        params.append(to_location)

    query += " ORDER BY Flight.departure_time"

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query, params)
    flights = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('agent_view_flights.html', flights=flights)

@app.route('/agent/purchase_ticket', methods=['GET', 'POST'])
def agent_purchase_ticket():
    if 'username' not in session or session['user_type'] != 'agent':
        flash('Please log in as a booking agent to purchase tickets.')
        return redirect(url_for('login_agent'))

    agent_email = session['username']

    if request.method == 'POST':
        customer_email = request.form['customer_email']
        airline_name = request.form['airline_name']
        flight_num = request.form['flight_num']

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # Check if the agent works for the airline
            cursor.execute("""
                SELECT 1 FROM Booking_Agent_Work_For 
                WHERE email = %s AND airline_name = %s
            """, (agent_email, airline_name))
            if not cursor.fetchone():
                flash('You can only purchase tickets for airlines you work for.')
                return redirect(url_for('agent_purchase_ticket'))

            # Check if there are available tickets
            cursor.execute("""
                SELECT 
                    a.seats - IFNULL(COUNT(p.ticket_id), 0) AS remaining_seats
                FROM Flight f
                JOIN Airplane a 
                    ON f.airline_name = a.airline_name AND f.airplane_id = a.airplane_id
                LEFT JOIN Ticket t 
                    ON f.airline_name = t.airline_name AND f.flight_num = t.flight_num
                LEFT JOIN Purchases p 
                    ON t.ticket_id = p.ticket_id
                WHERE f.airline_name = %s AND f.flight_num = %s
                GROUP BY a.seats;
            """, (airline_name, flight_num))
            result = cursor.fetchone()
            if not result or result[0] <= 0:
                flash('No available tickets for this flight.')
                return redirect(url_for('agent_purchase_ticket'))

            # Insert new ticket
            cursor.execute("SELECT MAX(ticket_id) FROM Ticket")
            max_id = cursor.fetchone()[0] or 0
            new_ticket_id = max_id + 1

            cursor.execute("""
                INSERT INTO Ticket (ticket_id, airline_name, flight_num)
                VALUES (%s, %s, %s)
            """, (new_ticket_id, airline_name, flight_num))

            # Insert purchase record
            cursor.execute("""
                INSERT INTO Purchases (ticket_id, customer_email, booking_agent_id, purchase_date)
                VALUES (%s, %s, (
                    SELECT booking_agent_id FROM Booking_Agent WHERE email = %s
                ), %s)
            """, (new_ticket_id, customer_email, agent_email, datetime.now().strftime('%Y-%m-%d')))
            conn.commit()
            flash('Ticket purchased successfully!')
        except mysql.connector.Error as err:
            flash(f"Error: {err}")
        finally:
            cursor.close()
            conn.close()

        return redirect(url_for('agent_home'))

    # Pre-fill form with query parameters
    airline_name = request.args.get('airline_name', '')
    flight_num = request.args.get('flight_num', '')

    return render_template('agent_purchase_ticket.html', airline_name=airline_name, flight_num=flight_num)


@app.route('/agent/view_commission', methods=['GET', 'POST'])
def agent_view_commission():
    if 'username' not in session or session['user_type'] != 'agent':
        flash('Please log in as a booking agent to view your commission.')
        return redirect(url_for('login_agent'))

    agent_email = session['username']
    start_date = request.form.get('start_date', (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
    end_date = request.form.get('end_date', datetime.now().strftime('%Y-%m-%d'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT 
            SUM(Flight.price * 0.1) AS total_commission,
            AVG(Flight.price * 0.1) AS avg_commission,
            COUNT(*) AS total_tickets
        FROM Purchases
        JOIN Ticket ON Purchases.ticket_id = Ticket.ticket_id
        JOIN Flight ON Ticket.airline_name = Flight.airline_name AND Ticket.flight_num = Flight.flight_num
        WHERE Purchases.booking_agent_id = (
            SELECT booking_agent_id FROM Booking_Agent WHERE email = %s
        )
        AND DATE(Purchases.purchase_date) BETWEEN %s AND %s
    """, (agent_email, start_date, end_date))
    commission_data = cursor.fetchone()
    cursor.close()
    conn.close()

    return render_template('agent_view_commission.html', commission_data=commission_data, start_date=start_date, end_date=end_date)


@app.route('/agent/view_top_customers')
def agent_view_top_customers():
    if 'username' not in session or session['user_type'] != 'agent':
        flash('Please log in as a booking agent to view top customers.')
        return redirect(url_for('login_agent'))

    agent_email = session['username']

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Top 5 customers by tickets sold
    cursor.execute("""
        SELECT 
            Purchases.customer_email, 
            COUNT(*) AS tickets_sold
        FROM Purchases
        JOIN Ticket ON Purchases.ticket_id = Ticket.ticket_id
        WHERE Purchases.booking_agent_id = (
            SELECT booking_agent_id FROM Booking_Agent WHERE email = %s
        )
        AND Purchases.purchase_date >= DATE_SUB(NOW(), INTERVAL 6 MONTH)
        GROUP BY Purchases.customer_email
        ORDER BY tickets_sold DESC
        LIMIT 5
    """, (agent_email,))
    top_customers_tickets = cursor.fetchall()

    # Top 5 customers by commission earned
    cursor.execute("""
        SELECT 
            Purchases.customer_email, 
            SUM(Flight.price * 0.1) AS commission_earned
        FROM Purchases
        JOIN Ticket ON Purchases.ticket_id = Ticket.ticket_id
        JOIN Flight ON Ticket.airline_name = Flight.airline_name AND Ticket.flight_num = Flight.flight_num
        WHERE Purchases.booking_agent_id = (
            SELECT booking_agent_id FROM Booking_Agent WHERE email = %s
        )
        AND Purchases.purchase_date >= DATE_SUB(NOW(), INTERVAL 1 YEAR)
        GROUP BY Purchases.customer_email
        ORDER BY commission_earned DESC
        LIMIT 5
    """, (agent_email,))
    top_customers_commission = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('agent_view_top_customers.html', 
                           top_customers_tickets=top_customers_tickets, 
                           top_customers_commission=top_customers_commission)


@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully!')
    return render_template('goodbye.html')


if __name__ == '__main__':
    app.run(debug=True)
    # app.run(host='0.0.0.0', port=5000, debug=True)