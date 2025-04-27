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
        cursor.execute("SELECT * FROM Airline_Staff WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and user['password'] == password:  # 如果密码是明文存储
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
        # print(flight_num, result)
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

# ...existing code...

from datetime import datetime, timedelta

@app.route('/user_home', methods=['GET', 'POST'])
def user_home():
    if 'username' not in session or session['user_type'] != 'customer':
        flash('Please log in as a customer to view your dashboard.')
        return redirect(url_for('login_customer'))

    customer_email = session['username']

    # 默认起止时间：最近半年
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
        # 取该月最后一天
        end_date = datetime.strptime(end_month, '%Y-%m')
        next_month = (end_date.replace(day=28) + timedelta(days=4)).replace(day=1)
        end_date = next_month - timedelta(days=1)
    else:
        end_date = default_end

    # 查询半年内总花销
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
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
    # print(customer_email, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
    monthly_data = cursor.fetchall()
    print("monthly_data", monthly_data)
    cursor.close()
    conn.close()

    # 构造柱状图数据
    months = []
    monthly_spent = []
    # 补全没有消费的月份
    current = start_date
    while current <= end_date:
        m = current.strftime('%Y-%m')
        months.append(m)
        found = next((item['monthly_spent'] for item in monthly_data if item['month'] == m), 0)
        monthly_spent.append(float(found) if found else 0)
        # 下个月
        if current.month == 12:
            current = current.replace(year=current.year+1, month=1)
        else:
            current = current.replace(month=current.month+1)

    return render_template(
        'user_home.html',
        total_spent=total_spent,
        months=months,
        monthly_spent=monthly_spent,
        start_month=start_date.strftime('%Y-%m'),
        end_month=end_date.strftime('%Y-%m')
    )

@app.route('/staff_home')
def staff_home():
    if 'username' not in session or session['user_type'] != 'staff':
        flash('Please log in as airline staff to view this page.')
        return redirect(url_for('login_staff'))
    return render_template('staff_home.html')

@app.route('/view_my_flights')
def view_my_flights():
    # TODO: Implement staff flight view
    return "View My Flights page (to be implemented)"

@app.route('/create_flight')
def create_flight():
    # TODO: Implement create flight
    return "Create New Flight page (to be implemented)"

@app.route('/change_flight_status')
def change_flight_status():
    # TODO: Implement change status
    return "Change Status of Flights page (to be implemented)"

@app.route('/add_airplane')
def add_airplane():
    # TODO: Implement add airplane
    return "Add Airplane page (to be implemented)"

@app.route('/add_airport')
def add_airport():
    # TODO: Implement add airport
    return "Add New Airport page (to be implemented)"


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


@app.route('/agent/purchase_ticket', methods=['POST'])
def agent_purchase_ticket():
    if 'username' not in session or session['user_type'] != 'agent':
        flash('Please log in as a booking agent to purchase tickets.')
        return redirect(url_for('login_agent'))

    agent_email = session['username']
    customer_email = request.form['customer_email']
    airline_name = request.form['airline_name']
    flight_num = request.form['flight_num']

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Check if the agent works for the airline
        cursor.execute("""
            SELECT 1 FROM Booking_Agent_Works_For 
            WHERE booking_agent_email = %s AND airline_name = %s
        """, (agent_email, airline_name))
        if not cursor.fetchone():
            flash('You can only purchase tickets for airlines you work for.')
            return redirect(url_for('search_flights'))

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
            return redirect(url_for('search_flights'))

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

    return redirect(url_for('search_flights'))


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


if __name__ == '__main__':
    app.run(debug=True)
    # app.run(host='0.0.0.0', port=5000, debug=True)