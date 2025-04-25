from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # 用于会话加密

# 数据库连接配置
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'airticketreservationsystem'
}

# 获取数据库连接
def get_db_connection():
    return mysql.connector.connect(**db_config)

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
        cursor.execute("SELECT * FROM Customer WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and user['password'] == password:  # 如果密码是明文存储
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
        cursor.execute("SELECT * FROM Booking_Agent WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and user['password'] == password:  # 如果密码是明文存储
            session['username'] = email
            session['user_type'] = 'agent'
            flash('Booking Agent login successful!')
            return redirect(url_for('home'))
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
        cursor.execute("SELECT * FROM Airline_Staff WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and user['password'] == password:  # 如果密码是明文存储
            session['username'] = username
            session['user_type'] = 'staff'
            flash('Airline Staff login successful!')
            return redirect(url_for('home'))
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
                VALUES (%s, %s, %s)
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
                VALUES (%s, %s, %s, %s, %s, %s)
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
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully!')
    return redirect(url_for('home'))


@app.route('/search_flights', methods=['GET','POST'])
def search_flights():
    if request.method == 'GET':
        # 如果是 GET 请求，直接渲染搜索页面
        return render_template('search_flights.html', flights=None, from_location='', to_location='', date='')

    from_location = request.form.get('from_location', '').strip()
    to_location = request.form.get('to_location', '').strip()
    date = request.form.get('date', '').strip()
    print(from_location,to_location,date)

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
    print("result:",flights)
    return render_template('search_flights.html', flights=flights, from_location=from_location, to_location=to_location, date=date)

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
        # 检查是否还有可用票
        cursor.execute("""
            SELECT 
                a.seats - IFNULL(COUNT(p.ticket_id), 0) AS remaining_seats
            FROM flight f
            JOIN airplane a 
                ON f.airline_name = a.airline_name AND f.airplane_id = a.airplane_id
            LEFT JOIN ticket t 
                ON f.airline_name = t.airline_name AND f.flight_num = t.flight_num
            LEFT JOIN purchases p 
                ON t.ticket_id = p.ticket_id
            WHERE f.airline_name = %s AND f.flight_num = %s
            GROUP BY a.seats;
        """, (airline_name, flight_num))
        result = cursor.fetchone()
        print(flight_num, result)
        if result and result[0] > 0:
            print("OK to purchase")
            cursor.execute("SELECT MAX(ticket_id) FROM ticket")
            max_id = cursor.fetchone()[0] or 0
            new_ticket_id = max_id + 1

            # 插入新的 ticket
            cursor.execute("""
                INSERT INTO ticket (ticket_id, airline_name, flight_num)
                VALUES (%s, %s, %s)
            """, (new_ticket_id, airline_name, flight_num))

            # 插入购票记录
            cursor.execute("""
                INSERT INTO Purchases (ticket_id, customer_email, purchase_date)
                VALUES (%s, %s, %s)
            """, (new_ticket_id, customer_email, datetime.now().strftime('%Y-%m-%d')))
            conn.commit()
            flash('Ticket purchased successfully!')
        else:
            flash('No available tickets for this flight. **Error1**')
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

@app.route('/user_home', methods=['GET', 'POST'])
def user_home():
    if 'username' not in session:
        flash('Please log in to view your homepage.')
        return redirect(url_for('login'))

    user_email = session['username']
    user_type = session['user_type']

    if user_type != 'customer':
        flash('Only customers can view this page.')
        return redirect(url_for('home'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Default: Past year and last 6 months
    total_spent = 0
    month_wise_spending = []
    start_date = None
    end_date = None

    try:
        # Calculate total spending in the past year
        cursor.execute("""
            SELECT SUM(Flight.price) AS total_spent
            FROM Purchases
            JOIN Ticket ON Purchases.ticket_id = Ticket.ticket_id
            JOIN Flight ON Ticket.airline_name = Flight.airline_name AND Ticket.flight_num = Flight.flight_num
            WHERE Purchases.customer_email = %s
            AND Purchases.purchase_date >= DATE_SUB(CURDATE(), INTERVAL 1 YEAR)
        """, (user_email,))
        total_spent = cursor.fetchone()['total_spent'] or 0

        # Calculate month-wise spending for the last 6 months
        cursor.execute("""
            SELECT DATE_FORMAT(Purchases.purchase_date, '%Y-%m') AS month, SUM(Flight.price) AS total
            FROM Purchases
            JOIN Ticket ON Purchases.ticket_id = Ticket.ticket_id
            JOIN Flight ON Ticket.airline_name = Flight.airline_name AND Ticket.flight_num = Flight.flight_num
            WHERE Purchases.customer_email = %s
            AND Purchases.purchase_date >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH)
            GROUP BY DATE_FORMAT(Purchases.purchase_date, '%Y-%m')
            ORDER BY month
        """, (user_email,))
        month_wise_spending = cursor.fetchall()

        # If a custom date range is provided
        if request.method == 'POST':
            start_date = request.form.get('start_date')
            end_date = request.form.get('end_date')

            if start_date and end_date:
                # Calculate total spending within the range
                cursor.execute("""
                    SELECT SUM(Flight.price) AS total_spent
                    FROM Purchases
                    JOIN Ticket ON Purchases.ticket_id = Ticket.ticket_id
                    JOIN Flight ON Ticket.airline_name = Flight.airline_name AND Ticket.flight_num = Flight.flight_num
                    WHERE Purchases.customer_email = %s
                    AND Purchases.purchase_date BETWEEN %s AND %s
                """, (user_email, start_date, end_date))
                total_spent = cursor.fetchone()['total_spent'] or 0

                # Calculate month-wise spending within the range
                cursor.execute("""
                    SELECT DATE_FORMAT(Purchases.purchase_date, '%Y-%m') AS month, SUM(Flight.price) AS total
                    FROM Purchases
                    JOIN Ticket ON Purchases.ticket_id = Ticket.ticket_id
                    JOIN Flight ON Ticket.airline_name = Flight.airline_name AND Ticket.flight_num = Flight.flight_num
                    WHERE Purchases.customer_email = %s
                    AND Purchases.purchase_date BETWEEN %s AND %s
                    GROUP BY DATE_FORMAT(Purchases.purchase_date, '%Y-%m')
                    ORDER BY month
                """, (user_email, start_date, end_date))
                month_wise_spending = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

    return render_template(
        'user_home.html',
        total_spent=total_spent,
        month_wise_spending=month_wise_spending,
        start_date=start_date,
        end_date=end_date
    )

if __name__ == '__main__':
    app.run(debug=True)
    # app.run(host='0.0.0.0', port=5000, debug=True)