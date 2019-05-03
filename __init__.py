from flask import Flask, render_template, url_for, flash, redirect, request, session, make_response, send_file
from wtforms import Form, BooleanField, TextField, PasswordField, validators
from datetime import datetime, timedelta
from pymysql import escape_string as thwart
from functools import wraps
import gc
from passlib.hash import sha256_crypt
from pymysql import escape_string as thwart
import os, sys; sys.path.append(os.path.dirname(os.path.realpath(__file__)))
from werkzeug.utils import secure_filename
from content import Content
from db_connect import connection
from flask_socketio import SocketIO
import json
import sqlite3 as lite
import time

DATABASE = "/var/www/FlaskApp/FlaskApp/database_example/database_example.db"
#input_data = "bananas"
#output_data = "cookies"

def message(user_name,topic,message): # creating my table and the parts that will be put into it. Must be run in the command line by running the fucntion if the table is deleted to restart it.
    con = lite.connect(DATABASE)
    c = con.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS input_log(id INTEGER PRIMARY KEY AUTOINCREMENT, user_name TEXT, topic TEXT, message TEXT)")
    c.execute("INSERT INTO input_log (user_name,topic,message) VALUES (?,?,?)",(user_name, topic, message))
    con.commit()
    c.close()
    return


def contents():
    con = lite.connect(DATABASE)
    c = con.cursor()
    c.execute("SELECT * FROM input_log")
    rows = c.fetchall() # there is also fetchone() this returns a list
    con.close()
    return reversed(rows)
    


# constants / globals
UPLOAD_FOLDER = "/var/www/FlaskApp/FlaskApp/uploads"

ALLOWED_EXTENSIONS = set(["txt", "pdf", "png", "jpg", "jpeg", "gif"])


app = Flask(__name__) # builds our web app

app.config['SECRET_KEY'] = 'ThIsIsAsEcReTkEy'
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

socketio = SocketIO(app)

def allowed_file(filename): # this is to check for our allowed extensions
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs): # defined the wraps and the *args will allow multiple arguements and **kwargs is keyword arguements
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash("Please login.")
            return redirect(url_for('login'))
    return wrap
          
    

APP_CONTENT = Content()

@app.route("/", methods=["GET", "POST"])     
def index():
    error = ""
    try:
        c, conn = connection()
        if request.method == "POST":
            
            data = c.execute("SELECT * FROM users WHERE username = ('{0}')".format(thwart(request.form['username'])))
            
            data = c.fetchone()[2]
            
            if sha256_crypt.verify(request.form["password"], data):
                session['logged_in'] = True
                session['username'] = request.form['username']
                
                flash("You are now logged in "+session['username']+"!")
                return redirect(url_for("message_page"))
            
            else: 
                error = "Invalid creditials, try again." # want this the same as below because then the hacker does not know what the error is.
                
        return render_template("main.html", error = error)
    
    except Exception as e:
        flash(e) # remember to remove! For debugging only!
        error = "Invalid creditials, try again." # this is extremely strict and will not tell the hacker what error it is
        return render_template("main.html", error = error)

## ABOUT

@app.route("/about/", methods=["GET", "POST"])
def about():
    error = ""
    try:
        c, conn = connection()
        if request.method == "POST":
            
            data = c.execute("SELECT * FROM users WHERE username = ('{0}')".format(thwart(request.form['username'])))
            
            data = c.fetchone()[2]
            
            if sha256_crypt.verify(request.form["password"], data):
                session['logged_in'] = True
                session['username'] = request.form['username']
                
                flash("You are now logged in "+session['username']+"!")
                return redirect(url_for("message_page"))
            
            else: 
                error = "Invalid creditials, try again." # want this the same as below because then the hacker does not know what the error is.
        return render_template("about.html")
    except Exception as e:
        return render_template("500.html", error = e) 
    
## DASHBOARD
    
@app.route("/dashboard/")
@login_required
def dashboard():
    try:
        return render_template("dashboard.html", APP_CONTENT = APP_CONTENT)
    except Exception as e:
        return render_template("500.html", error = e)
    
## LOGIN

@app.route("/login/", methods=["GET", "POST"])
def login():
    error = ""
    try:
        c, conn = connection()
        if request.method == "POST":
            
            data = c.execute("SELECT * FROM users WHERE username = ('{0}')".format(thwart(request.form['username'])))
            
            data = c.fetchone()[2]
            
            if sha256_crypt.verify(request.form["password"], data):
                session['logged_in'] = True # logged_in is the key and value is True
                session['username'] = request.form['username']
                
                flash("You are now logged in "+session['username']+"!")
                return redirect(url_for("message_page"))
            
            else: 
                error = "Invalid creditials, try again." # want this the same as below because then the hacker does not know what the error is.
                
        return render_template("login.html", error = error)
    
    except Exception as e:
        flash(e) # remember to remove! For debugging only!
        error = "Invalid creditials, try again." # this is extremely strict and will not tell the hacker what error it is
        return render_template("login.html", error = error)
    
