from typing import Optional
from datetime import datetime, date
from pydantic import BaseModel, ConfigDict


class FeatureContribution(BaseModel):
    feature: str
    value: float
    contribution: float


class RiskScoreResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

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


class RiskScoreDetailResponse(BaseModel):
    id: int
    farmer_id: int
    farm_id: int
    loan_id: int
    scoring_date: Optional[date] = None
    risk_probability: float
    risk_bucket: str
    confidence: float
    primary_drivers: list[FeatureContribution]
    recommended_action: str
