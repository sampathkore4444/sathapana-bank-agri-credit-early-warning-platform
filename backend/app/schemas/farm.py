from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel


class FarmBase(BaseModel):
    farm_code: str
    farmer_id: int
    centroid_lat: float
    centroid_lon: float
    boundary_geojson: Optional[str] = None
    area_hectares: float
    area_satellite: Optional[float] = None
    crop_type: str = "rice"
    planting_date: Optional[date] = None
    expected_harvest: Optional[date] = None
    season: str = "wet"


class FarmCreate(FarmBase):
    pass


class FarmResponse(FarmBase):
    id: int
    boundary_source: str
    boundary_confidence: float
    crop_classification_confidence: float
    created_at: datetime

    class Config:
        from_attributes = True
