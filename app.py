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
    'database': 'airticketreservationsystem'
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

        if user and user['password'] == password:  # 如果密码是明文存储
            session['username'] = email
            session['user_type'] = 'customer'
            flash('Login successful. Welcome,' + session['username'] + '!')
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
            flash('Login successful. Welcome,' + session['username'] + '!')
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

@app.route('/staff/staff_home')
def staff_home():
    if 'username' not in session.keys() or 'staff' not in session['user_type']:
        flash('Please log in as airline staff to view this page.')
        return redirect(url_for('login_staff'))
    return render_template('staff_home.html')


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
        flash('Please log in as airline staff to view flights.')
        return redirect(url_for('login_staff'))
    return "View top 5 booking agents. (to be implemented)"


@app.route('/staff/frequent_customers')
def view_frequent_customers():
    if 'username' not in session.keys() or 'staff' not in session['user_type']:
        flash('Please log in as airline staff to view flights.')
        return redirect(url_for('login_staff'))
    # TODO
    return "View frequent customers. (to be implemented)"


@app.route('/staff/ticket_sales')
def view_ticket_sales():
    if 'username' not in session.keys() or 'staff' not in session['user_type']:
        flash('Please log in as airline staff to view flights.')
        return redirect(url_for('login_staff'))
    # TODO
    return "View ticket sales. (to be implemented)"


@app.route('/staff/earnings')
def view_earning_analysis():
    if 'username' not in session.keys() or 'staff' not in session['user_type']:
        flash('Please log in as airline staff to view flights.')
        return redirect(url_for('login_staff'))
    # TODO  
    return "View earning analysis. (to be implemented)"


@app.route('/staff/top_destinations')
def view_top_destinations():
    if 'username' not in session.keys() or 'staff' not in session['user_type']:
        flash('Please log in as airline staff to view flights.')
        return redirect(url_for('login_staff'))
    # TODO
    return "View top destinations. (to be implemented)"


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
    cursor.execute("SELECT airline_name FROM Airline_Staff WHERE username = %s", (username,))
    staff = cursor.fetchone()
    if not staff:
        flash('You are not authorized to create flights.')
        cursor.close()
        conn.close()
        return redirect(url_for('staff_home'))

    airline_name = staff['airline_name']

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


@app.route('/staff/change_airplane', methods=['GET', 'POST'])
def change_airplane():
    if 'username' not in session.keys() or 'Admin' not in session['user_type']:
        flash('Unauthorized Access! You are not authorized to modify airplanes.')
        return redirect(url_for('staff_home'))

    username = session['username']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Verify if the user is an airline staff
    cursor.execute("SELECT airline_name FROM Airline_Staff WHERE username = %s", (username,))
    staff = cursor.fetchone()
    if not staff:
        flash('You are not authorized to modify airplanes.')
        cursor.close()
        conn.close()
        return redirect(url_for('staff_home'))

    airline_name = staff['airline_name']

    if request.method == 'POST':
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
                if err.errno == 1062:  # Duplicate entry error
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

@app.route('/staff/add_airport')
def add_airport():
    if 'username' not in session.keys() or 'Admin' not in session['user_type']:
        flash('Unauthorized Access! You are not authorized to add airports.')
        return redirect(url_for('staff_home'))

    # TODO: Implement add airport
    return "Add New Airport page (to be implemented)"


@app.route('/staff/change_permissions')
def change_permissions():
    if 'username' not in session.keys() or 'Admin' not in session['user_type']:
        flash('Unauthorized Access! You are not authorized to change permissions.')
        return redirect(url_for('staff_home'))

    # TODO: Implement add airport
    return "Change permissions page (to be implemented)"


@app.route('/staff/change_agents')
def change_agents():
    if 'username' not in session.keys() or 'Admin' not in session['user_type']:
        flash('Unauthorized Access! You are not authorized to change agents.')
        return redirect(url_for('staff_home'))

    # TODO: Implement add airport
    return "Change agents page (to be implemented)"


#Operator Functions
@app.route('/staff/change_flight_status')
def change_flight_status():
    if 'username' not in session.keys() or 'Operator' not in session['user_type']:
        flash('Unauthorized Access! You are not authorized to change flights status.')
        return redirect(url_for('staff_home'))
    
    # TODO: Implement change status   
    return "Change Status of Flights page (to be implemented)"




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