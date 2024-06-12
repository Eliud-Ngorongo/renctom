from flask import Flask, request, jsonify, render_template, redirect, session, url_for
from pymongo import MongoClient
from datetime import datetime
from pymongo.server_api import ServerApi
import os

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


@app.route('/send_invoice', methods=['GET', 'POST'])
def send_invoice():
    # if not current_user.is_authenticated or current_user.role != 'admin':
    #     return jsonify({'error': 'Unauthorized access'}), 401
    
    if request.method == 'GET':
        return render_template('send_invoice.html')
    
    house_number = request.form.get('house_number')
    amount = request.form.get('amount')
    
    if not house_number or not amount:
        return jsonify({'error': 'House number and amount are required'}), 400
    
    existing_user = users.find_one({'house_number': house_number})
    if not existing_user:
        return jsonify({'error': 'User not found'}), 404
    
    invoice_data = {
        'user_id': house_number,
        'amount': amount,
        'date': datetime.now()  # Get current date and time
    }
    invoices.insert_one(invoice_data)
    if request.method == 'POST':
         return redirect(url_for('dashboard_info', house_number=house_number))
    
    return jsonify({'message': f'Invoice sent to user with house number {house_number} for amount {amount}'}), 200


@app.route('/record_rent_payment', methods=['GET', 'POST'])
def record_rent_payment():
    if request.method == 'POST':
        # # Check if the user is authorized (you may adjust this as needed)
        # if 'id_number' not in session or users.find_one({'id_number': session['id_number'], 'role': 'admin'}) is None:
        #     return jsonify({'error': 'Unauthorized access'}), 401

        # Get data from the form
        house_number = request.form.get('house_number')
        amount = request.form.get('amount')
        
        # Validate input
        if not house_number or not amount:
            return render_template('record_rent.html', error='House number and amount are required')

        # Convert amount to float (assuming rent amount can have decimals)
        try:
            amount = float(amount)
        except ValueError:
            return render_template('record_rent.html', error='Amount must be a valid number')

        # Record rent payment
        date = datetime.now()
        rent_payment_data = {
            'house_number': house_number,
            'amount': amount,
            'date': date
        }
        rent_payments.insert_one(rent_payment_data)

        # Update invoice status
        house_invoices = list(invoices.find({'user_id': house_number}))
        total_invoiced_amount = sum(int(invoice['amount']) for invoice in house_invoices)
        
        rent_payments_cursor = rent_payments.find({'house_number': house_number})
        total_paid_amount = sum(payment['amount'] for payment in rent_payments_cursor)
        
        balance = total_invoiced_amount - total_paid_amount
        
        if balance == 0:
            status = "paid"
        elif balance > 0:
            status = "partially paid"
        elif balance < 0:
            status = "Overpaid"
        
        # Update invoice status
        invoices.update_many({'user_id': house_number}, {'$set': {'status': status}})
        
        return render_template('homepage.html', message=f'Rent payment recorded for house number {house_number}. Invoices updated to "{status}"')

    # If the method is GET, render the form
    return render_template('record_rent.html'), 200
    

# Route to retrieve detailed history of invoices and payments for a house number

def house_history():
    house_number = session.get("house_number")
    
    if not house_number:
        return jsonify({'error': 'House number is required'}), 400
    
    # Find invoices for the given house number
    house_invoices = list(invoices.find({'user_id': house_number}))

    # Find rent payments for the given house number
    rent_payments_cursor = rent_payments.find({'house_number': house_number})
    total_invoices = sum(int(invoice['amount']) for invoice in house_invoices)
    total_receipts = sum(payment['amount'] for payment in rent_payments_cursor)
    account_balance = total_invoices - total_receipts
    
    
    # Prepare detailed history list
    history = []
    
    # Add invoices to history
    for invoice in house_invoices:
        history.append({
            'type': 'Invoice Sent',
            'amount': invoice['amount'],
            'date': invoice['date']
        })
    
    rent_payments_cursor = rent_payments.find({'house_number': house_number})
    # Add payments to history
    for payment in rent_payments_cursor:
        history.append({
            'type': 'Payment Received',
            'amount': payment['amount'],
            'date': payment['date']
        })
    # Sort history by date
    history.sort(key=lambda x: x['date'])
    
    return render_template("house_history.html", history=history, house_number=house_number, balance=account_balance), 200

# Route to retrieve invoices and payments for a house number

def house_summary():
    house_number = session.get("house_number")
    
    if not house_number:
        return jsonify({'error': 'House number is required'}), 400
    
    # Find invoices for the given house number
    house_invoices = list(invoices.find({'user_id': house_number}))
    total_invoiced_amount = sum(int(invoice['amount']) for invoice in house_invoices)
    
    # Find rent payments for the given house number
    rent_payments_cursor = rent_payments.find({'house_number': house_number})
    total_paid_amount = sum(payment['amount'] for payment in rent_payments_cursor)
    
    # Calculate balance
    balance = total_invoiced_amount - total_paid_amount
    
    # Prepare response data
    response_data = {
        'house_number': house_number,
        'total_invoiced_amount': total_invoiced_amount,
        'total_paid_amount': total_paid_amount,
        'balance': balance
    }
    
    return render_template("house_summary.html", summary=response_data), 200

# Route to check if rent has been paid for a house number and calculate the balance
@app.route('/check_balance', methods=['POST'])
def check_rent_paid():
    data = request.json
    house_number = data.get('house_number')
    
    if not house_number:
        return jsonify({'error': 'House number is required'}), 400
    
    # Find invoices for the given house number
    house_invoices = list(invoices.find({'user_id': house_number}))
    
    # Calculate total invoiced amount
    total_invoiced_amount = sum(invoice['amount'] for invoice in house_invoices)
    
    # Find rent payments for the given house number
    rent_payments_cursor = rent_payments.find({'house_number': house_number})
    
    # Calculate total amount paid
    total_paid_amount = sum(payment['amount'] for payment in rent_payments_cursor)
    
    # Calculate balance
    balance = total_invoiced_amount - total_paid_amount
    
    if balance == 0:
        return jsonify({'message': f'Rent has been paid in full for house number {house_number}'}), 200
    elif balance > 0:
        return jsonify({'message': f'Rent balance for house number {house_number} is {balance}'}), 200
    else:
        return jsonify({'error': f'Total paid amount exceeds total invoiced amount for house number {house_number}'}), 500