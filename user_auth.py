from flask import Flask, request, jsonify
import sqlite3
import bcrypt
from email.utils import parseaddr
from flask_cors import CORS
import traceback

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Database setup
def create_db():
    try:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                email TEXT NOT NULL
            )
        ''')
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error creating database: {e}")
        traceback.print_exc()

# Helper function to get database connection
def get_db_connection():
    try:
        conn = sqlite3.connect('users.db')
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        traceback.print_exc()
        return None

# Validate email format
def is_valid_email(email):
    return '@' in parseaddr(email)[1]

# Signup route
@app.route('/signup', methods=['POST'])
def signup():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')

        if not username or not password or not email:
            return jsonify({'error': 'Username, password, and email are required'}), 400

        if not is_valid_email(email):
            return jsonify({'error': 'Invalid email address'}), 400

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        conn = get_db_connection()
        if conn is None:
            return jsonify({'error': 'Database connection error'}), 500

        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (username, password, email) VALUES (?, ?, ?)', 
                       (username, hashed_password, email))
        conn.commit()
        conn.close()
        return jsonify({'message': 'User created successfully'}), 201

    except Exception as e:
        print(f"Error during signup: {e}")
        traceback.print_exc()
        return jsonify({'error': 'An error occurred during signup'}), 500

# Login route
@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({'error': 'Username and password are required'}), 400

        conn = get_db_connection()
        if conn is None:
            return jsonify({'error': 'Database connection error'}), 500

        cursor = conn.cursor()
        user = cursor.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()

        if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
            return jsonify({'message': 'Login successful'}), 200
        else:
            return jsonify({'error': 'Invalid username or password'}), 401

    except Exception as e:
        print(f"Error during login: {e}")
        traceback.print_exc()
        return jsonify({'error': 'An error occurred during login'}), 500

# Main function to run the app
if __name__ == '__main__':
    create_db()  # Create database and users table if they don't exist
    app.run(debug=True)
