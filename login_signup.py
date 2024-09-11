# from flask import Flask, request, jsonify
# import sqlite3
# import bcrypt
# from email.utils import parseaddr
# from flask_cors import CORS, cross_origin

# app = Flask(__name__)
# CORS(app, resources={r"/*": {"origins": "*"}})

# def get_db_connection():
#     conn = sqlite3.connect('users.db')
#     conn.row_factory = sqlite3.Row
#     return conn

# def is_valid_email(email):
#     # Check if the email is valid
#     return '@' in parseaddr(email)[1]

# @app.route('/signup', methods=['POST'])
# def signup():
#     data = request.get_json()
#     username = data.get('username')
#     password = data.get('password')
#     email = data.get('email') 

#     if not username or not password or not email:
#         return jsonify({'error': 'Username, password, and email are required'}), 400

#     if not is_valid_email(email):
#         return jsonify({'error': 'Invalid email address'}), 400

#     hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

#     try:
#         conn = get_db_connection()
#         cursor = conn.cursor()
#         cursor.execute('INSERT INTO users (username, password, email) VALUES (?, ?, ?)', 
#                        (username, hashed_password, email))
#         conn.commit()
#         conn.close()
#         return jsonify({'message': 'User created successfully'}), 201
#     except sqlite3.IntegrityError:
#         return jsonify({'error': 'Username already exists'}), 400

# @app.route('/login', methods=['POST'])
# def login():
#     data = request.get_json()
#     username = data.get('username')
#     password = data.get('password')

#     if not username or not password:
#         return jsonify({'error': 'Username and password are required'}), 400

#     conn = get_db_connection()
#     cursor = conn.cursor()
#     user = cursor.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
#     conn.close()

#     if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
#         return jsonify({'message': 'Login successful'}), 200
#     else:
#         return jsonify({'error': 'Invalid username or password'}), 401

# if __name__ == '__main__':
#     app.run(debug=True)

from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from pymongo import MongoClient
import bcrypt
from email.utils import parseaddr

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# MongoDB connection
client = MongoClient('mongodb+srv://asharmetaviz:user123@cluster0.qckme.mongodb.net/')  # Replace with your MongoDB connection URI
db = client['Users_name']  # Database name
users_collection = db['user']  # Collection name

def is_valid_email(email):
    # Check if the email is valid
    return '@' in parseaddr(email)[1]

@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    email = data.get('email') 

    if not username or not password or not email:
        return jsonify({'error': 'Username, password, and email are required'}), 400

    if not is_valid_email(email):
        return jsonify({'error': 'Invalid email address'}), 400

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    try:
        # Check if the username already exists
        if users_collection.find_one({"username": username}):
            return jsonify({'error': 'Username already exists'}), 400

        # Insert user into MongoDB
        users_collection.insert_one({
            'username': username,
            'password': hashed_password,
            'email': email
        })
        return jsonify({'message': 'User created successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400

    # Find user in MongoDB
    user = users_collection.find_one({"username": username})

    if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
        return jsonify({'message': 'Login successful'}), 200
    else:
        return jsonify({'error': 'Invalid username or password'}), 401

if __name__ == '__main__':
    app.run(debug=True)
