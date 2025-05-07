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
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'flight_ticket_system'
}

# 获取数据库连接
def get_db_connection():
    return mysql.connector.connect(**db_config)

@app.route('/')
def home():
    if 'username' in session and session['user_type'] == 'customer':
        customer_email = session['username']

        # 查询该顾客的机票信息
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("CALL customer_get_upcoming_flights(%s);", (customer_email,))
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

        if user:
            if user['password'] == password:  # 如果密码是明文存储
                session['username'] = email
                session['user_type'] = 'customer'
                flash('Login successful. Welcome,' + session['username'] + '!')
                return redirect(url_for('home'))
            else:
                flash('Invalid login credentials.')
                return redirect(url_for('login_customer'))
        else:
            flash('No account found with this email. Please register first.')
            return redirect(url_for('register_customer'))

    return render_template(
        'login_generic.html',
        user_type="Customer",
        form_action=url_for('login_customer'),
        input_label="Email",
        input_type="email",
        input_name="email"
    )


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
            flash('Login successful. Welcome,' + session['username'] + '!')
            return redirect(url_for('agent_home'))
        else:
            flash('Invalid login credentials.')
            return redirect(url_for('login_agent'))

    return render_template(
        'login_generic.html',
        user_type="Booking Agent",
        form_action=url_for('login_agent'),
        input_label="Email",
        input_type="email",
        input_name="email"
    )


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
            authorization = 'staff'
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT permission_type FROM permission WHERE username = %s", (username,))
            permissions = cursor.fetchall()
            cursor.close()
            conn.close()
            for p in permissions:
                authorization += (',' + p['permission_type'])
            #print(authorization) #Displays how authorization loos like
            session['user_type'] = authorization
            flash('Login successful. Welcome,' + session['username'] + '!')
            return redirect(url_for('staff_home'))
        else:
            flash('Invalid login credentials.')
            return redirect(url_for('login_staff'))

    return render_template(
        'login_generic.html',
        user_type="Airline Staff",
        form_action=url_for('login_staff'),
        input_label="Username",
        input_type="text",
        input_name="username"
    )

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
    if 'username' not in session.keys() or 'customer' not in session['user_type'] :
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



@app.route('/customer/history', methods=['GET', 'POST'])
def view_all_tickets():
    if 'username' not in session.keys() or session['user_type'] != 'customer':
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

@app.route('/customer/spending', methods=['GET', 'POST'])
def spending():
    if 'username' not in session.keys() or session['user_type'] != 'customer':
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
        'spending.html',
        total_spent=total_spent,
        months=months,
        monthly_spent=monthly_spent,
        start_month=start_date.strftime('%Y-%m'),
        end_month=end_date.strftime('%Y-%m')
    )

@app.route('/staff')
def staff_home():
    if 'username' not in session.keys() or 'staff' not in session['user_type']:
        flash('Please log in as airline staff to view this page.')
        return redirect(url_for('login_staff'))
    return render_template('staff_home.html')


@app.route('/staff/home')
def redirect_staff_home():
    return redirect(url_for('staff_home'))


# Staff Functions
@app.route('/staff/view_my_flights', methods=['GET', 'POST'])
def view_my_flights():
    if 'username' not in session.keys() or 'staff' not in session['user_type']:
        flash('Please log in as airline staff to view flights.')
        return redirect(url_for('login_staff'))

    username = session['username']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    # 获取员工所属航空公司
    cursor.callproc('GetStaffAirlineInfo', (username,))
    for result in cursor.stored_results():
        staff = result.fetchone()
        if not staff:
            flash('You are not associated with any airline.')
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
    cursor.close()
    conn.close()

    return render_template(
        'staff_view_my_flights.html',
        flights=flights,
        start_date=start_date,
        end_date=end_date,
        from_location=from_location,
        to_location=to_location
    )


