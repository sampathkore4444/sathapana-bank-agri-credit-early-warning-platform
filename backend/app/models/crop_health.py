from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, DateTime, Date, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class CropHealth(Base):
    __tablename__ = "crop_health"

    id = Column(Integer, primary_key=True, index=True)
    farm_id = Column(Integer, ForeignKey("farms.id"))
    observation_date = Column(Date)
    ndvi_current = Column(Float)
    ndvi_historical = Column(Float)
    ndvi_deviation_pct = Column(Float)
    ndvi_trend = Column(String(20))  # improving, stable, declining
    ndwi_current = Column(Float)
    growth_stage = Column(String(30))
    flood_exposure = Column(Boolean, default=False)
    drought_stress = Column(Boolean, default=False)
    rainfall_30d = Column(Float)
    rainfall_deviation_30d = Column(Float)
    temperature_stress_days = Column(Integer, default=0)
    sar_vh_backscatter = Column(Float)
    crop_health_score = Column(Integer)
    status = Column(String(20))  # green, yellow, orange, red
    confidence = Column(Float, default=0.85)
    created_at = Column(DateTime, default=datetime.utcnow)

    farm = relationship("Farm", back_populates="crop_health_records")
