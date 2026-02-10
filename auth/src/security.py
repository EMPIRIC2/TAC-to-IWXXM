"""Security utilities: password hashing, JWT, API key hashing, reset tokens."""
from __future__ import annotations

import os
import hashlib
import datetime as dt
from typing import Optional
from jose import jwt, JWTError
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

JWT_SECRET = os.getenv("AUTH_JWT_SECRET", "dev-insecure-secret-change")
JWT_ALGO = "HS256"
JWT_EXPIRE_MINUTES = int(os.getenv("AUTH_JWT_EXPIRE_MINUTES", "60"))

API_KEY_HASH_ALGO = "sha256"

RESET_TOKEN_EXPIRE_MINUTES = int(os.getenv("AUTH_RESET_EXPIRE_MINUTES", "30"))


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)


def create_access_token(sub: str) -> str:
    expire = dt.datetime.now(dt.UTC) + dt.timedelta(minutes=JWT_EXPIRE_MINUTES)
    to_encode = {"sub": sub, "exp": expire}
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGO)


def decode_access_token(token: str) -> Optional[str]:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])
        return payload.get("sub")
    except JWTError:
        return None


def hash_api_key(raw_key: str) -> str:
    return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()


def create_reset_expiry() -> dt.datetime:
    return dt.datetime.now(dt.UTC) + dt.timedelta(minutes=RESET_TOKEN_EXPIRE_MINUTES)


__all__ = [
    "hash_password",
    "verify_password",
    "create_access_token",
    "decode_access_token",
    "hash_api_key",
    "create_reset_expiry",
]