@app.route('/staff/top_agents')
def view_agents():
    if 'username' not in session.keys() or 'staff' not in session['user_type']:
        flash('Please log in as airline staff to view this page.')
        return redirect(url_for('login_staff'))

    username = session['username']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Get staff's airline
    cursor.callproc('GetStaffAirlineInfo', (username,))
    for result in cursor.stored_results():
        staff = result.fetchone()
        if not staff:
            flash('You are not associated with any airline.')
            cursor.close()
            conn.close()
            return redirect(url_for('staff_home'))
        airline_name = staff['airline_name']
    
    current_date = datetime.now().date()
    
    try:
        # Top 5 agents by ticket sales (past month)
        last_month = current_date - timedelta(days=30)
        cursor.execute("""
            SELECT ba.email, ba.booking_agent_id, COUNT(p.ticket_id) as ticket_count
            FROM Booking_Agent ba
            JOIN Purchases p ON ba.booking_agent_id = p.booking_agent_id
            JOIN Ticket t ON p.ticket_id = t.ticket_id
            JOIN Flight f ON t.flight_num = f.flight_num AND t.airline_name = f.airline_name
            WHERE f.airline_name = %s 
            AND p.purchase_date >= %s
            GROUP BY ba.email, ba.booking_agent_id
            ORDER BY ticket_count DESC
            LIMIT 5
        """, (airline_name, last_month))
        top_monthly_sales = cursor.fetchall()

        # Top 5 agents by ticket sales (past year)
        last_year = current_date - timedelta(days=365)
        cursor.execute("""
            SELECT ba.email, ba.booking_agent_id, COUNT(p.ticket_id) as ticket_count
            FROM Booking_Agent ba
            JOIN Purchases p ON ba.booking_agent_id = p.booking_agent_id
            JOIN Ticket t ON p.ticket_id = t.ticket_id
            JOIN Flight f ON t.flight_num = f.flight_num AND t.airline_name = f.airline_name
            WHERE f.airline_name = %s 
            AND p.purchase_date >= %s
            GROUP BY ba.email, ba.booking_agent_id
            ORDER BY ticket_count DESC
            LIMIT 5
        """, (airline_name, last_year))
        top_yearly_sales = cursor.fetchall()

        # Top 5 agents by commission (past year)
        cursor.execute("""
            SELECT ba.email, ba.booking_agent_id, 
                   SUM(f.price * 0.1) as commission  # Assuming 10% commission
            FROM Booking_Agent ba
            JOIN Purchases p ON ba.booking_agent_id = p.booking_agent_id
            JOIN Ticket t ON p.ticket_id = t.ticket_id
            JOIN Flight f ON t.flight_num = f.flight_num AND t.airline_name = f.airline_name
            WHERE f.airline_name = %s 
            AND p.purchase_date >= %s
            GROUP BY ba.email, ba.booking_agent_id
            ORDER BY commission DESC
            LIMIT 5
        """, (airline_name, last_year))
        top_commission = cursor.fetchall()

    except mysql.connector.Error as err:
        flash(f"Error retrieving agent data: {err}")
        top_monthly_sales = []
        top_yearly_sales = []
        top_commission = []
    finally:
        cursor.close()
        conn.close()

    return render_template('staff_top_agents.html',
                         top_monthly_sales=top_monthly_sales,
                         top_yearly_sales=top_yearly_sales,
                         top_commission=top_commission,
                         airline_name=airline_name)


@app.route('/staff/frequent_customers', methods=['GET', 'POST'])
def view_frequent_customers():
    if 'username' not in session.keys() or 'staff' not in session['user_type']:
        flash('Please log in as airline staff to view flights.')
        return redirect(url_for('login_staff'))
    
    username = session['username']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Get the airline the staff belongs to
    cursor.callproc('GetStaffAirlineInfo', (username,))
    for result in cursor.stored_results():
        staff = result.fetchone()
        if not staff:
            flash('You are not associated with any airline.')
            cursor.close()
            conn.close()
            return redirect(url_for('staff_home'))
        airline_name = staff['airline_name']

    frequent_customer = None
    customer_flights = []
    selected_customer_email = None

    try:
        # Query the most frequent customer in the last year
        cursor.execute("""
            SELECT 
                Purchases.customer_email, 
                COUNT(*) AS flight_count
            FROM Purchases
            JOIN Ticket ON Purchases.ticket_id = Ticket.ticket_id
            JOIN Flight ON Ticket.airline_name = Flight.airline_name AND Ticket.flight_num = Flight.flight_num
            WHERE Flight.airline_name = %s
              AND Purchases.purchase_date >= DATE_SUB(NOW(), INTERVAL 1 YEAR)
            GROUP BY Purchases.customer_email
            ORDER BY flight_count DESC
            LIMIT 1
        """, (airline_name,))
        frequent_customer = cursor.fetchone()

        # If a specific customer is selected, fetch their flight history
        selected_customer_email = request.form.get('customer_email')
        if selected_customer_email:
            cursor.execute("""
                SELECT 
                    Flight.flight_num, Flight.departure_airport, Flight.arrival_airport, 
                    Flight.departure_time, Flight.arrival_time, Flight.status, Flight.price
                FROM Purchases
                JOIN Ticket ON Purchases.ticket_id = Ticket.ticket_id
                JOIN Flight ON Ticket.airline_name = Flight.airline_name AND Ticket.flight_num = Flight.flight_num
                WHERE Purchases.customer_email = %s
                  AND Flight.airline_name = %s
                ORDER BY Flight.departure_time
            """, (selected_customer_email, airline_name))
            customer_flights = cursor.fetchall()

    except mysql.connector.Error as err:
        flash(f"Error retrieving data: {err}")
    finally:
        cursor.close()
        conn.close()

    return render_template(
        'staff_frequent_customer.html',
        frequent_customer=frequent_customer,
        customer_flights=customer_flights,
        selected_customer_email=selected_customer_email,
        airline_name=airline_name
    )


