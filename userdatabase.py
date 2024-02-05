import sqlite3
from flask import Flask, request, jsonify, current_app
from flask_cors import CORS
import jwt
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)
app.config["SECRET_KEY"] = "yfs78gudgh8gndsfugd87gundsfygdsfugnsd78fgsndfygbs8dufng8"

def initialize_database():
    # Connect to SQLite database and create 'users' table if not exists
    connection = sqlite3.connect('users.db')
    cursor = connection.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            uid TEXT NOT NULL,
            password TEXT NOT NULL,
            birth_year INTEGER NOT NULL
        )
    ''')
    connection.commit()
    connection.close()

initialize_database()

def authenticate_user(uid, password, birth_year):
    # Authenticate user and generate JWT token if authentication is successful
    connection = sqlite3.connect('users.db')
    cursor = connection.cursor()

    cursor.execute('''
        SELECT * FROM users
        WHERE uid=? AND password=? AND birth_year=?
    ''', (uid, password, birth_year))

    user = cursor.fetchone()
    connection.close()

    if user is not None:
        # Create a payload for the JWT token
        payload = {
            "_uid": user[1],
            "exp": datetime.utcnow() + timedelta(hours=1)  # Token expiration time
        }
        # Generate JWT token using the payload and secret key
        token = jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")
        return True, True, token
    else:
        return False, False, None

def check_user_exists(uid, password, birth_year):
    # Check if user exists in the database
    connection = sqlite3.connect('users.db')
    cursor = connection.cursor()

    cursor.execute('''
        SELECT * FROM users
        WHERE uid=? AND password=? AND birth_year=?
    ''', (uid, password, birth_year))

    user = cursor.fetchone()
    connection.close()

    return user is not None

# Authentication route
@app.route('/api/users/authenticate', methods=['POST'])
def authenticate_user_route():
    data = request.get_json()

    uid = data.get('uid')
    password = data.get('password')
    birth_year = data.get('birthYear')

    is_authenticated, is_admin, token = authenticate_user(uid, password, birth_year)

    if is_authenticated:
        if is_admin:
            response = {'message': 'Authentication successful', 'redirect': 'crud.html', 'token': token}
        else:
            response = {'message': 'Authentication successful', 'redirect': None, 'token': token}
        resp_obj = jsonify(response)
        resp_obj.set_cookie("jwt", token,
                    max_age=3600,
                    secure=True,
                    httponly=True,
                    path='/',
                    samesite='None'  # This is the key part for cross-site requests

                    # domain="frontend.com"
                    )

        return resp_obj, 200
    else:
        response = {'message': 'Invalid credentials'}
        return jsonify(response), 401

# Signup route
@app.route('/api/users/signup', methods=['POST'])
def signup_user_route():
    data = request.get_json()

    uid = data.get('uid')
    password = data.get('password')
    birth_year = data.get('birthYear')

    if uid == '' or password == '' or birth_year == '':
        response = {'message': 'Invalid credentials. Please fill in all fields.'}
        return jsonify(response), 400

    if check_user_exists(uid, password, birth_year):
        response = {'message': 'User already exists.'}
        return jsonify(response), 409

    connection = sqlite3.connect('users.db')
    cursor = connection.cursor()

    cursor.execute('''
        INSERT INTO users (uid, password, birth_year)
        VALUES (?, ?, ?)
    ''', (uid, password, birth_year))

    connection.commit()
    connection.close()

    response = {'message': 'User registered successfully.'}
    return jsonify(response), 201

# Create user route
@app.route('/api/users', methods=['POST'])
def create_user():
    data = request.get_json()

    uid = data.get('uid')
    password = data.get('password')
    birth_year = data.get('birthYear')

    if uid == '' or password == '' or birth_year == '':
        response = {'message': 'Invalid credentials. Please fill in all fields.'}
        return jsonify(response), 400

    if check_user_exists(uid, password, birth_year):
        response = {'message': 'User already exists.'}
        return jsonify(response), 409

    connection = sqlite3.connect('users.db')
    cursor = connection.cursor()

    cursor.execute('''
        INSERT INTO users (uid, password, birth_year)
        VALUES (?, ?, ?)
    ''', (uid, password, birth_year))

    connection.commit()
    connection.close()

    response = {'message': 'User added to database'}
    return jsonify(response), 201

# Get all users route
@app.route('/api/users', methods=['GET'])
def get_all_users():
    connection = sqlite3.connect('users.db')
    cursor = connection.cursor()

    cursor.execute('SELECT * FROM users')
    users = cursor.fetchall()

    connection.close()

    user_list = [{'id': user[0], 'uid': user[1], 'password': user[2], 'birth_year': user[3]} for user in users]
    return jsonify({'users': user_list})

# Update user route
@app.route('/api/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.get_json()

    uid = data.get('uid')
    password = data.get('password')
    birth_year = data.get('birthYear')

    if uid == '' or password == '' or birth_year == '':
        response = {'message': 'Invalid credentials. Please fill in all fields.'}
        return jsonify(response), 400

    connection = sqlite3.connect('users.db')
    cursor = connection.cursor()

    cursor.execute('''
        UPDATE users
        SET uid=?, password=?, birth_year=?
        WHERE id=?
    ''', (uid, password, birth_year, user_id))

    connection.commit()
    connection.close()

    response = {'message': 'User updated'}
    return jsonify(response), 200

# Delete user route
@app.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    connection = sqlite3.connect('users.db')
    cursor = connection.cursor()

    cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))

    connection.commit()
    connection.close()

    response = {'message': 'User deleted'}
    return jsonify(response), 200

if __name__ == '__main__':
    app.run(debug=True)
