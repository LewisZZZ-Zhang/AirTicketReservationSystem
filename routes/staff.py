from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from db import get_db_connection
from datetime import datetime, timedelta
import mysql.connector

staff_bp = Blueprint('staff', __name__, url_prefix='/staff')

@staff_bp.route('/staff/staff_home')
def staff_home():
    if 'username' not in session or session['user_type'] != 'staff':
        flash('Please log in as airline staff to view this page.')
        return redirect(url_for('login_staff'))
    return render_template('staff_home.html')

# ...existing code...
@staff_bp.route('/staff/view_my_flights', methods=['GET', 'POST'])
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


@staff_bp.route('/staff/create_flight', methods=['GET', 'POST'])
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

@staff_bp.route('/staff/change_flight_status', methods=['GET', 'POST'])
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

@staff_bp.route('/staff/add_airplane', methods=['GET', 'POST'])
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

@staff_bp.route('/staff/add_airport', methods=['GET', 'POST'])
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

@staff_bp.route('/staff/view_booking_agents', methods=['GET', 'POST'])
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



@staff_bp.route('/staff/view_frequent_customers', methods=['GET', 'POST'])
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


@staff_bp.route('/staff/view_reports', methods=['GET', 'POST'])
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

@staff_bp.route('/staff/view_revenue_comparison')
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

@staff_bp.route('/staff/view_top_destinations')
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

@staff_bp.route('/staff/grant_permission', methods=['GET', 'POST'])
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


@staff_bp.route('/staff/add_booking_agent', methods=['GET', 'POST'])
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