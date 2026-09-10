from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship

from app.database import Base


class Farmer(Base):
    __tablename__ = "farmers"

    id = Column(Integer, primary_key=True, index=True)
    farmer_code = Column(String(20), unique=True, index=True)
    name = Column(String(100))
    phone = Column(String(20))
    province = Column(String(50))
    district = Column(String(50))
    commune = Column(String(50))
    village = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)

    farms = relationship("Farm", back_populates="farmer")
    loans = relationship("Loan", back_populates="farmer")
