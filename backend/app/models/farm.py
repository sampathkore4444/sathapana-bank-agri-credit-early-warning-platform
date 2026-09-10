from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, Text, DateTime, Date, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class Farm(Base):
    __tablename__ = "farms"

    id = Column(Integer, primary_key=True, index=True)
    farm_code = Column(String(20), unique=True, index=True)
    farmer_id = Column(Integer, ForeignKey("farmers.id"))
    centroid_lat = Column(Float)
    centroid_lon = Column(Float)
    boundary_geojson = Column(Text)  # stored as GeoJSON string
    area_hectares = Column(Float)
    area_satellite = Column(Float)
    crop_type = Column(String(30), default="rice")
    planting_date = Column(Date, nullable=True)
    expected_harvest = Column(Date, nullable=True)
    season = Column(String(20), default="wet")
    boundary_source = Column(String(20), default="gps")
    boundary_confidence = Column(Float, default=0.95)
    crop_classification_confidence = Column(Float, default=0.90)
    created_at = Column(DateTime, default=datetime.utcnow)

    farmer = relationship("Farmer", back_populates="farms")
    crop_health_records = relationship("CropHealth", back_populates="farm")
    risk_scores = relationship("RiskScore", back_populates="farm")
    alerts = relationship("Alert", back_populates="farm")
