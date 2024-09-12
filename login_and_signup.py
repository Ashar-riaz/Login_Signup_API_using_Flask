from flask import Flask, request, jsonify
import bcrypt
from email.utils import parseaddr
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# File path for storing user data
USER_DATA_FILE = 'users.json'

# Load users from JSON file
def load_users():
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, 'r') as f:
            return json.load(f)
    return []

# Save users to JSON file
def save_users(users):
    with open(USER_DATA_FILE, 'w') as f:
        json.dump(users, f)

# Validate email format
def is_valid_email(email):
    return '@' in parseaddr(email)[1]

# Signup route
@app.route('/signup', methods=['POST'])
def signup():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')

        if not username or not password or not email:
            return jsonify({'error': 'Username, password, and email are required'}), 400

        if not is_valid_email(email):
            return jsonify({'error': 'Invalid email address'}), 400

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        users = load_users()

        # Check if username already exists
        if any(user['username'] == username for user in users):
            return jsonify({'error': 'Username already exists'}), 400

        users.append({'username': username, 'password': hashed_password, 'email': email})
        save_users(users)
        return jsonify({'message': 'User created successfully'}), 201

    except Exception as e:
        return jsonify({'error': f'An error occurred during signup: {str(e)}'}), 500

# Login route
@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400

        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({'error': 'Username and password are required'}), 400

        users = load_users()
        user = next((user for user in users if user['username'] == username), None)

        if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            return jsonify({'message': 'Login successful'}), 200
        else:
            return jsonify({'error': 'Invalid username or password'}), 401

    except Exception as e:
        return jsonify({'error': f'An error occurred during login: {str(e)}'}), 500

# Main function to run the app
if __name__ == '__main__':
    app.run(debug=True)
