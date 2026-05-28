import jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext

SECRET_KEY = "your-secret-key-keep-it-safe"
ALGORITHM = "HS256"
TOKEN_EXPIRE_HOURS = 24

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Password hash karo
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


# Password verify karo
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# JWT Token banao
def create_token(user_id: int, email: str, role: str) -> str:
    payload = {
        "user_id" : user_id,
        "email"   : email,
        "role"    : role,
        "exp"     : datetime.utcnow() + timedelta(hours=TOKEN_EXPIRE_HOURS)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)