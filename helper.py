import re

import bcrypt
from flask import Flask, jsonify, render_template, request
from flask_pymongo import PyMongo


app = Flask(__name__)
# 103.31.100.66
app.config['MONGO_URI'] = "mongodb://localhost:27017/testing"
db = PyMongo(app).db



def validate_password(password):
    return len(password)>=6
 
#check wether username already exist or not
def validate_name(name,category):
        
        user=db.test1.find({"name":name,"category":category})
        return len(list(user)) == 0
    


def validate_email(email):
    # Regular expression pattern for basic email validation
    pattern = r'^[\w\.-]+@[a-zA-Z\d\.-]+\.[a-zA-Z]{2,}$'
    
    # Compile the pattern into a regex object
    regex = re.compile(pattern)

    # Check if the email matches the regex pattern
    if regex.match(email):
            return True
    
    return False
# def check_user_existance(

def encrypt_password(password):
    hashed=bcrypt.hashpw(password.encode("utf-8"),bcrypt.gensalt())
    return hashed


def verify_password(password,hash_password):
    return bcrypt.checkpw(password.encode("utf-8"),hash_password)

def check_user_existance(user):
    
    
    
    print(user)
    tempchk=db.test1.find_one( {"name":user["name"] , "email":user["email"] , "category" : user["category"]})
    
    if tempchk is not None and verify_password(user["password"],tempchk["password"]):
         
         return True
    
    return False
    
    
def save_user(user):
     user["password"]=encrypt_password(user["password"])        
     db.test1.insert_one(user)

def delete_user(email):
    
    
    db.test1.delete_one({"email":email})

    

def update_user(USER:dict,email:str):

        
        db.test1.update_one(    {"email":email},{"$set":USER  }   )  
        
     
def get_user(email,category=""):
     user=db.test1.find_one({"email":email})
     
     if user is not None:
        return user     
     else:
          r={"name":" ","phone":""}
          return r
     

