from flask import Flask
from flask_cors import CORS

#Blueprints import
from Controller.UserController import users_bp
from Controller.BankController import bank_bp
from Controller.TransactionController import trans_bp

app = Flask(__name__)
CORS(app)  # Enable CORS for cross-origin requests

# Register Blueprints
app.register_blueprint(users_bp)
app.register_blueprint(bank_bp)
app.register_blueprint(trans_bp)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)