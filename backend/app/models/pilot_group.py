from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from app.database import Base


class PilotGroup(Base):
    """Tracks pilot vs control group assignment for the experiment."""
    __tablename__ = "pilot_groups"

    id = Column(Integer, primary_key=True, index=True)
    farmer_id = Column(Integer, ForeignKey("farmers.id"), unique=True)
    group_type = Column(String(10))  # "pilot" or "control"
    assigned_date = Column(DateTime, default=datetime.utcnow)
    province = Column(String(50))
    loan_size_bucket = Column(String(20))  # small, medium, large
    crop_type = Column(String(30), default="rice")
    stratification_weight = Column(Float, default=1.0)

    farmer = relationship("Farmer")


class PilotOutcome(Base):
    """Outcome metrics for pilot experiment measurement."""
    __tablename__ = "pilot_outcomes"

    id = Column(Integer, primary_key=True, index=True)
    farmer_id = Column(Integer, ForeignKey("farmers.id"))
    group_type = Column(String(10))  # pilot or control
    measurement_date = Column(DateTime, default=datetime.utcnow)

    # DPD metrics
    dpd_30_ever = Column(Boolean, default=False)
    dpd_60_ever = Column(Boolean, default=False)
    npl_migration = Column(Boolean, default=False)
    restructured = Column(Boolean, default=False)

    # Intervention metrics
    days_to_rm_intervention = Column(Integer, nullable=True)
    rm_intervened = Column(Boolean, default=False)

    # Financial outcome
    recovered = Column(Boolean, default=False)
    loss_amount = Column(Float, default=0.0)
