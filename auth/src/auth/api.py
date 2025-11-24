"""Authentication API router.

Endpoints:
- POST /auth/register        (create user)
- POST /auth/login           (returns JWT + optional API key list)
- GET  /auth/me              (current user profile)
- POST /auth/apikeys         (create new API key)
- GET  /auth/apikeys         (list API keys)
- DELETE /auth/apikeys/{id}  (revoke API key)
- POST /auth/password-reset/request  (send reset link)
- POST /auth/password-reset/confirm  (reset password)

Registration and password reset are API-only (no GUI forms).
"""
from __future__ import annotations
from fastapi import Header

import os
import datetime as dt
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from sqlalchemy.orm import Session

from .database import SessionLocal, init_db
from .models import User, APIKey, PasswordResetToken
from .security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
    hash_api_key,
    create_reset_expiry,
)

# Initialize DB at import time (simple approach; consider migrations for prod)
init_db()

router = APIRouter(prefix="/auth", tags=["Auth"])


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    address: str
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8)


class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    address: str
    username: str

    model_config = ConfigDict(from_attributes=True)


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut
    api_keys: List[str] = []  # masked hashes or IDs? Keep simple list of IDs.


class APIKeyOut(BaseModel):
    id: int
    created_at: dt.datetime
    revoked: bool

    model_config = ConfigDict(from_attributes=True)


class APIKeyCreateResponse(BaseModel):
    id: int
    raw_key: str  # show once


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(min_length=8)


class Message(BaseModel):
    message: str


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(db: Session = Depends(get_db), authorization: str | None = Header(default=None)) -> User:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    token = authorization.split()[1]
    username = decode_access_token(token)
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


def send_reset_email(email: str, token: str):
    base_url = os.getenv("FRONTEND_BASE_URL", "http://localhost:8000")
    reset_link = f"{base_url}/reset-password?token={token}"
    print(f"[auth] Password reset link for {email}: {reset_link}")


@router.post("/register", response_model=UserOut)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter((User.username == user_in.username) | (User.email == user_in.email)).first():
        raise HTTPException(
            status_code=400, detail="Username or email already exists")
    user = User(
        name=user_in.name,
        email=user_in.email,
        address=user_in.address,
        username=user_in.username,
        password_hash=hash_password(user_in.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=LoginResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == req.username).first()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    token = create_access_token(sub=user.username)
    key_ids = [k.id for k in user.api_keys if not k.revoked]
    return LoginResponse(access_token=token, user=user, api_keys=[str(i) for i in key_ids])


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return user


@router.post("/apikeys", response_model=APIKeyCreateResponse)
def create_apikey(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    raw_key = APIKey.generate_raw_key()
    hashed = hash_api_key(raw_key)
    api_key = APIKey(key_hash=hashed, user_id=user.id)
    db.add(api_key)
    db.commit()
    db.refresh(api_key)
    return APIKeyCreateResponse(id=api_key.id, raw_key=raw_key)


@router.get("/apikeys", response_model=list[APIKeyOut])
def list_apikeys(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    keys = db.query(APIKey).filter(APIKey.user_id == user.id).all()
    return keys


@router.delete("/apikeys/{key_id}", response_model=Message)
def revoke_apikey(key_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    key = db.query(APIKey).filter(APIKey.id == key_id,
                                  APIKey.user_id == user.id).first()
    if not key:
        raise HTTPException(status_code=404, detail="API key not found")
    key.revoked = True
    db.commit()
    return Message(message="API key revoked")


@router.post("/password-reset/request", response_model=Message)
def request_reset(req: PasswordResetRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email).first()
    if not user:
        return Message(message="If the email exists a reset link was sent")
    token_value = PasswordResetToken.generate_token()
    reset_token = PasswordResetToken(
        token=token_value,
        user_id=user.id,
        expires_at=create_reset_expiry(),
    )
    db.add(reset_token)
    db.commit()
    send_reset_email(user.email, token_value)
    return Message(message="If the email exists a reset link was sent")


@router.post("/password-reset/confirm", response_model=Message)
def confirm_reset(req: PasswordResetConfirm, db: Session = Depends(get_db)):
    token = db.query(PasswordResetToken).filter(
        PasswordResetToken.token == req.token).first()
    now_utc = dt.datetime.now(dt.UTC)
    if not token:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    expires_at = token.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=dt.UTC)
    if token.used or expires_at < now_utc:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    user = db.query(User).filter(User.id == token.user_id).first()
    if not user:
        raise HTTPException(status_code=400, detail="User not found")
    user.password_hash = hash_password(req.new_password)
    token.used = True
    db.commit()
    return Message(message="Password reset successful")


__all__ = ["router"]