@app.route('/staff/ticket_sales', methods=['GET', 'POST'])
def view_ticket_sales():
    if 'username' not in session.keys() or 'staff' not in session['user_type']:
        flash('Please log in as airline staff to view ticket sales.')
        return redirect(url_for('login_staff'))

    username = session['username']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Get the airline the staff belongs to
    cursor.callproc('GetStaffAirlineInfo', (username,))
    for result in cursor.stored_results():
        staff = result.fetchone()
        if not staff:
            flash('You are not associated with any airline.')
            cursor.close()
            conn.close()
            return redirect(url_for('staff_home'))
        airline_name = staff['airline_name']

    # Default date range: last month
    today = datetime.today()
    default_start = (today - timedelta(days=30)).strftime('%Y-%m-%d')
    default_end = today.strftime('%Y-%m-%d')

    start_date = request.form.get('start_date', default_start)
    end_date = request.form.get('end_date', default_end)

    try:
        # Query total tickets sold in the given date range
        cursor.execute("""
            SELECT COUNT(*) AS total_tickets, SUM(Flight.price) AS total_revenue
            FROM Purchases
            JOIN Ticket ON Purchases.ticket_id = Ticket.ticket_id
            JOIN Flight ON Ticket.airline_name = Flight.airline_name AND Ticket.flight_num = Flight.flight_num
            WHERE Ticket.airline_name = %s
              AND DATE(Purchases.purchase_date) BETWEEN %s AND %s
        """, (airline_name, start_date, end_date))
        summary = cursor.fetchone()

        # Query month-wise ticket sales
        cursor.execute("""
            SELECT DATE_FORMAT(Purchases.purchase_date, '%Y-%m') AS month, COUNT(*) AS tickets_sold
            FROM Purchases
            JOIN Ticket ON Purchases.ticket_id = Ticket.ticket_id
            JOIN Flight ON Ticket.airline_name = Flight.airline_name AND Ticket.flight_num = Flight.flight_num
            WHERE Ticket.airline_name = %s
              AND DATE(Purchases.purchase_date) BETWEEN %s AND %s
            GROUP BY month
            ORDER BY month
        """, (airline_name, start_date, end_date))
        monthly_data = cursor.fetchall()

    except mysql.connector.Error as err:
        flash(f"Error retrieving ticket sales data: {err}")
        summary = {'total_tickets': 0, 'total_revenue': 0}
        monthly_data = []
    finally:
        cursor.close()
        conn.close()

    # Prepare data for the bar chart
    months = [data['month'] for data in monthly_data]
    tickets_sold = [data['tickets_sold'] for data in monthly_data]

    return render_template(
        'staff_ticket_sales.html',
        airline_name=airline_name,
        summary=summary,
        months=months,
        tickets_sold=tickets_sold,
        start_date=start_date,
        end_date=end_date
    )


@app.route('/staff/earnings', methods=['GET', 'POST'])
def view_earning_analysis():
    if 'username' not in session.keys() or 'staff' not in session['user_type']:
        flash('Please log in as airline staff to view flights.')
        return redirect(url_for('login_staff'))
    
    username = session['username']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Get the airline the staff belongs to
    cursor.callproc('GetStaffAirlineInfo', (username,))
    for result in cursor.stored_results():
        staff = result.fetchone()
        if not staff:
            flash('You are not associated with any airline.')
            cursor.close()
            conn.close()
            return redirect(url_for('staff_home'))
        airline_name = staff['airline_name']

    current_date = datetime.now().date()
    
    # Initialize variables
    monthly_direct = 0
    monthly_indirect = 0
    yearly_direct = 0
    yearly_indirect = 0
    recent_direct = []
    recent_indirect = []

    try:
        # Calculate monthly revenue (last 30 days)
        last_month = current_date - timedelta(days=30)
        cursor.execute("""
            SELECT 
                SUM(CASE WHEN p.booking_agent_id IS NULL THEN f.price ELSE 0 END) as direct,
                SUM(CASE WHEN p.booking_agent_id IS NOT NULL THEN f.price ELSE 0 END) as indirect
            FROM Ticket t
            JOIN Purchases p ON t.ticket_id = p.ticket_id
            JOIN Flight f on t.flight_num = f.flight_num
            WHERE t.airline_name = %s 
            AND p.purchase_date >= %s
        """, (airline_name, last_month))
        monthly_result = cursor.fetchone()
        monthly_direct = monthly_result['direct'] or 0
        monthly_indirect = monthly_result['indirect'] or 0

        # Calculate yearly revenue (last 365 days)
        last_year = current_date - timedelta(days=365)
        cursor.execute("""
            SELECT 
                SUM(CASE WHEN p.booking_agent_id IS NULL THEN f.price ELSE 0 END) as direct,
                SUM(CASE WHEN p.booking_agent_id IS NOT NULL THEN f.price ELSE 0 END) as indirect
            FROM Ticket t
            JOIN Purchases p ON t.ticket_id = p.ticket_id
            JOIN Flight f on t.flight_num = f.flight_num
            WHERE t.airline_name = %s 
            AND p.purchase_date >= %s
        """, (airline_name, last_year))
        yearly_result = cursor.fetchone()
        yearly_direct = yearly_result['direct'] or 0
        yearly_indirect = yearly_result['indirect'] or 0

        # Get recent direct sales (last 10)
        cursor.execute("""
            SELECT t.ticket_id, f.price, p.purchase_date, p.customer_email
            FROM Ticket t
            JOIN Purchases p ON t.ticket_id = p.ticket_id
            JOIN Flight f on t.flight_num = f.flight_num
            WHERE t.airline_name = %s 
            AND p.booking_agent_id IS NULL
            ORDER BY p.purchase_date DESC
            LIMIT 10
        """, (airline_name,))
        recent_direct = cursor.fetchall()

        # Get recent indirect sales (last 10)
        cursor.execute("""
            SELECT t.ticket_id, f.price, p.purchase_date, p.customer_email, 
                   ba.email as agent_email, ba.booking_agent_id
            FROM Ticket t
            JOIN Purchases p ON t.ticket_id = p.ticket_id
            JOIN Booking_Agent ba ON p.booking_agent_id = ba.booking_agent_id
            JOIN Flight f on t.flight_num = f.flight_num
            WHERE t.airline_name = %s 
            AND p.booking_agent_id IS NOT NULL
            ORDER BY p.purchase_date DESC
            LIMIT 10
        """, (airline_name,))
        recent_indirect = cursor.fetchall()

    except mysql.connector.Error as err:
        flash(f"Error retrieving earnings data: {err}")
    finally:
        cursor.close()
        conn.close()

    # Calculate totals and percentages for charts
    monthly_total = monthly_direct + monthly_indirect
    yearly_total = yearly_direct + yearly_indirect

    monthly_data = {
        'direct': monthly_direct,
        'indirect': monthly_indirect,
        'direct_percent': round((monthly_direct/monthly_total)*100, 2) if monthly_total > 0 else 0,
        'indirect_percent': round((monthly_indirect/monthly_total)*100, 2) if monthly_total > 0 else 0
    }

    yearly_data = {
        'direct': yearly_direct,
        'indirect': yearly_indirect,
        'direct_percent': round((yearly_direct/yearly_total)*100, 2) if yearly_total > 0 else 0,
        'indirect_percent': round((yearly_indirect/yearly_total)*100, 2) if yearly_total > 0 else 0
    }

    return render_template('staff_earnings_analysis.html',
                         monthly_data=monthly_data,
                         yearly_data=yearly_data,
                         recent_direct=recent_direct,
                         recent_indirect=recent_indirect,
                         airline_name=airline_name)


