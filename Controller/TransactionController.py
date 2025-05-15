# Module Implementation
# 1. CRUD on transaction 

from flask import Blueprint, jsonify, request
from Database.db import get_db_connection
import hashlib
import datetime
import base64
from urllib.parse import unquote
from Model.Transaction import Transaction


trans_bp = Blueprint('trans', __name__, url_prefix="/api/trans")

@trans_bp.route("/", methods=['GET'])
def list_all_banks():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM dbo.Transactions")
        transactions = [
            Transaction(
                Trans_ID = row[0], 
                User_ID = row[1],
                Bank_ID = row[2],
                Amount = row[3],
                Usage = row[4],
                Date = row[5]
            ) for row in cursor.fetchall()
        ]
        cursor.close()
        conn.close()
        return jsonify([transaction.__dict__ for transaction in transactions]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    
# fetch user's transaction with bank and account number
@trans_bp.route('/user/<int:user_id>', methods=['GET'])
def get_user_trans(user_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
            SELECT 
                t.Trans_ID,
                b.Bank_ID,
                b.Name AS Bank,
                ub.AccNum AS AccountNumber,
                t.Amount,
                t.Date AS TransferAt,
                t.Usage
            FROM dbo.Transactions t
            INNER JOIN dbo.Bank b ON t.Bank_ID = b.Bank_ID
            INNER JOIN dbo.User_Bank ub ON t.Bank_ID = ub.Bank_ID AND t.User_ID = ub.User_ID
            WHERE t.User_ID = ?
            ORDER BY t.Date DESC
        """
        
        cursor.execute(query, (user_id,))
        transactions = []
        for i, row in enumerate(cursor.fetchall(), start=1):
            transactions.append({
                "#": i,
                "Bank_ID": row.Bank_ID,
                "Trans_ID": row.Trans_ID,
                "Bank": row.Bank,
                "AccountNumber": row.AccountNumber,
                "Amount": float(row.Amount),
                "TransferAt": row.TransferAt.strftime("%Y-%m-%d %H:%M:%S") if row.TransferAt else None,
                "Usage": row.Usage,
                "Action": ""  # You can fill this based on frontend requirements
            })

        cursor.close()
        conn.close()
        return jsonify(transactions), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    


        
# making new transaction
@trans_bp.route('/new', methods=['POST'])
def new_trans():
    try: 
        conn = get_db_connection()
        cursor = conn.cursor()
        data = request.get_json()

        user = data.get("User_ID")
        bank = data.get("Bank_ID")
        amount = data.get("Amount")
        usage = data.get("Usage")
        date = data.get("Date")

        cursor.execute("INSERT INTO dbo.Transactions (User_ID, Bank_ID, Amount, Usage, Date) VALUES (?, ?, ?, ?, ?)", (user, bank, amount, usage, date))

        conn.commit()
        cursor.close()
        return jsonify({'message': 'Transaction inserted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

# 🔵 Update a transaction
@trans_bp.route('/update/<int:trans_id>', methods=['PUT'])
def update_transaction(trans_id):
    try:
        data = request.get_json()
        conn = get_db_connection()
        cursor = conn.cursor()

        bank = data.get('Bank_ID')
        amount = data.get('Amount')
        usage = data.get('Usage')
        date = data.get('Date')

        cursor.execute("""
            UPDATE dbo.Transactions 
            SET Bank_ID = ?, Amount = ?, Usage = ?, Date = ?
            WHERE Trans_ID = ?
        """, (
            bank, amount, 
            usage, date, trans_id
        ))

        conn.commit()
        cursor.close()
        return jsonify({'message': 'Transaction updated successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# 🔴 Delete a transaction
@trans_bp.route('/<int:trans_id>', methods=['DELETE'])
def delete_transaction(trans_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM dbo.Transactions WHERE Trans_ID = ?", (trans_id,))
        conn.commit()
        cursor.close()
        return jsonify({'message': 'Transaction deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

# 🔍 Filter by month and year
@trans_bp.route('/filter/month-year', methods=['GET'])
def filter_by_month_year():
    try:
        month = request.args.get('month')  # MM
        year = request.args.get('year')    # YYYY
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM dbo.Transactions 
            WHERE MONTH(Date) = ? AND YEAR(Date) = ?
        """, (month, year))

        transactions = [Transaction(*row).__dict__ for row in cursor.fetchall()]
        cursor.close()
        return jsonify(transactions), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 🔍 Filter by date range
@trans_bp.route('/filter/date-range', methods=['GET'])
def filter_by_date_range():
    try:
        start_date = request.args.get('start')  # format: YYYY-MM-DD
        end_date = request.args.get('end')      # format: YYYY-MM-DD

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM dbo.Transactions 
            WHERE Date BETWEEN ? AND ?
        """, (start_date, end_date))

        transactions = [Transaction(*row).__dict__ for row in cursor.fetchall()]
        cursor.close()
        return jsonify(transactions), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

# 📊 Total amount by year
@trans_bp.route('/stats/year', methods=['GET'])
def stats_by_year():
    try:
        year = request.args.get('year')
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT MONTH(Date) AS Month, SUM(Amount) AS Total 
            FROM dbo.Transactions
            WHERE YEAR(Date) = ?
            GROUP BY MONTH(Date)
            ORDER BY Month
        """, (year,))

        data = [{'month': row[0], 'total': float(row[1])} for row in cursor.fetchall()]
        cursor.close()
        return jsonify(data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 📊 Total amount by specific month of all years
@trans_bp.route('/stats/month', methods=['GET'])
def stats_by_month():
    try:
        month = request.args.get('month')
        year = request.args.get('year')
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT SUM(Amount) 
            FROM dbo.Transactions
            WHERE MONTH(Date) = ? AND YEAR(Date) = ?
        """, (month, year))

        result = cursor.fetchone()
        total = float(result[0]) if result[0] is not None else 0.0

        cursor.close()
        conn.close()
        return jsonify({
            'year': int(year),
            'month': int(month),
            'total': total
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 📊 Total amount by range
@trans_bp.route('/stats/range', methods=['GET'])
def stats_by_range():
    try:
        start = request.args.get('start')
        end = request.args.get('end')
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT CONVERT(date, Date) AS DateOnly, SUM(Amount) AS Total
            FROM dbo.Transactions
            WHERE Date BETWEEN ? AND ?
            GROUP BY CONVERT(date, Date)
            ORDER BY DateOnly
        """, (start, end))

        data = [{'date': row[0].strftime('%Y-%m-%d'), 'total': float(row[1])} for row in cursor.fetchall()]
        cursor.close()
        return jsonify(data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
