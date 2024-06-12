from flask import Flask, request, jsonify, render_template, redirect, session, url_for
from pymongo import MongoClient
from datetime import datetime
from pymongo.server_api import ServerApi
import os
from bson.objectid import ObjectId

app = Flask(__name__ ,  template_folder='frontend/templates')
app.secret_key = os.urandom(24)
mongodb_password = os.environ.get('MONGODB_PASSWORD') # Retrieve the MongoDB password from the environment variable
mongo_uri = f'mongodb+srv://eliudnjenga:{mongodb_password}@rentco.hcmmfxk.mongodb.net/?retryWrites=true&w=majority'
client = MongoClient(mongo_uri, server_api=ServerApi('1'))  
db = client['rental_db'] 
users = db['users']
invoices = db['invoices']
rent_payments = db['rent_payments']
water_readings= db['water_readings']


# Route to render the login page as the first point of entry
@app.route('/')
def index():
    return render_template('index.html')

# User registration
def register():
   if request.method == 'GET':
       return render_template('register.html')
   data = request.form
   name = data.get('name')
   id_number = data.get('id_number')
   email = data.get('email')
   house_number = data.get('house_number')
   phone_number = data.get('phone_number')
    
   if not name or not id_number or not email or not house_number or not phone_number:
        return jsonify({'error': 'Name, ID number, email, house number, and phone number are required'}), 400
    
   existing_user = users.find_one({'house_number': house_number})
   if existing_user:
        return jsonify({'error': f'A user with house number {house_number} already exists'}), 409
    
   user_data = {
        'name': name,
        'id_number': id_number,
        'email': email,
        'house_number': house_number,
        'phone_number': phone_number,
        'role': 'user'  # Regular user role
    }
   users.insert_one(user_data)
    
   return render_template('/homepage.html', house_number=house_number, name=name)  # Redirect to home page after successful registration


# User login
def login():
    if request.method == "POST":
        house_number = request.form["house_number"]

        user = users.find_one({"house_number": house_number})
        if user:
            name = user.get('name')

        if user:
            session["house_number"] = house_number  
            return render_template("homepage.html", name=name, house_number=house_number)  # Redirect to dashboard on successful login
        else:
            return "Invalid username"

    return render_template("login.html")

# # User logout
# def logout():
#     session.pop('id_number', None)  # Remove ID number from session
#     return jsonify({'message': 'Logout successful'}), 200

# user dashboard    
def dashboard():
   house_number = session.get("house_number")
    
   if not house_number:
        return jsonify({'error': 'House number is required'}), 400
    
    # Find invoices for the given house number
   user_invoices = list(invoices.find({'user_id': house_number}))
   total_invoiced_amount = sum(int(invoice['amount']) for invoice in user_invoices)
    
    # Find rent payments for the given house number
   user_payments = list(rent_payments.find({'house_number': house_number}))
   total_paid_amount = sum(payment['amount'] for payment in user_payments)
    
    # Calculate balance
   balance = total_invoiced_amount - total_paid_amount
    
    # Sort invoices and payments by date
   user_invoices.sort(key=lambda x: x['date'])
   user_payments.sort(key=lambda x: x['date'])
    
   return render_template("dashboard.html", 
                           house_number=house_number, 
                           invoices=user_invoices, 
                           payments=user_payments, 
                           balance=balance)