@app.route('/staff/top_destinations')
def view_top_destinations():
    if 'username' not in session.keys() or 'staff' not in session['user_type']:
        flash('Please log in as airline staff to view this page.')
        return redirect(url_for('login_staff'))

    username = session['username']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Get staff's airline
    cursor.callproc('GetStaffAirlineInfo', (username,))
    for result in cursor.stored_results():
        staff = result.fetchone()
        if not staff:
            flash('You are not associated with any airline.')
            cursor.close()
            conn.close()
            return redirect(url_for('staff_home'))
        airline_name = staff['airline_name']

    airline_name = staff['airline_name']
    current_date = datetime.now().date()
    
    try:
        # Top 3 destinations (last 3 months)
        three_months_ago = current_date - timedelta(days=90)
        cursor.execute("""
            SELECT a.airport_name, a.airport_city, COUNT(*) as ticket_count
            FROM Flight f
            JOIN Ticket t ON f.flight_num = t.flight_num AND f.airline_name = t.airline_name
            JOIN Airport a ON f.arrival_airport = a.airport_name
            WHERE f.airline_name = %s 
            AND f.arrival_time >= %s
            GROUP BY a.airport_name, a.airport_city
            ORDER BY ticket_count DESC
            LIMIT 3
        """, (airline_name, three_months_ago))
        top_3month = cursor.fetchall()

        # Top 3 destinations (last year)
        one_year_ago = current_date - timedelta(days=365)
        cursor.execute("""
            SELECT a.airport_name, a.airport_city, COUNT(*) as ticket_count
            FROM Flight f
            JOIN Ticket t ON f.flight_num = t.flight_num AND f.airline_name = t.airline_name
            JOIN Airport a ON f.arrival_airport = a.airport_name
            WHERE f.airline_name = %s 
            AND f.arrival_time >= %s
            GROUP BY a.airport_name, a.airport_city
            ORDER BY ticket_count DESC
            LIMIT 3
        """, (airline_name, one_year_ago))
        top_year = cursor.fetchall()

    except mysql.connector.Error as err:
        flash(f"Error retrieving destination data: {err}")
        top_3month = []
        top_year = []
    finally:
        cursor.close()
        conn.close()

    return render_template('staff_top_destinations.html',
                         top_3month=top_3month,
                         top_year=top_year,
                         airline_name=airline_name)


# Admin Functions
@app.route('/staff/create_flight', methods=['GET', 'POST'])
def create_flight():
    if 'username' not in session.keys() or 'Admin' not in session['user_type']:
        flash('Unauthorized Access! You are not authorized to create flights.')
        return redirect(url_for('staff_home'))

    username = session['username']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Verify if the user is an airline staff
    cursor.callproc('GetStaffAirlineInfo', (username,))
    for result in cursor.stored_results():
        staff = result.fetchone()
        if not staff:
            flash('You are not associated with any airline.')
            cursor.close()
            conn.close()
            return redirect(url_for('staff_home'))
        airline_name = staff['airline_name']

    airline_name = staff['airline_name']

    if request.method == 'POST':
        # Doublecheck for Admin permission when altering the table
        cursor.execute("SELECT 1 FROM Permission WHERE username = %s AND permission_type = 'Admin'",(username,))
        has_admin = cursor.fetchone()
        if not has_admin:
            cursor.close()
            conn.close()
            flash('You do not have permission to create flights.')
            return redirect(url_for('staff_home'))

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


