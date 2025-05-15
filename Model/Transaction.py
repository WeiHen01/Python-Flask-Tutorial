# Module Implementation
# 1. CRUD on transaction 
from dataclasses import dataclass
from datetime import date
@dataclass
class Transaction:
    Trans_ID: int
    User_ID: int
    Bank_ID: int
    Amount: float
    Usage: str
    Date: date