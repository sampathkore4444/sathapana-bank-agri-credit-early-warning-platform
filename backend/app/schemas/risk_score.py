from datetime import datetime, date
from pydantic import BaseModel


class RiskScoreResponse(BaseModel):
    id: int
    farm_id: int
    farmer_id: int
    loan_id: int
    scoring_date: date
    risk_probability: float
    risk_bucket: str
    confidence: float
    primary_drivers_json: str
    recommended_action: str
    created_at: datetime

    class Config:
        from_attributes = True
