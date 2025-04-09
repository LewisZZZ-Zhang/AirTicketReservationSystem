from flask import Flask, render_template, request, redirect, session, url_for, flash
import mysql.connector

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# 配置数据库
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",  # 根据你设置的密码
    database="airticketsystem"
)
cursor = db.cursor(dictionary=True)

# 主页
@app.route('/')
def index():
    return render_template('index.html')

# 注册页面
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user_type = request.form['user_type']
        email = request.form['email']
        password = request.form['password']

        try:
            if user_type == 'customer':
                name = request.form['name']
                dob = request.form['dob']
                query = "INSERT INTO customer (email, name, password, date_of_birth) VALUES (%s, %s, %s, %s)"
                cursor.execute(query, (email, name, password, dob))
            
            elif user_type == 'booking_agent':
                query = "INSERT INTO booking_agent (email, password) VALUES (%s, %s)"
                cursor.execute(query, (email, password))

            elif user_type == 'airline_staff':
                first = request.form['first_name']
                last = request.form['last_name']
                dob = request.form['dob']
                airline = request.form['airline_name']
                query = "INSERT INTO airline_staff (username, password, first_name, last_name, date_of_birth, airline_name) VALUES (%s, %s, %s, %s, %s, %s)"
                cursor.execute(query, (email, password, first, last, dob, airline))
                cursor.execute("INSERT INTO airline_staff_permissions (username, permission_type) VALUES (%s, %s)", (email, 'Operator'))
            
            db.commit()
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('login'))

        except mysql.connector.Error as err:
            flash(f'Error: {err}', 'danger')

    return render_template('register.html')

# 登录页面
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # 检查各类用户
        user_types = {
            'customer': 'SELECT * FROM customer WHERE email=%s AND password=%s',
            'booking_agent': 'SELECT * FROM booking_agent WHERE email=%s AND password=%s',
            'airline_staff': 'SELECT * FROM airline_staff WHERE username=%s AND password=%s'
        }

        for role, query in user_types.items():
            cursor.execute(query, (email, password))
            user = cursor.fetchone()
            if user:
                session['user'] = email
                session['role'] = role
                flash(f'Welcome back, {email}!', 'success')
                return redirect(url_for('dashboard'))

        flash('Invalid login credentials', 'danger')

    return render_template('login.html')

# 用户主页
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    user = session['user']
    role = session['role']
    return render_template('dashboard.html', user=user, role=role)

# 注销
@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
