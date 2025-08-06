from datetime import datetime, timedelta
from jose import jwt
import os


# WARNING: In production, keep this secret hidden in .env
SECRET_KEY = os.getenv("JWT_SECRET","HELLO_SECRET") 
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 30

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
