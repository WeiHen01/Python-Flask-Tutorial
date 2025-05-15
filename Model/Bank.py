# Module Implementation
# 1. CRUD on banks
from dataclasses import dataclass
from datetime import date

@dataclass
class Bank:
    Bank_ID: int
    Name: str
    Type: date