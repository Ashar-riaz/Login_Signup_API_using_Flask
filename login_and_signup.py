from flask import Flask, request, jsonify
import bcrypt
from email.utils import parseaddr
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Path to the JSON file
JSON_FILE_PATH = 'users.json'

# Helper function to read users from JSON file
def read_users():
    if os.path.exists(JSON_FILE_PATH):
        with open(JSON_FILE_PATH, 'r') as file:
            return json.load(file)
    return []

# Helper function to write users to JSON file
def write_users(users):
    with open(JSON_FILE_PATH, 'w') as file:
        json.dump(users, file, indent=4)

# Validate email format
def is_valid_email(email):
    return '@' in parseaddr(email)[1]
@app.route('/signup', methods=['POST'])
def signup():
    try:
        data = request.get_json()
        print(f"Received data: {data}")  # Debug print

        username = data.get('username')
        password = data.get('password')
        email = data.get('email')

        if not username or not password or not email:
            return jsonify({'error': 'Username, password, and email are required'}), 400

        if not is_valid_email(email):
            return jsonify({'error': 'Invalid email address'}), 400

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        print(f"Hashed password: {hashed_password}")  # Debug print

        users = read_users()
        print(f"Current users: {users}")  # Debug print

        if any(user['username'] == username for user in users):
            return jsonify({'error': 'Username already exists'}), 400

        users.append({
            'username': username,
            'password': hashed_password,
            'email': email
        })
        write_users(users)
        return jsonify({'message': 'User created successfully'}), 201

    except Exception as e:
        print(f"Error during signup: {e}")  # Debug print
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

        users = read_users()
        user = next((u for u in users if u['username'] == username), None)

        if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            return jsonify({'message': 'Login successful'}), 200
        else:
            return jsonify({'error': 'Invalid username or password'}), 401

    except Exception as e:
        return jsonify({'error': 'An error occurred during login'}), 500

# Main function to run the app
if __name__ == '__main__':
    if not os.path.exists(JSON_FILE_PATH):
        write_users([])  # Create an empty JSON file if it doesn't exist
    app.run(debug=True)
