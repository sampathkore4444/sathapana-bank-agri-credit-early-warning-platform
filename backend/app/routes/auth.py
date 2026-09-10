"""Auth API routes — login, register, user management."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, UserLogin, Token
from app.services.auth_service import (
    login, create_user, get_current_user, require_role,
)

router = APIRouter()


@router.post("/auth/login")
def login_endpoint(data: UserLogin, db: Session = Depends(get_db)):
    """Authenticate and return JWT token."""
    return login(db, data.username, data.password)


@router.get("/auth/me", response_model=UserResponse)
def get_me(user: User = Depends(get_current_user)):
    """Get current authenticated user."""
    return user


@router.post("/auth/register", response_model=UserResponse, status_code=201)
def register(data: UserCreate, db: Session = Depends(get_db), _admin: User = Depends(require_role("admin"))):
    """Register a new user (admin only)."""
    return create_user(db, data.model_dump())


@router.get("/auth/users", response_model=List[UserResponse])
def list_users(db: Session = Depends(get_db), _admin: User = Depends(require_role("admin"))):
    """List all users (admin only)."""
    return db.query(User).all()


@router.patch("/auth/users/{user_id}/deactivate")
def deactivate_user(user_id: int, db: Session = Depends(get_db), _admin: User = Depends(require_role("admin"))):
    """Deactivate a user (admin only)."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")
    user.is_active = False
    db.commit()
    return {"status": "deactivated"}
