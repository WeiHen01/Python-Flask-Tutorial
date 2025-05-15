# Module Implementation
# 1. CRUD on banks

from flask import Blueprint, jsonify, request
from Database.db import get_db_connection
import hashlib
import datetime
import base64
from urllib.parse import unquote
from Model.Bank import Bank

bank_bp = Blueprint('bank', __name__, url_prefix="/api/bank")

@bank_bp.route("/", methods=['GET'])
def list_all_banks():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM dbo.Bank")
        banks = [
            Bank(
                Bank_ID=row[0],
                Name=row[1],
                Type=row[2],
            ) for row in cursor.fetchall()
        ]
        cursor.close()
        conn.close()
        return jsonify([bank.__dict__ for bank in banks]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
# GET single bank by ID
@bank_bp.route("/<int:bank_id>", methods=['GET'])
def get_bank(bank_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM dbo.Bank WHERE Bank_ID = ?", (bank_id,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()

        if row:
            bank = Bank(Bank_ID=row[0], Name=row[1], Type=row[2])
            return jsonify(bank.__dict__), 200
        else:
            return jsonify({'error': 'Bank not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
# GET single bank by ID
@bank_bp.route("/user/<int:user_id>", methods=['GET'])
def get_userbank(user_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # JOIN User_Bank with Bank for detailed list
        query = """
            SELECT ub.User_ID, ub.Bank_ID, ub.AccNum,
                   b.Name, b.Type
            FROM dbo.User_Bank ub
            JOIN dbo.Bank b ON ub.Bank_ID = b.Bank_ID
            WHERE ub.User_ID = ?
        """
        cursor.execute(query, (user_id,))
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        if rows:
            results = []
            for i, row in enumerate(rows, start=1):
                results.append({
                    "#": i,
                    'User_ID': row[0],
                    'Bank_ID': row[1],
                    'AccNum': row[2],
                    'Bank': {
                        'Name': row[3],
                        'Type': row[4]
                    }
                })

            
            return jsonify({'Result': results}), 200
        else:
            return jsonify({'Result': []}), 200  # Return empty list if no data
    except Exception as e:
        return jsonify({'error': str(e)}), 500



# POST create new bank
@bank_bp.route("/", methods=['POST'])
def create_bank():
    data = request.get_json()
    name = data.get('Name')
    bank_type = data.get('Type')

    if not name or not bank_type:
        return jsonify({'error': 'Name and Type are required'}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO dbo.Bank (Name, Type) VALUES (?, ?)", (name, bank_type))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'message': 'Bank created successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# PUT update bank
@bank_bp.route("/<int:bank_id>", methods=['PUT'])
def update_bank(bank_id):
    data = request.get_json()
    name = data.get('Name')
    bank_type = data.get('Type')

    if not name or not bank_type:
        return jsonify({'error': 'Name and Type are required'}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE dbo.Bank SET Name = ?, Type = ? WHERE Bank_ID = ?", (name, bank_type, bank_id))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'message': 'Bank updated successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@bank_bp.route("/update/<int:bank_id>", methods=['PUT'])
def update_userbank(bank_id):
    data = request.get_json()
    accnum = data.get('AccNum')
    userID = data.get('UserID')

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE dbo.User_Bank SET AccNum = ? WHERE Bank_ID = ? AND User_ID = ?", (accnum, bank_id, userID))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'message': 'Bank updated successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

# DELETE bank
@bank_bp.route("/delete/<int:bank_id>/<int:user_id>", methods=['DELETE'])
def delete_bank(bank_id, user_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM dbo.User_Bank WHERE Bank_ID = ? AND user_id = ?", (bank_id, user_id))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'message': 'Bank deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500