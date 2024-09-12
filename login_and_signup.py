from flask import Flask, request, jsonify
import bcrypt
from email.utils import parseaddr
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# In-memory storage for users
users = []

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

        # Check if username already exists
        for user in users:
            if user['username'] == username:
                return jsonify({'error': 'Username already exists'}), 400

        users.append({'username': username, 'password': hashed_password, 'email': email})
        return jsonify({'message': 'User created successfully'}), 201

    except Exception as e:
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

        user = next((user for user in users if user['username'] == username), None)

        if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
            return jsonify({'message': 'Login successful'}), 200
        else:
            return jsonify({'error': 'Invalid username or password'}), 401

    except Exception as e:
        return jsonify({'error': 'An error occurred during login'}), 500

# Main function to run the app
if __name__ == '__main__':
    app.run(debug=True)
