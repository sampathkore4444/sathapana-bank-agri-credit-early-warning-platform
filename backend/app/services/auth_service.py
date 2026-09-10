"""Authentication service — password hashing, JWT tokens, role-based access.

Uses bcrypt for passwords and PyJWT for tokens.
For PoC: simple secret key. For production: use RSA keys.
"""
import os
from datetime import datetime, timedelta
from typing import Optional

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User

SECRET_KEY = os.getenv("JWT_SECRET", "sarp-poc-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("TOKEN_EXPIRE_MINUTES", "480"))  # 8 hours

security = HTTPBearer(auto_error=False)


# --- Password Hashing ---

def hash_password(password: str) -> str:
    """Hash a password with bcrypt."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a password against its hash."""
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


# --- JWT Tokens ---

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    """Decode and validate a JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


# --- User Management ---

def create_user(db: Session, data: dict) -> User:
    """Create a new user."""
    existing = db.query(User).filter(
        (User.username == data["username"]) | (User.email == data["email"])
    ).first()
    if existing:
        raise HTTPException(400, "Username or email already exists")

    user = User(
        username=data["username"],
        email=data["email"],
        full_name=data["full_name"],
        hashed_password=hash_password(data["password"]),
        role=data.get("role", "rm"),
        province=data.get("province"),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """Authenticate a user by username and password."""
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        return None
    user.last_login = datetime.utcnow()
    db.commit()
    return user


def login(db: Session, username: str, password: str) -> dict:
    """Login and return JWT token."""
    user = authenticate_user(db, username, password)
    if not user:
        raise HTTPException(401, "Invalid username or password")

    token = create_access_token({
        "sub": str(user.id),
        "username": user.username,
        "role": user.role,
    })

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "province": user.province,
        },
    }


# --- FastAPI Dependencies ---

def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """FastAPI dependency: extract and validate current user from JWT."""
    if not credentials:
        raise HTTPException(status_code=401, detail="Not authenticated")

    payload = decode_token(credentials.credentials)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")
    return user


def require_role(*roles: str):
    """Dependency factory: require the current user to have one of the specified roles."""
    def role_checker(user: User = Depends(get_current_user)):
        if user.role not in roles:
            raise HTTPException(
                status_code=403,
                detail=f"Role '{user.role}' not authorized. Required: {', '.join(roles)}",
            )
        return user
    return role_checker


# --- Seed Default Users ---

def seed_default_users(db: Session):
    """Create default users for the PoC."""
    defaults = [
        {"username": "admin", "email": "admin@sathapana.com.kh", "full_name": "System Admin", "password": "admin123", "role": "admin"},
        {"username": "credit_risk", "email": "creditrisk@sathapana.com.kh", "full_name": "Credit Risk Manager", "password": "risk123", "role": "credit_risk"},
        {"username": "sovannara", "email": "sovannara@sathapana.com.kh", "full_name": "Sovannara (RM)", "password": "rm123", "role": "rm", "province": "Battambang"},
        {"username": "dara", "email": "dara@sathapana.com.kh", "full_name": "Dara (RM)", "password": "rm123", "role": "rm", "province": "Siem Reap"},
        {"username": "chantrea", "email": "chantrea@sathapana.com.kh", "full_name": "Chantrea (RM)", "password": "rm123", "role": "rm", "province": "Kampong Cham"},
        {"username": "viewer", "email": "viewer@sathapana.com.kh", "full_name": "Read-only Viewer", "password": "view123", "role": "viewer"},
    ]

    for u in defaults:
        existing = db.query(User).filter(User.username == u["username"]).first()
        if not existing:
            create_user(db, u)
