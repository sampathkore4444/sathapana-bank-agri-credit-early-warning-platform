from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, Text, DateTime, Date, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class RiskScore(Base):
    __tablename__ = "risk_scores"

    id = Column(Integer, primary_key=True, index=True)
    farm_id = Column(Integer, ForeignKey("farms.id"))
    farmer_id = Column(Integer)
    loan_id = Column(Integer)
    scoring_date = Column(Date)
    risk_probability = Column(Float)  # 0.0 - 1.0
    risk_bucket = Column(String(10))  # GREEN, AMBER, ORANGE, RED
    confidence = Column(Float, default=0.80)
    primary_drivers_json = Column(Text, default="[]")
    recommended_action = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)

    farm = relationship("Farm", back_populates="risk_scores")
