from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
from app.config import settings
from typing import Optional
from fastapi import HTTPException, status


pwd_context = CryptContext(schemes=["pbkdf2_sha256", "bcrypt"], deprecated="auto")

def verify_and_update_password(plain_password, hashed_password_from_db):
    return pwd_context.verify(plain_password, hashed_password_from_db)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def decode_and_validate_token(encoded_jwt: str, secret_key: str, algorithms: list[str]) -> dict:
    try:
        decoded_jwt = jwt.decode(encoded_jwt, secret_key, algorithms=algorithms)
        return decoded_jwt

    except JWTError:
        raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials"
    )