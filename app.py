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
    'database': 'airticketsystem'
}

# 获取数据库连接
def get_db_connection():
    return mysql.connector.connect(**db_config)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user_type = request.form['user_type']

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        if user_type == 'customer':
            cursor.execute("SELECT * FROM Customer WHERE email = %s AND password = %s", (email, password))
        elif user_type == 'agent':
            cursor.execute("SELECT * FROM Booking_Agent WHERE email = %s AND password = %s", (email, password))
        elif user_type == 'staff':
            cursor.execute("SELECT * FROM Airline_Staff WHERE username = %s AND password = %s", (email, password))
        else:
            flash("Invalid user type.")
            return redirect(url_for('login'))

        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user:
            session['username'] = email
            session['user_type'] = user_type
            flash('Login successful!')
            return redirect(url_for('home'))
        else:
            flash('Invalid login credentials.')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully!')
    return redirect(url_for('home'))

@app.route('/register')
def register():
    return render_template('register.html')

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

# @app.route('/check_status', methods=['POST'])
# def check_status():
#     flight_num = request.form['flight_num']
#     departure_date = request.form['departure_date']
#     arrival_date = request.form.get('arrival_date', '').strip()

#     query = "SELECT * FROM Flight WHERE 1=1"  # 基础查询
#     params = []

#     # 动态添加查询条件
#     if flight_num:
#         query += " AND flight_num = %s"
#         params.append(flight_num)
#     if departure_date:
#         query += " AND DATE(departure_time) = %s"
#         params.append(departure_date)
#     if arrival_date:
#         query += " AND DATE(arrival_time) = %s"
#         params.append(arrival_date)

#     conn = get_db_connection()
#     cursor = conn.cursor(dictionary=True)
#     cursor.execute(query, params)  # 动态查询
#     flights = cursor.fetchall()
#     cursor.close()
#     conn.close()

#     if flights:
#         flash(f"Found {len(flights)} flight(s) matching your criteria.")
#     else:
#         flash("No flights found matching your criteria.")
#     return render_template('index.html', flights=flights, flight_num=flight_num, departure_date=departure_date, arrival_date=arrival_date)
#     # return redirect(url_for('home'))

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


if __name__ == '__main__':
    app.run(debug=True)