@app.route('/staff/change_airplane', methods=['GET', 'POST'])
def change_airplane():
    if 'username' not in session.keys() or 'Admin' not in session['user_type']:
        flash('Unauthorized Access! You are not authorized to modify airplanes.')
        return redirect(url_for('staff_home'))

    username = session['username']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Retrieve the staff's airline company.
    cursor.callproc('GetStaffAirlineInfo', (username,))
    for result in cursor.stored_results():
        staff = result.fetchone()
        if not staff:
            flash('You are not associated with any airline.')
            cursor.close()
            conn.close()
            return redirect(url_for('staff_home'))
        airline_name = staff['airline_name']

    if request.method == 'POST':
        # Doublecheck for Admin permission when altering the table
        cursor.execute("SELECT 1 FROM Permission WHERE username = %s AND permission_type = 'Admin'",(username,))
        has_admin = cursor.fetchone()
        if not has_admin:
            cursor.close()
            conn.close()
            flash('You do not have permission to add airplanes.')
            return redirect(url_for('staff_home'))
        
        action = request.form['action']
        
        if action == 'add':
            # Get airplane details from the form
            airplane_id = request.form['airplane_id']
            seats = request.form['seats']
            
            # Validate input data
            if not all([airplane_id, seats]):
                flash('All fields are required for adding an airplane.')
                cursor.close()
                conn.close()
                return redirect(url_for('change_airplane'))

            try:
                # Insert the new airplane into the database
                cursor.execute("""
                    INSERT INTO Airplane (airline_name, airplane_id, seats)
                    VALUES (%s, %s, %s)
                """, (airline_name, airplane_id, seats))
                conn.commit()
                flash('Airplane added successfully!')
            except mysql.connector.Error as err:
                if (err.errno == 1062):  # Duplicate entry error
                    flash(f"Error: Airplane ID {airplane_id} already exists.")
                else:
                    flash(f"Error: {err}")
        
        elif action == 'remove':
            # Get airplane ID to remove
            airplane_id = request.form['airplane_id_remove']
            
            if not airplane_id:
                flash('Airplane ID is required for removal.')
                cursor.close()
                conn.close()
                return redirect(url_for('change_airplane'))

            try:
                # Check if airplane exists and belongs to the airline
                cursor.execute("""
                    SELECT 1 FROM Airplane 
                    WHERE airplane_id = %s AND airline_name = %s
                """, (airplane_id, airline_name))
                if not cursor.fetchone():
                    flash(f"Airplane ID '{airplane_id}' does not exist or does not belong to your airline.")
                    cursor.close()
                    conn.close()
                    return redirect(url_for('change_airplane'))

                # Delete the airplane
                cursor.execute("""
                    DELETE FROM Airplane 
                    WHERE airplane_id = %s AND airline_name = %s
                """, (airplane_id, airline_name))
                conn.commit()
                flash('Airplane removed successfully!')
            except mysql.connector.Error as err:
                flash(f"Error: {err}")

    # Get all airplanes for the current airline to display
    cursor.execute("""
        SELECT airplane_id, seats 
        FROM Airplane 
        WHERE airline_name = %s
        ORDER BY airplane_id
    """, (airline_name,))
    airplanes = cursor.fetchall()

    cursor.close()
    conn.close()
    
    return render_template('staff_change_airplane.html', 
                         airline_name=airline_name, 
                         airplanes=airplanes)


@app.route('/staff/airport_management', methods=['GET', 'POST'])
def airport_management():
    if 'username' not in session.keys() or 'Admin' not in session['user_type']:
        flash('Unauthorized Access! You are not authorized to manage airports.')
        return redirect(url_for('staff_home'))

    username = session['username']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.callproc('GetStaffAirlineInfo', (username,))
    for result in cursor.stored_results():
        staff = result.fetchone()
        if not staff:
            flash('You are not associated with any airline.')
            cursor.close()
            conn.close()
            return redirect(url_for('staff_home'))
        airline_name = staff['airline_name']

    search_results = None

    if request.method == 'POST':
        # Doublecheck for Admin permission when altering the table
        cursor.execute("SELECT 1 FROM Permission WHERE username = %s AND permission_type = 'Admin'",(username,))
        has_admin = cursor.fetchone()
        if not has_admin:
            cursor.close()
            conn.close()
            flash('You do not have permission to add airplanes.')
            return redirect(url_for('staff_home'))
        
        action = request.form.get('action')
        
        if action == 'add':
            airport_name = request.form['airport_name'].upper()
            airport_city = request.form['airport_city']
            
            if not all([airport_name, airport_city]):
                flash('All fields are required for adding an airport.')
                cursor.close()
                conn.close()
                return redirect(url_for('airport_management'))

            if len(airport_name) != 3:
                flash('Airport code must be exactly 3 letters.')
                cursor.close()
                conn.close()
                return redirect(url_for('airport_management'))

            try:
                cursor.execute("SELECT 1 FROM Airport WHERE airport_name = %s", (airport_name,))
                if cursor.fetchone():
                    flash(f"Airport '{airport_name}' already exists.")
                    cursor.close()
                    conn.close()
                    return redirect(url_for('airport_management'))

                cursor.execute("""
                    INSERT INTO Airport (airport_name, airport_city)
                    VALUES (%s, %s)
                """, (airport_name, airport_city))
                conn.commit()
                flash(f"Airport '{airport_name}' added successfully!")
            except mysql.connector.Error as err:
                flash(f"Error: {err}")
        
        elif action == 'delete':
            airport_name = request.form['airport_name_delete'].upper()
            
            if not airport_name:
                flash('Airport code is required for deletion.')
                cursor.close()
                conn.close()
                return redirect(url_for('airport_management'))

            try:
                cursor.execute("SELECT 1 FROM Airport WHERE airport_name = %s", (airport_name,))
                if not cursor.fetchone():
                    flash(f"Airport '{airport_name}' does not exist.")
                    cursor.close()
                    conn.close()
                    return redirect(url_for('airport_management'))

                cursor.execute("""
                    SELECT 1 FROM Flight 
                    WHERE departure_airport = %s OR arrival_airport = %s
                    LIMIT 1
                """, (airport_name, airport_name))
                if cursor.fetchone():
                    flash(f"Cannot delete airport '{airport_name}' as it is used in existing flights.")
                    cursor.close()
                    conn.close()
                    return redirect(url_for('airport_management'))

                cursor.execute("DELETE FROM Airport WHERE airport_name = %s", (airport_name,))
                conn.commit()
                flash(f"Airport '{airport_name}' deleted successfully!")
            except mysql.connector.Error as err:
                flash(f"Error: {err}")
        
        elif action == 'search':
            search_term = request.form['search_term']
            if not search_term:
                flash('Please enter a search term.')
                cursor.close()
                conn.close()
                return redirect(url_for('airport_management'))

            try:
                cursor.execute("""
                    SELECT * FROM Airport 
                    WHERE airport_name LIKE %s OR airport_city LIKE %s
                    ORDER BY airport_name
                """, (f'%{search_term}%', f'%{search_term}%'))
                search_results = cursor.fetchall()
                if not search_results:
                    flash('No airports found matching your search.')
            except mysql.connector.Error as err:
                flash(f"Error: {err}")

    cursor.close()
    conn.close()
    
    return render_template('staff_airport_management.html', 
                         airline_name=airline_name,
                         search_results=search_results)


