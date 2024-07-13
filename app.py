from flasgger import Swagger
from flask import Flask, jsonify, redirect, render_template, request, session,make_response

from flask_session import Session
from helper import (check_user_existance, delete_user, get_user, save_user,
                    update_user, validate_email, validate_name,
                    validate_password)
from flask_jwt_extended import JWTManager,create_access_token,jwt_required,get_jwt_identity
from datetime import timedelta
app = Flask(__name__)
# created key using uuid package
app.config["SECRET_KEY"]="ccc05e80c8fd4da78a006c67f34995d2"
app.config["JWT_SECRET_KEY"]="ccc05e80c8fd4da78a006c67f34995d2"

#for seconds
# app.config["ACCESS_TOKEN_EXPIRES"]=timedelta(seconds=30)

#for hours
# app.config["ACCESS_TOKEN_EXPIRES"]=timedelta(hours=24)

#for month
app.config["ACCESS_TOKEN_EXPIRES"]=timedelta(days=30)

app.config["SESSION_PERMANENT"] = True
app.config["SESSION_TYPE"] = "mongodb"
Session(app)
jwt=JWTManager(app)

swagger = Swagger(app)

@app.route("/")
def index():
    """
    Index Page
    ---
    responses:
      200:
        description: The home page or login page
    """
    if "logged_in" in session and session["logged_in"]:
        user = get_user(session["email"], session.get("category", ""))
        return render_template("home.html", user_email=user["email"], user_name=user["name"], user_phone=user["phone"], user_category=user["category"])   
    return render_template("login.html")


@app.route("/login", methods=["POST", "GET"])
def login():
    """
    User Login
    ---
    parameters:
      - name: email
        in: formData
        type: string
        required: true
      - name: password
        in: formData
        type: string
        required: true
      - name: category
        in: formData
        type: string
        required: false
    responses:
      200:
        description: Redirects to the home page
      400:
        description: Invalid Email or Password
    """
    
    if request.method == "POST":
        
        user = initialize_user()
        email_is_valid = validate_email(user["email"])
        password_is_valid = validate_password(user["password"])

        if not email_is_valid:
            return render_template("error.html", message="Invalid Email")
        
        if not password_is_valid:
            return render_template("error.html", message="Invalid Password")
        
        
        
        user_exist = check_user_existance(user)

        if user_exist:
            session["logged_in"] = True
            session["email"] = user["email"]
            
            access_token=create_access_token(identity=user["name"])
            return jsonify(access_token=access_token),200
            redirect("/home")      
        else:
            return render_template("error.html", message="Incorrect Email or password")
    
    return render_template("login.html")


@app.route("/signup", methods=["POST", "GET"])

def signup():
    """
    User Signup
    ---
    parameters:
      - name: email
        in: formData
        type: string
        required: true
      - name: name
        in: formData
        type: string
        required: true
      - name: password
        in: formData
        type: string
        required: true
      - name: phone
        in: formData
        type: string
        required: false
      - name: category
        in: formData
        type: string
        required: false
    responses:
      200:
        description: Renders the login page
      400:
        description: Invalid Email, Name, or Password
    """
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


@app.route("/home",methods=["GET","POST"])
@jwt_required
def home():
    """
    User Home
    ---
    responses:
      200:
        description: The home page
      401:
        description: Unauthorized access
    """
    print("home")
    current_user = get_jwt_identity()
    
    if "logged_in" in session and session["logged_in"]:
        user = get_user(session["email"], session.get("category", ""))
        
        return render_template("home.html", user_email=user["email"], user_name=user["name"], user_phone=user["phone"], user_category=user["category"])
    return render_template("login.html")


@app.route("/logout", methods=["POST","GET"])
def logout():
    """
    User Logout
    ---
    responses:
      200:
        description: Redirects to the home page
    """
    session.clear()
    return redirect("/home")


@app.route("/update", methods=["POST"])
def update():
    """
    Update User Information
    ---
    parameters:
      - name: email
        in: formData
        type: string
        required: true
      - name: name
        in: formData
        type: string
        required: true
      - name: phone
        in: formData
        type: string
        required: false
      - name: category
        in: formData
        type: string
        required: false
    responses:
      200:
        description: Updates the user information and renders the home page
      400:
        description: Invalid Input
    """
    password = get_user(session["email"])["password"]
    user = initialize_user()
    user["password"] = password
    update_user(user, session["email"])
    session["email"] = user["email"]

    return render_template("home.html", user_email=user["email"], user_name=user["name"], user_phone=user["phone"], user_category=user["category"])


@app.route("/delete", methods=["POST", "GET"])
def delete():
    """
    Delete User
    ---
    responses:
      200:
        description: Deletes the user and renders the login page
    """
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
