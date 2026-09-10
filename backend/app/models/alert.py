from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    alert_code = Column(String(30), unique=True, index=True)
    farm_id = Column(Integer, ForeignKey("farms.id"))
    risk_score_id = Column(Integer, ForeignKey("risk_scores.id"), nullable=True)
    alert_type = Column(String(30))  # risk_escalation, crop_stress, flood, drought
    severity = Column(String(10))  # LOW, MEDIUM, HIGH, CRITICAL
    title = Column(String(200))
    description = Column(Text)
    risk_score_value = Column(Float)
    status = Column(String(20), default="open")  # open, acknowledged, investigated, dismissed, resolved
    assigned_to = Column(String(50))
    action_taken = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    acknowledged_at = Column(DateTime, nullable=True)
    resolved_at = Column(DateTime, nullable=True)

    farm = relationship("Farm", back_populates="alerts")
