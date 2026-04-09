from datetime import datetime, timedelta, timezone

from fastapi import HTTPException
from jose import jwt, JWTError, ExpiredSignatureError
from passlib.context import CryptContext

SECRET_KEY = "3b4c099b112945d9ed7ee2fba7e8cc9cf6b7f1975d8b133839e9f89f286a2456"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str):
    return bcrypt_context.hash(password)


def verify_password(plain_password: str, hashed_password: str):
    return bcrypt_context.verify(plain_password, hashed_password)


def create_access_token(username: str, user_id: int, role: str):
    to_encode = {
        "sub": username,
        "id": user_id,
        "role": role
    }

    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": int(expire.timestamp())})

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Token expired"
        )

    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Could not validate user"
        )