@app.route('/staff/permission_management', methods=['GET', 'POST'])
def manage_permission():
    if 'username' not in session.keys() or 'Admin' not in session['user_type']:
        flash('Unauthorized Access! You are not authorized to manage permissions.')
        return redirect(url_for('staff_home'))

    admin_username = session['username']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Get admin's airline
    cursor.execute("SELECT airline_name FROM Airline_Staff WHERE username = %s", (admin_username,))
    admin_airline = cursor.fetchone()
    if not admin_airline:
        flash('You are not associated with any airline.')
        cursor.close()
        conn.close()
        return redirect(url_for('staff_home'))

    airline_name = admin_airline['airline_name']
    staff_list = []
    current_permissions = {}

    if request.method == 'POST':        
        action = request.form.get('action')
        target_username = request.form.get('username')
        permission_type = request.form.get('permission_type')

        # Validate inputs
        if not all([action, target_username, permission_type]):
            flash('All fields are required.')
            cursor.close()
            conn.close()
            return redirect(url_for('manage_permission'))

        # Check if target staff exists and belongs to same airline
        cursor.execute("""
            SELECT 1 FROM Airline_Staff 
            WHERE username = %s AND airline_name = %s
        """, (target_username, airline_name))
        if not cursor.fetchone():
            flash(f"Staff '{target_username}' not found in your airline.")
            cursor.close()
            conn.close()
            return redirect(url_for('manage_permission'))

        if action == 'add':
            try:
                # Check if permission already exists
                cursor.execute("""
                    SELECT 1 FROM Permission 
                    WHERE username = %s AND permission_type = %s
                """, (target_username, permission_type))
                if cursor.fetchone():
                    flash(f"Permission '{permission_type}' already granted to '{target_username}'.")
                    cursor.close()
                    conn.close()
                    return redirect(url_for('manage_permission'))

                # Add new permission
                cursor.execute("""
                    INSERT INTO Permission (username, permission_type)
                    VALUES (%s, %s)
                """, (target_username, permission_type))
                conn.commit()
                flash(f"Successfully granted '{permission_type}' permission to '{target_username}'.")
            except mysql.connector.Error as err:
                flash(f"Error: {err}")

        elif action == 'remove':
            # Special check for Admin permission removal
            if permission_type == 'Admin':
                # Check if this is the last admin
                cursor.execute("""
                    SELECT COUNT(*) as admin_count
                    FROM Permission p
                    JOIN Airline_Staff s ON p.username = s.username
                    WHERE p.permission_type = 'Admin' 
                    AND s.airline_name = %s
                """, (airline_name,))
                admin_count = cursor.fetchone()['admin_count']
                
                if admin_count <= 1:
                    flash("Cannot remove last Admin permission from the airline.")
                    cursor.close()
                    conn.close()
                    return redirect(url_for('manage_permission'))

            try:
                # Remove permission
                cursor.execute("""
                    DELETE FROM Permission 
                    WHERE username = %s AND permission_type = %s
                """, (target_username, permission_type))
                if cursor.rowcount == 0:
                    flash(f"Permission '{permission_type}' not found for '{target_username}'.")
                else:
                    conn.commit()
                    flash(f"Successfully removed '{permission_type}' permission from '{target_username}'.")
            except mysql.connector.Error as err:
                flash(f"Error: {err}")

    # Get all staff in the same airline
    cursor.execute("""
        SELECT username FROM Airline_Staff 
        WHERE airline_name = %s
        ORDER BY username
    """, (airline_name,))
    staff_list = [staff['username'] for staff in cursor.fetchall()]

    # Get current permissions for all staff
    cursor.execute("""
        SELECT p.username, p.permission_type 
        FROM Permission p
        JOIN Airline_Staff s ON p.username = s.username
        WHERE s.airline_name = %s
        ORDER BY p.username, p.permission_type
    """, (airline_name,))
    
    for row in cursor.fetchall():
        if row['username'] not in current_permissions:
            current_permissions[row['username']] = []
        current_permissions[row['username']].append(row['permission_type'])

    cursor.close()
    conn.close()

    return render_template('staff_permission_management.html',
                         airline_name=airline_name,
                         staff_list=staff_list,
                         current_permissions=current_permissions)



