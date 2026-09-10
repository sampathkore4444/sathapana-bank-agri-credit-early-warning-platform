"""User model for authentication and role-based access."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(100), unique=True)
    full_name = Column(String(100))
    hashed_password = Column(String(256))
    role = Column(String(20), default="rm")  # admin, credit_risk, rm, viewer
    province = Column(String(50), nullable=True)  # RM's assigned province
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