## LOGOUT

@app.route("/logout/")
@login_required
def logout():
    session.clear() # will delete the cookie
    flash("You have been logged out!")
    gc.collect()
    return redirect(url_for("index"))
        
class RegistrationForm(Form):
    username = TextField("Username", [validators.Length(min=4, max=20)])
    email = TextField("PSU Email Address", [validators.Length(min=6, max=50)])
    password = PasswordField("New Password", [validators.Required(), 
                validators.EqualTo('confirm', message ="Passwords must match")])
    confirm = PasswordField("Repeat Password")
    accept_tos = BooleanField("I accept the Terms of Service and Privacy Notice", [validators.Required()])

## REGISTER

@app.route("/register/", methods=["GET","POST"])
def register_page():
    try:
        form = RegistrationForm(request.form)
        
        if request.method == "POST" and form.validate():
            username = form.username.data
            email = form.email.data
            password = sha256_crypt.encrypt((str(form.password.data)))
            # this encrypts the password information then stores it in our database
            
            c, conn = connection() # if it runs, it will post a string
            
            x = c.execute("SELECT * FROM users WHERE username = ('{0}')".format((thwart(username))))
            
            if int(x) > 0:
                flash("That username is already taken, please choose another.")
                return render_template("register.html", form=form)
            else:
                c.execute("INSERT INTO users(username, password, email, tracking) VALUES ('{0}','{1}','{2}','{3}')".format(thwart(username),thwart(password),thwart(email),thwart("/dashboard/")))

            conn.commit() # save your registration to MySQLdb
            flash("Thanks for registering, "+username+"!")
            c.close() # close user
            conn.close() # close connection
            gc.collect() # garbage collection with Python

            session['logged_in'] = True
            session['username'] = username

            return redirect(url_for("message_page"))
        return render_template("register.html", form=form)
    except Exception as e:
        return(str(e)) # remember to remove! For debugging only!
    
## TERMS OF SERVICE

@app.route("/tos/")
def tos():
    return render_template("tos.html")


## UPLOADS

@app.route("/uploads/", methods=["GET", "POST"])
@login_required
def upload_file():
    try:
        if request.method == "POST":
            if "file" not in request.files:
                flash("No file part")
                return redirect(request.url)
            file = request.files["file"]
            
            if file.filename =="":
                flash("No selected file")
                return redirect(request.url)
            
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
                flash("File" + str(filename) + "upload successful!")
                return render_template('uploads.html', filename = filename)
        return render_template("uploads.html")
        
    except Exception as e:
        return(str(e)) # remember to remove! For debugging only!
    
## DOWNLOAD

@app.route("/download/")
@login_required
def download():
    try:
        return send_file("/var/www/FlaskApp/FlaskApp/uploads/cat.jpg", attachment_filename="kitties.jpg")
        
    except Exception as e:
        return str(e)
    
## WELCOME

@app.route("/welcome/")
@login_required
def welcome():
    try:
        #This is where all the python goes!
        
        def my_function():
            output = ["DIGIT 400 is good.", "Python, Java, php, SQL, C++", "<p><strong>Hello World<strong></p>", 42, "42"]
            return output
        
        output = my_function()
        
        return render_template("templating_demo.html", output = output)
        
    except Exception as e:
        return str(e) # remember to remove! For debugging only!
    
## HELLO WORLD

@app.route("/message/", methods=["GET", "POST"])
@login_required
def message_page():
    try:
        content = ""
        if request.method == "POST":
            
            data = thwart(request.form['message'])
            topic = thwart(request.form['topic'])
            
            name = session['username']
            message(name, topic, data)
            
            content = contents()
            flash("Thanks for your message!")
            return render_template("message.html", content = content)
        
        content = contents()
        return render_template("message.html", content = content)
    
    except Exception as e:
        return str(e) # remember to remove! For debugging only!
        

## SITEMAP

@app.route("/sitemap.xml/", methods=["GET"])
def sitemap():
    try:
        pages = []
        week = ((datetime.now()) - timedelta(days = 7)).date().isoformat()
        for rule in app.url_map.iter_rules():
            if "GET" in rule.methods and len(rule.arguments)==0:
                pages.append(["http://68.183.19.24"+str(rule.rule), week])
            
        sitemap_xml = render_template("sitemap_template.xml", pages = pages)
        response = make_response(sitemap_xml)
        response.headers["Content-Type"] = "application/xml"
        return response
    
    except Exception as e:
        return(str(e)) # remember to remove! For debugging only!
    
## ROUGE ROBOTS

@app.route("/robots.txt")
def robots():
    return("User-agent: \nDisallow: /login \nDisallow: /register")

## Error Handlers

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")

@app.errorhandler(405)
def method_not_allowed(e):
    return render_template("405.html")

@app.errorhandler(500)
def int_server_error(e):
    return render_template("500.html", error = e)

if __name__ == "__main__":
    app.run(debug=True) # should be turned off/False for production!