@app.route('/staff/change_agent', methods=['GET', 'POST'])
def change_agent():
    if 'username' not in session.keys() or 'Admin' not in session['user_type']:
        flash('Unauthorized Access! You are not authorized to change agents.')
        return redirect(url_for('staff_home'))

    username = session['username']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Retrieve the staff's airline company.
    cursor.callproc('GetStaffAirlineInfo', (username,))
    for result in cursor.stored_results():
        staff = result.fetchone()
        if not staff:
            flash('You are not associated with any airline.')
            cursor.close()
            conn.close()
            return redirect(url_for('staff_home'))
        airline_name = staff['airline_name']

    if request.method == 'POST':
        # Doublecheck for Admin permission when altering the table
        cursor.execute("SELECT 1 FROM Permission WHERE username = %s AND permission_type = 'Admin'",(username,))
        has_admin = cursor.fetchone()
        if not has_admin:
            cursor.close()
            conn.close()
            flash('You do not have permission to add airplanes.')
            return redirect(url_for('staff_home'))
        
        action = request.form['action']
        
        if action == 'add':
            # Get agent details from the form
            agent_email = request.form['agent_email']
            
            # Validate input data
            if not agent_email:
                flash('Agent email is required.')
                cursor.close()
                conn.close()
                return redirect(url_for('change_agents'))

            try:
                # Check if agent exists in booking_agent table
                cursor.execute("SELECT 1 FROM Booking_Agent WHERE email = %s", (agent_email,))
                if not cursor.fetchone():
                    flash(f"Agent with email '{agent_email}' does not exist in the system.")
                    cursor.close()
                    conn.close()
                    return redirect(url_for('change_agents'))

                # Check if agent already works for this airline
                cursor.execute("""
                    SELECT 1 FROM Booking_Agent_Work_For 
                    WHERE email = %s AND airline_name = %s
                """, (agent_email, airline_name))
                if cursor.fetchone():
                    flash(f"Agent already works for {airline_name}.")
                    cursor.close()
                    conn.close()
                    return redirect(url_for('change_agents'))

                # Add the agent to work for this airline
                cursor.execute("""
                    INSERT INTO Booking_Agent_Work_For (email, airline_name)
                    VALUES (%s, %s)
                """, (agent_email, airline_name))
                conn.commit()
                flash('Booking agent added successfully!')
            except mysql.connector.Error as err:
                flash(f"Error: {err}")
        
        elif action == 'remove':
            # Get agent email to remove
            agent_email = request.form['agent_email_remove']
            
            if not agent_email:
                flash('Agent email is required for removal.')
                cursor.close()
                conn.close()
                return redirect(url_for('change_agents'))

            try:
                # Check if agent exists and works for this airline
                cursor.execute("""
                    SELECT 1 FROM Booking_Agent_Work_For 
                    WHERE email = %s AND airline_name = %s
                """, (agent_email, airline_name))
                if not cursor.fetchone():
                    flash(f"Agent with email '{agent_email}' does not work for your airline.")
                    cursor.close()
                    conn.close()
                    return redirect(url_for('change_agents'))

                # Remove the agent from working for this airline
                cursor.execute("""
                    DELETE FROM Booking_Agent_Work_For 
                    WHERE email = %s AND airline_name = %s
                """, (agent_email, airline_name))
                conn.commit()
                flash('Booking agent removed successfully!')
            except mysql.connector.Error as err:
                flash(f"Error: {err}")

    # Get all booking agents for the current airline to display
    cursor.execute("""
        SELECT b.email, b.booking_agent_id 
        FROM Booking_Agent b
        JOIN Booking_Agent_Work_For w ON b.email = w.email
        WHERE w.airline_name = %s
        ORDER BY b.booking_agent_id
    """, (airline_name,))
    agents = cursor.fetchall()

    cursor.close()
    conn.close()
    
    return render_template('staff_change_agent.html', 
                         airline_name=airline_name, 
                         agents=agents)



