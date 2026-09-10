from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, DateTime, Date, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class Loan(Base):
    __tablename__ = "loans"

    id = Column(Integer, primary_key=True, index=True)
    loan_code = Column(String(30), unique=True, index=True)
    farmer_id = Column(Integer, ForeignKey("farmers.id"))
    outstanding_principal = Column(Float)
    monthly_installment = Column(Float)
    disbursement_date = Column(Date)
    maturity_date = Column(Date)
    interest_rate = Column(Float)
    dpd = Column(Integer, default=0)
    dpd_max_90d = Column(Integer, default=0)
    missed_payments_count = Column(Integer, default=0)
    restructured = Column(Boolean, default=False)
    status = Column(String(20), default="active")
    created_at = Column(DateTime, default=datetime.utcnow)

    farmer = relationship("Farmer", back_populates="loans")
