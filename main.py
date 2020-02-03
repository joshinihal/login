from flask import Flask, render_template, request, flash, redirect, session, request, Response,url_for
from functools import wraps
import sys
import os
from werkzeug import generate_password_hash, check_password_hash
from flaskext.mysql import MySQL
import mysql.connector
from mysql.connector import Error

connection = mysql.connector.connect(host='localhost', database='user_data', user='root', password='')
cursor = connection.cursor(buffered=True)


mysql = MySQL()
app = Flask(__name__)
message = ''

mysql.init_app(app)


# defining a decorator to check if user is logged in every route
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'email' in session:
            print("is in session")
            return f(*args, **kwargs)
        flash("You need to be logged in for this operation")
        return redirect(url_for('logout'))   
    return decorated


@app.route('/home')
@login_required
def home():
    return render_template('home.html')

# register account in db for login
@app.route('/registered', methods=['GET', 'POST'])
@login_required
def registered():
    try:
        if request.method == 'POST' and 'inputUsername' in request.form and  'inputEmail' in request.form and 'inputPassword' in request.form:
            email = request.form['inputEmail']
            username = request.form['inputUsername']
            password = request.form['inputPassword']
            repeatPassword = request.form['inputRepeatPassword']
            # check if the re-entered password is same as password
            if repeatPassword == password:
                # generate hash password to save in db
                hashpassword= generate_password_hash(password)
                cursor.execute('INSERT INTO `user` (`user_name`, `user_email`, `user_password`) VALUES (%s,%s,%s) ', (username,email,hashpassword))
                connection.commit()
                regsuccess=True
            else:
                flash("Passwords Don't Match")
                return redirect('/register')
        elif request.method == 'POST':
            msg = 'Please fill out the form!'
    except Exception as e:
        print(e)
    return render_template('loginpage.html', regsuccess= regsuccess)

@app.route('/register')
@login_required
def register():
    return render_template('registerpage.html')

# check for correct login and render homepage
@app.route('/loggedin', methods=['POST'])
def loggedin():
    try:
        print("log in successful")
        _email = request.form['inputEmail']
        _password = request.form['inputPassword']
        if _email and _password and request.method == 'POST':
            sql = "SELECT * FROM user WHERE user_email=%s" 
            sql_where = (_email,)
            cursor.execute(sql, sql_where)
            row = cursor.fetchone()
            # check if email and password match
            if row:
                if check_password_hash(row[3], _password):
                    session['email'] = row[2]
                    admin= session['email']
                    return render_template('home.html')
                else:
                    # redirect for wrong password
                    flash('Invalid password!')
                    return redirect('/login')
            else:
                flash('Invalid email/password!')
                return redirect('/login')
    except Exception as e:
        print(e)

# pop the email from session and logout
@app.route('/logout')
def logout():
    session.pop('email', None)
    return redirect('/')

# home route
@app.route('/')
def index():
    # if loggedin go to homepage or else redirect to loginpage
    if 'email' in session:
        username = session['email']
        return render_template('PTL.html')
    return render_template("loginpage.html")

# login page
@app.route('/login')
def checkinglogin():
    return render_template('loginpage.html')

if __name__ == '__main__':
    app.secret_key = os.urandom(12)
    app.run(debug=True)
    