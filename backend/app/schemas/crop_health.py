from datetime import datetime, date
from pydantic import BaseModel


class CropHealthResponse(BaseModel):
    id: int
    farm_id: int
    observation_date: date
    ndvi_current: float
    ndvi_historical: float
    ndvi_deviation_pct: float
    ndvi_trend: str
    ndwi_current: float
    growth_stage: str
    flood_exposure: bool
    drought_stress: bool
    rainfall_30d: float
    rainfall_deviation_30d: float
    temperature_stress_days: int
    sar_vh_backscatter: float
    crop_health_score: int
    status: str
    confidence: float
    created_at: datetime

    class Config:
        from_attributes = True
