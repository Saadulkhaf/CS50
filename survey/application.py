import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required


# Configure application
app = Flask(__name__)

# Reload templates when they are changed
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("sqlite:///survey.db")

@app.after_request
def after_request(response):
    """Disable caching"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":

        if not request.form.get("username"):
            return render_template("error1.html", message="Provide user name")

        elif not request.form.get("password"):
            return render_template("error1.html", message="Provide password")

        elif not request.form.get("password") == request.form.get("confirmation"):
            return render_template("error1.html", message="Passwords don't match")

        hash = generate_password_hash(request.form.get("password"))
        new_user_id = db.execute("INSERT INTO tenants (username, hash) VALUES (:username, :hash)",
                                username = request.form.get("username"),
                                hash=hash)

        if not new_user_id:
            return render_template("error1.html", message="User name alraedy taken")

        session["user_id"]=new_user_id

        flash("Registered!")

        return redirect("/")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return render_template("error.html", message="Provide username")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template("error.html", message="Provide Password")

        # Query database for username
        rows = db.execute("SELECT * FROM tenants WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return render_template("error.html", message="Invalid Username or Password")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")



@app.route("/", methods=["GET"])
@login_required
def get_index():
    return redirect("/form")


@app.route("/form", methods=["GET"])
@login_required
def get_form():
    return render_template("form.html")


@app.route("/form", methods=["POST"])
@login_required
def post_form():
    if not request.form.get("name") or not request.form.get("room") or not request.form.get("phone"):
        return render_template("error.html", message="Danger! Learn how to fill a form you idiot")

    new_name = request.form.get("name")
    new_room = request.form.get("room")
    new_phone = request.form.get("phone")
    print(f"{new_name}")
    db.execute(f"INSERT INTO tenants ( name, room, phone) VALUES( '{new_name}', '{new_room}', '{new_phone}')")
    return redirect("/sheet")


    # file = open("survey.csv", "a")
    # writer = csv.writer(file)
    # writer.writerow((request.form.get("name"), request.form.get("room"), request.form.get("phone")))
    # file.close()
    # return redirect("/sheet")

@app.route("/sheet", methods=["GET"])
@login_required
def get_sheet():
    rows = db.execute("SELECT * FROM tenants ")
    print(f"{rows}")
    return render_template("sheet1.html", rows=rows)

    # file = open("survey.csv", "r")
    # reader = csv.reader(file)
    # tenants = list(reader)
    # return render_template("sheet.html", tenants=tenants)