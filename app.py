from flask import Flask, jsonify, redirect, render_template, request, session
from flask_session import Session
from helper import (check_user_existance, delete_user, get_user, save_user,
                    update_user, validate_email, validate_name,
                    validate_password)

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = True
app.config["SESSION_TYPE"] = "mongodb"
# nknkjkjdfk

Session(app)

@app.route("/")
def index():
    
    if "logged_in" in session and session["logged_in"]:
        user = get_user(session["email"], session.get("category", ""))
        return render_template("home.html", user_email=user["email"], user_name=user["name"], user_phone=user["phone"], user_category=user["category"])   
    return render_template("login.html")


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        user = initialize_user()

        email_is_valid = validate_email(user["email"])
        password_is_valid = validate_password(user["password"])

        if not email_is_valid:
            return render_template("error.html", message="Invalid Email")
        
        if not password_is_valid:
            return render_template("error.html", message="Invalid Password")
        
        user_data = get_user(user["email"], user["category"])
        user_exist = check_user_existance(user_data)

        if user_exist:
            session["logged_in"] = True
            session["email"] = user["email"]
            return redirect("/home")
        else:
            return render_template("error.html", message="Incorrect Email or password")
    
    return render_template("login.html")


@app.route("/signup", methods=["POST", "GET"])
def signup():
    if request.method == "POST":
        user = initialize_user()

        email_is_valid = validate_email(user["email"])
        name_is_valid = validate_name(user["name"], user["category"])
        password_is_valid = validate_password(user["password"])

        if not email_is_valid:
            return render_template("error.html", message="Invalid Email")
        if not name_is_valid:
            return render_template("error.html", message="Invalid Name")
        if not password_is_valid:
            return render_template("error.html", message="Invalid Password")
        
        save_user(user)
        return render_template("login.html")
    
    return render_template("signup.html")


@app.route("/home")
def home():
    if "logged_in" in session and session["logged_in"]:
        user = get_user(session["email"], session.get("category", ""))
        
        return render_template("home.html", user_email=user["email"], user_name=user["name"], user_phone=user["phone"], user_category=user["category"])
    return render_template("login.html")


@app.route("/logout", methods=["POST","GET"])
def logout():
    session.clear()
    
    return redirect("/home")


@app.route("/update", methods=["POST"])
def update():
    password=get_user(session["email"])["password"]
    user = initialize_user()
    user["password"]=password
    update_user(user, session["email"])
    session["email"] = user["email"]

    return render_template("home.html", user_email=user["email"], user_name=user["name"], user_phone=user["phone"], user_category=user["category"])


@app.route("/delete",methods=["POST","GET"])
def delete():
    delete_user(session["email"])
    session.clear()
    return render_template("login.html")


def initialize_user():
    user = {}
    user["email"] = request.form.get("email")
    user["category"] = request.form.get("category")
    user["name"] = request.form.get("name", get_user(user["email"], user["category"]).get("name", ""))
    user["phone"] = request.form.get("phone", get_user(user["email"], user["category"]).get("phone", ""))
    user["password"] = request.form.get("password")
    return user

if __name__ == '__main__':
    app.run(debug=True)
