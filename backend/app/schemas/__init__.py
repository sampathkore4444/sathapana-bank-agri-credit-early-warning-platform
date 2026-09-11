"""Pydantic schemas for API request/response validation."""
from app.schemas.farmer import FarmerBase, FarmerCreate, FarmerResponse
from app.schemas.farm import FarmBase, FarmCreate, FarmResponse
from app.schemas.loan import LoanBase, LoanCreate, LoanResponse
from app.schemas.crop_health import CropHealthResponse
from app.schemas.risk_score import FeatureContribution, RiskScoreResponse, RiskScoreDetailResponse
from app.schemas.alert import AlertBase, AlertCreate, AlertResponse
from app.schemas.dashboard import ProvinceBreakdown, PortfolioSummary

__all__ = [
    "FarmerBase", "FarmerCreate", "FarmerResponse",
    "FarmBase", "FarmCreate", "FarmResponse",
    "LoanBase", "LoanCreate", "LoanResponse",
    "CropHealthResponse",
    "RiskScoreResponse", "RiskScoreDetailResponse", "FeatureContribution",
    "AlertBase", "AlertCreate", "AlertResponse",
    "ProvinceBreakdown", "PortfolioSummary",
]
