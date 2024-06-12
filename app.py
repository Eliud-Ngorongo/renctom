from login import register,index,login, dashboard  
from actions import send_invoice, record_rent_payment, check_rent_paid, house_history,house_summary
from prometheus_flask_exporter import PrometheusMetrics
from prometheus_client import Counter, generate_latest, Histogram, Counter
from prometheus_client.exposition import CONTENT_TYPE_LATEST
import time
from flask import Flask, request
from pymongo import MongoClient
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
metrics = PrometheusMetrics(app)

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

# Define Prometheus metrics
REQUEST_COUNT = Counter('flask_app_request_count', 'App Request Count', ['method', 'endpoint', 'http_status'])
REQUEST_LATENCY = Histogram('flask_app_request_latency_seconds', 'Request latency', ['endpoint'])

# Middleware to track request count and latency
@app.before_request
def before_request():
    request.start_time = time.time()

@app.after_request
def after_request(response):
    latency = time.time() - request.start_time
    REQUEST_COUNT.labels(request.method, request.path, response.status_code).inc()
    REQUEST_LATENCY.labels(request.path).observe(latency)
    return response


@app.route('/metrics')
def metrics_endpoint():
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}
    

@app.route('/')
def index_page():
    return index()

@app.route('/register', methods=['GET', 'POST'])
def register_details():
    return register()

@app.route('/login', methods=["GET", "POST"])
def check_login():
    return login()

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard_info():
    return dashboard()

@app.route('/send_invoice', methods=['GET', 'POST'])
def invoices():
    return send_invoice()

@app.route('/record_rent_payment', methods=['GET', 'POST'])
def record_rent():
    return record_rent_payment()

@app.route('/house_history', methods=['GET'])
def history():
    return house_history()

@app.route('/house_summary', methods=['GET'])
def summary():
    return house_summary()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000,debug=True)
