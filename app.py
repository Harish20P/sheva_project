from flask import Flask, request, jsonify, render_template, redirect, url_for
from pymongo import MongoClient
from bcrypt import hashpw, gensalt, checkpw
import os
from werkzeug.utils import secure_filename
import pandas as pd

app = Flask(__name__)

# MongoDB connection
client = MongoClient("mongodb+srv://harish:harish20@cluster0.amazss0.mongodb.net/")
db = client['User_Details']
admins_collection = db['admins']
students_collection = db['students']

# Configure upload folder and allowed extensions
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'xlsx', 'xls'}

# Helper function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def home():
    # Render main page of the website
    return render_template('index.html')

@app.route('/admin-signup', methods=['GET', 'POST'])
def admin_signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if not username or not password:
            return jsonify({"error": "Username and password are required!"}), 400
        
        # Hash the password (ensure it is encoded as bytes)
        hashed_password = hashpw(password.encode('utf-8'), gensalt())
        admins_collection.insert_one({"username": username, "password": hashed_password})
        
        # Redirect to admin page after successful signup
        return redirect(url_for('admin_page'))
    
    return render_template('admin_signup.html')

@app.route('/student-signup', methods=['GET', 'POST'])
def student_signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if not username or not password:
            return jsonify({"error": "Username and password are required!"}), 400
        
        # Hash the password (ensure it is encoded as bytes)
        hashed_password = hashpw(password.encode('utf-8'), gensalt())
        students_collection.insert_one({"username": username, "password": hashed_password})
        
        # Redirect to login page after successful signup
        return redirect(url_for('login'))
    
    return render_template('student_signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        role = request.form.get('role')
        username = request.form.get('username')
        password = request.form.get('password')

        if not role or not username or not password:
            return jsonify({"error": "Role, username, and password are required!"}), 400

        # Choose collection based on role
        collection = admins_collection if role == 'admin' else students_collection
        user = collection.find_one({"username": username})

        if user and checkpw(password.encode('utf-8'), user['password']):
            # Redirect to main page after successful login
            return redirect(url_for('main_page_view'))  # Fix here
        else:
            return jsonify({"message": "Invalid credentials!"})
    
    return render_template('login.html')

@app.route('/admin-page')
def admin_page():
    return "<h1>Welcome, Admin!</h1><p>This is the admin page.</p>"

@app.route('/main-page', methods=['GET', 'POST'])
def main_page_view():
    sheet_data = []
    
    # Handle file upload and sheet parsing
    if request.method == 'POST':
        if 'sheet' not in request.files:
            return jsonify({"error": "No file part"}), 400
        
        file = request.files['sheet']
        
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # Read the sheet data with pandas
            df = pd.read_excel(filepath)
            
            # Convert to JSON format (list of dictionaries)
            sheet_data = df.to_dict(orient='records')

    return render_template('main_page.html', sheet_data=sheet_data)

@app.route('/logout')
def logout():
    # Implement logic for sign-out (redirect to home page)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)