#Operator Functions
@app.route('/staff/change_flight_status', methods=['GET', 'POST'])
def change_flight_status():
    if 'username' not in session.keys() or 'Operator' not in session['user_type']:
        flash('Unauthorized Access! You are not authorized to change flight statuses.')
        return redirect(url_for('staff_home'))

    username = session['username']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Get the airline the staff belongs to
    cursor.callproc('GetStaffAirlineInfo', (username,))
    for result in cursor.stored_results():
        staff = result.fetchone()
        if not staff:
            flash('You are not associated with any airline.')
            cursor.close()
            conn.close()
            return redirect(url_for('staff_home'))
        airline_name = staff['airline_name']

    if request.method == 'POST':
        # Doublecheck for Operator permission when altering the table
        cursor.execute("SELECT 1 FROM Permission WHERE username = %s AND permission_type = 'Operator'",(username,))
        has_admin = cursor.fetchone()
        if not has_admin:
            cursor.close()
            conn.close()
            flash('You do not have permission to change flight status.')
            return redirect(url_for('staff_home'))

        flight_num = request.form['flight_num']
        new_status = request.form['new_status']

        # Validate the new status
        if new_status not in ['Upcoming', 'In Progress', 'Delayed', 'Completed']:
            flash('Invalid status.')
            cursor.close()
            conn.close()
            return redirect(url_for('change_flight_status'))

        # Check if the flight belongs to the airline
        cursor.execute(
            "SELECT * FROM Flight WHERE airline_name = %s AND flight_num = %s",
            (airline_name, flight_num)
        )
        flight = cursor.fetchone()
        if not flight:
            flash('Flight not found or does not belong to your airline.')
        else:
            try:
                # Update the flight status
                cursor.execute(
                    "UPDATE Flight SET status = %s WHERE airline_name = %s AND flight_num = %s",
                    (new_status, airline_name, flight_num)
                )
                conn.commit()
                flash('Flight status updated successfully!')
            except mysql.connector.Error as err:
                flash(f"Error: {err}")

    # Fetch all flights for the airline
    cursor.execute(
        "SELECT flight_num, departure_airport, arrival_airport, departure_time, arrival_time, status "
        "FROM Flight WHERE airline_name = %s ORDER BY flight_num ASC",
        (airline_name,)
    )
    flights = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('staff_change_flight_status.html', flights=flights)


# Agent Functions
@app.route('/agent/home')
def agent_home():
    if 'username' not in session.keys() or session['user_type'] != 'agent':
        flash('Please log in as a booking agent to view this page.')
        return redirect(url_for('login_agent'))
    return render_template('agent_home.html')


@app.route('/agent/view_flights', methods=['GET', 'POST'])
def agent_view_flights():
    if 'username' not in session.keys() or session['user_type'] != 'agent':
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


# 这里有点问题，前端要新弄一个html给agent
# Purchase tickets: Booking agent chooses a flight and purchases tickets for other customers giving 
# customer information. You may find it easier to implement this along with a use case to search for 
# flights. Notice that as described in the previous assignments, the booking agent may only purchase tickets from 
# airlines they work for.

# @app.route('/agent/purchase_ticket', methods=['POST'])
# def agent_purchase_ticket():
#     if 'username' not in session.keys() or session['user_type'] != 'agent':
#         flash('Please log in as a booking agent to purchase tickets.')
#         return redirect(url_for('login_agent'))

#     agent_email = session['username']
#     customer_email = request.form['customer_email']  这里有点问题，前端要新弄一个html给agent
#     airline_name = request.form['airline_name']       
#     flight_num = request.form['flight_num']  

#     conn = get_db_connection()
#     cursor = conn.cursor()

#     try:
#         # Check if the agent works for the airline
#         cursor.execute("""
#             SELECT 1 FROM Booking_Agent_Works_For 
#             WHERE booking_agent_email = %s AND airline_name = %s
#         """, (agent_email, airline_name))
#         if not cursor.fetchone():
#             flash('You can only purchase tickets for airlines you work for.')
#             return redirect(url_for('search_flights'))

#         # Check if there are available tickets
#         cursor.execute("""
#             SELECT 
#                 a.seats - IFNULL(COUNT(p.ticket_id), 0) AS remaining_seats
#             FROM Flight f
#             JOIN Airplane a 
#                 ON f.airline_name = a.airline_name AND f.airplane_id = a.airplane_id
#             LEFT JOIN Ticket t 
#                 ON f.airline_name = t.airline_name AND f.flight_num = t.flight_num
#             LEFT JOIN Purchases p 
#                 ON t.ticket_id = p.ticket_id
#             WHERE f.airline_name = %s AND f.flight_num = %s
#             GROUP BY a.seats;
#         """, (airline_name, flight_num))
#         result = cursor.fetchone()
#         if not result or result[0] <= 0:
#             flash('No available tickets for this flight.')
#             return redirect(url_for('search_flights'))

#         # Insert new ticket
#         cursor.execute("SELECT MAX(ticket_id) FROM Ticket")
#         max_id = cursor.fetchone()[0] or 0
#         new_ticket_id = max_id + 1

#         cursor.execute("""
#             INSERT INTO Ticket (ticket_id, airline_name, flight_num)
#             VALUES (%s, %s, %s)
#         """, (new_ticket_id, airline_name, flight_num))

#         # Insert purchase record
#         cursor.execute("""
#             INSERT INTO Purchases (ticket_id, customer_email, booking_agent_id, purchase_date)
#             VALUES (%s, %s, (
#                 SELECT booking_agent_id FROM Booking_Agent WHERE email = %s
#             ), %s)
#         """, (new_ticket_id, customer_email, agent_email, datetime.now().strftime('%Y-%m-%d')))
#         conn.commit()
#         flash('Ticket purchased successfully!')
#     except mysql.connector.Error as err:
#         flash(f"Error: {err}")
#     finally:
#         cursor.close()
#         conn.close()

#     return redirect(url_for('search_flights'))

#4/29 测试一下改过的purchase
@app.route('/agent/purchase_ticket', methods=['GET', 'POST'])
def agent_purchase_ticket():
    if 'username' not in session.keys() or session['user_type'] != 'agent':
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
    if 'username' not in session.keys() or session['user_type'] != 'agent':
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
    if 'username' not in session.keys() or session['user_type'] != 'agent':
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