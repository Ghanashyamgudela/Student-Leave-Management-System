from flask import Flask, render_template, request, redirect, session, flash
from flask_mysqldb import MySQL
import MySQLdb.cursors

app = Flask(__name__)
app.secret_key = "xyz123"

# Load config from config.py
app.config.from_pyfile('config.py')
mysql = MySQL(app)

# ---------------- STUDENT REGISTRATION ----------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT * FROM student WHERE email=%s", (email,))
        account = cur.fetchone()

        if account:
            flash("Email already registered! Please login.")
            return redirect('/register')

        # Correct insert: do NOT include student_id
        cur.execute("INSERT INTO student(full_name, email, password) VALUES (%s, %s, %s)",
                    (name, email, password))
        mysql.connection.commit()

        flash("Registration successful! Please login.")
        return redirect('/')
    
    return render_template('register.html')


# ---------------- STUDENT LOGIN ----------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT * FROM student WHERE email=%s AND password=%s",
                    (email, password))
        user = cur.fetchone()

        if user:
            session['student_id'] = user['student_id']
            session['student_name'] = user['full_name']
            return redirect('/student/dashboard')
        else:
            flash("Invalid email or password")
            return redirect('/')

    return render_template('login.html')


# ---------------- STUDENT DASHBOARD ----------------
@app.route('/student/dashboard')
def student_dashboard():
    if 'student_id' not in session:
        return redirect('/')
    return render_template('student_dashboard.html')


# ---------------- APPLY LEAVE ----------------
@app.route('/student/apply_leave', methods=['GET','POST'])
def apply_leave():
    if 'student_id' not in session:
        return redirect('/')

    # Fetch student details
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM student WHERE student_id=%s", (session['student_id'],))
    student = cur.fetchone()

    if request.method == 'POST':
        reason = request.form['reason']
        from_date = request.form['from_date']
        to_date = request.form['to_date']

        cur.execute("""INSERT INTO leave_requests(student_id, reason, from_date, to_date, status)
                       VALUES(%s, %s, %s, %s, %s)""",
                    (session['student_id'], reason, from_date, to_date, "Pending"))
        mysql.connection.commit()

        flash("Leave applied successfully!")
        return redirect('/student/dashboard')

    # Pass student to template
    return render_template('apply_leave.html', student=student)



# ---------------- STUDENT VIEW LEAVE HISTORY ----------------
@app.route('/student/my_leaves')
def my_leaves():
    if 'student_id' not in session:
        return redirect('/')

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM leave_requests WHERE student_id=%s ORDER BY from_date DESC",
                (session['student_id'],))
    leaves = cur.fetchall()
    return render_template('my_leaves.html', leaves=leaves)


# ---------------- ADMIN LOGIN ----------------
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT * FROM admins WHERE username=%s AND password=%s",
                    (username, password))
        admin = cur.fetchone()

        if admin:
            session['admin_id'] = admin['id']
            session['admin_name'] = admin['username']
            return redirect('/admin/dashboard')
        else:
            flash("Invalid admin credentials")
            return redirect('/admin/login')

    return render_template('admin_login.html')


# ---------------- ADMIN DASHBOARD ----------------
@app.route('/admin/dashboard')
def admin_dashboard():
    if 'admin_id' not in session:
        return redirect('/admin/login')
    return render_template('admin_dashboard.html')


# ---------------- ADMIN VIEW LEAVE REQUESTS ----------------
@app.route('/admin/requests')
def admin_requests():
    if 'admin_id' not in session:
        return redirect('/admin/login')

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("""
        SELECT lr.id, s.full_name, lr.reason, lr.from_date, lr.to_date, lr.status
        FROM leave_requests lr
        JOIN student s ON lr.student_id = s.student_id
        ORDER BY lr.from_date DESC
    """)
    data = cur.fetchall()
    return render_template("view_leave_requests.html", data=data)


# ---------------- APPROVE / REJECT LEAVE ----------------
@app.route('/admin/update/<int:id>/<string:action>')
def update_status(id, action):
    if 'admin_id' not in session:
        return redirect('/admin/login')

    new_status = "Approved" if action == "approve" else "Rejected"
    cur = mysql.connection.cursor()
    cur.execute("UPDATE leave_requests SET status=%s WHERE id=%s", (new_status, id))
    mysql.connection.commit()

    return redirect('/admin/requests')

@app.route('/student/profile')
def student_profile():
    if 'student_id' not in session:
        return redirect('/')
    
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM student WHERE student_id=%s", (session['student_id'],))
    student = cur.fetchone()
    
    return render_template('profile.html', student=student)

# ---------------- ADMIN REPORTS ----------------
@app.route('/admin/reports')
def admin_reports():
    if 'admin_id' not in session:
        return redirect('/admin/login')

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # Total leave requests
    cur.execute("SELECT COUNT(*) AS total_requests FROM leave_requests")
    total = cur.fetchone()['total_requests']

    # Approved leave requests
    cur.execute("SELECT COUNT(*) AS approved FROM leave_requests WHERE status='Approved'")
    approved = cur.fetchone()['approved']

    # Rejected leave requests
    cur.execute("SELECT COUNT(*) AS rejected FROM leave_requests WHERE status='Rejected'")
    rejected = cur.fetchone()['rejected']

    # Pending leave requests
    cur.execute("SELECT COUNT(*) AS pending FROM leave_requests WHERE status='Pending'")
    pending = cur.fetchone()['pending']

    # Optional: leaves per student
    cur.execute("""
        SELECT s.full_name, COUNT(lr.id) AS total_leaves,
               SUM(lr.status='Approved') AS approved,
               SUM(lr.status='Rejected') AS rejected,
               SUM(lr.status='Pending') AS pending
        FROM leave_requests lr
        JOIN student s ON lr.student_id = s.student_id
        GROUP BY s.student_id
        ORDER BY s.full_name
    """)
    student_summary = cur.fetchall()

    return render_template('admin_reports.html',
                           total=total,
                           approved=approved,
                           rejected=rejected,
                           pending=pending,
                           student_summary=student_summary)

# ---------------- LOGOUT ----------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/choose')
def choose_user():
    return render_template('choose_user.html')
@app.route('/')
def home():
    return redirect('/choose')
# ---------------- ADMIN VIEW STUDENTS ----------------
@app.route('/admin/students')
def admin_view_students():
    if 'admin_id' not in session:
        return redirect('/admin/login')

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM student ORDER BY full_name ASC")
    students = cur.fetchall()
    return render_template('admin_students.html', students=students)

if __name__ == "__main__":
    app.run(debug=True)
