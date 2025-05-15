from flask import Blueprint, jsonify, request
from Database.db import get_db_connection
from Model.User import User
import hashlib
import datetime
import base64
from urllib.parse import unquote


users_bp = Blueprint('users', __name__, url_prefix='/api/users')

# Module Implementation
# 1. User Login
# 2. Login Attempts
# 3. Upload profile image - multipart/form-data (BLOB)
# 4. CRUD account
# 5. Add bank

# endpoint: http://localhost:5000/api/users
@users_bp.route('/', methods=['GET'])
def get_users():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM dbo.users")
        users = [
            User(
                User_ID=row[0],
                Username=row[1],
                Email=row[2],
                Password=row[3],
                ProfileImg=row[4],
                Status=row[5],
                MaxLimitMonth=float(row[6]),
                TargetSaving=float(row[7])
            ) for row in cursor.fetchall()
        ]
        cursor.close()
        conn.close()
        return jsonify([user.__dict__ for user in users]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
# dynamic query for retreive data
@users_bp.route('/get/<path:query>', methods=['GET'])
def run_raw_query(query):
    try:
        query_decoded = unquote(query)  # Decode URL-encoded query
        print("Decoded query:", query_decoded)

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query_decoded)
        row = cursor.fetchone()
        users = [
            User(
                User_ID=row[0],
                Username=row[1],
                Email=row[2],
                Password=row[3],
                ProfileImg=row[4],
                Status=row[5],
                MaxLimitMonth=float(row[6]),
                TargetSaving=float(row[7])
            )
        ]
        conn.close()

        if not row:
            return jsonify({'error': 'No data found'}), 404

        return jsonify({'Result': users}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
# dynamic query for retreive data
@users_bp.route('/get/user/<int:id>', methods=['GET'])
def get_user_profile(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM dbo.Users WHERE User_ID = ?", id)
        row = cursor.fetchone()
        users = [
            User(
                User_ID=row[0],
                Username=row[1],
                Email=row[2],
                Password=row[3],
                ProfileImg=row[4],
                Status=row[5],
                MaxLimitMonth=float(row[6]),
                TargetSaving=float(row[7])
            )
        ]
        conn.close()

        if not row:
            return jsonify({'error': 'No data found'}), 404

        return jsonify({'Result': users}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
# endpoint: http://localhost:5000/api/users/login
@users_bp.route('/login', methods=['POST'])
def user_login():
    try:
        data = request.get_json()
        username = data.get('Username')
        password = data.get('Password')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT User_ID, Password FROM dbo.Users WHERE Username = ? AND Password = ?", (username, password))
        user = cursor.fetchone()
        
        if user and user[1] == password:
            cursor.execute("UPDATE dbo.Login_attempts SET No_attempt = 0, Last_Login = ? WHERE User_ID = ?",
                         (datetime.datetime.now(), user[0]))
            conn.commit()
            cursor.close()
            conn.close()
            return jsonify({'message': 'Login successful', 'User_ID': user[0]}), 200
        else:
            if user:
                cursor.execute("UPDATE dbo.Login_attempts SET No_attempt = No_attempt + 1 WHERE User_ID = ?",
                             (user[0],))
                conn.commit()
            cursor.close()
            conn.close()
            return jsonify({'error': 'Invalid credentials'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@users_bp.route('/profile-image/<int:user_id>', methods=['POST'])
def upload_profile_image(user_id):
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400
        
        image = request.files['image']
        image_data = base64.b64encode(image.read()).decode('utf-8')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE dbo.Users SET ProfileImg = ? WHERE User_ID = ?",
                      (image_data, user_id))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'message': 'Profile image uploaded successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@users_bp.route("/bank", methods=['POST'])
def create_userbank():
    try:
        data = request.get_json()
        conn = get_db_connection()
        cursor = conn.cursor()

        bank_id = data.get('BankID')
        user_id = data.get('UserID')
        acc_num = data.get('AccNum')

        cursor.execute("INSERT INTO dbo.User_Bank (Bank_ID, User_ID, AccNum) VALUES (?, ?, ?)", (bank_id, user_id, acc_num))
        
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'message': 'User created successfully', 'User_ID': user_id}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@users_bp.route('/', methods=['POST'])
def create_user():
    try:
        data = request.get_json()
        conn = get_db_connection()
        cursor = conn.cursor()
        
        hashed_password = hashlib.sha256(data['Password'].encode()).hexdigest()
        cursor.execute("""
            INSERT INTO dbo.Users (Username, Email, Password, ProfileImg, Status, MaxLimitMonth, TargetSaving)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (data['Username'], data['Email'], hashed_password, data.get('ProfileImg', ''),
              data.get('Status', 'Active'), data['MaxLimitMonth'], data['TargetSaving']))
        
        user_id = cursor.execute("SELECT @@IDENTITY").fetchone()[0]
        cursor.execute("INSERT INTO dbo.Login_attempts (User_ID, No_attempt, Last_Login) VALUES (?, ?, ?)",
                      (user_id, 0, None))
        
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'message': 'User created successfully', 'User_ID': user_id}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@users_bp.route('/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    try:
        data = request.get_json()
        conn = get_db_connection()
        cursor = conn.cursor()
        
        update_fields = []
        params = []
        for field in ['Username', 'Email', 'Status', 'MaxLimitMonth', 'TargetSaving']:
            if field in data:
                update_fields.append(f"{field} = ?")
                params.append(data[field])
        
        if 'Password' in data:
            update_fields.append("Password = ?")
            params.append(hashlib.sha256(data['Password'].encode()).hexdigest())
            
        if update_fields:
            params.append(user_id)
            query = f"UPDATE dbo.Users SET {', '.join(update_fields)} WHERE User_ID = ?"
            cursor.execute(query, params)
            conn.commit()
        
        cursor.close()
        conn.close()
        return jsonify({'message': 'User updated successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@users_bp.route('/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM dbo.Users WHERE User_ID = ?", (user_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'message': 'User deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500