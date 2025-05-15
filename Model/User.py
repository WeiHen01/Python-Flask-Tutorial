# Module Implementation
# 1. User Login
# 2. Login Attempts
# 3. Upload profile image - multipart/form-data (BLOB)
# 4. CRUD account
# 5. Add bank

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class User:
    User_ID: int
    Username: str
    Email: str
    Password: str
    ProfileImg: Optional[str]
    Status: str
    MaxLimitMonth: float
    TargetSaving: float