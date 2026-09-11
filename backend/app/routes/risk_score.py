from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.risk_score import RiskScoreDetailResponse
from app.services import risk_score_service

router = APIRouter()


@router.get("/risk-scores")
def list_risk_scores(
    bucket: Optional[str] = None,
    province: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    return risk_score_service.list_risk_scores(db, bucket=bucket, province=province, skip=skip, limit=limit)


@router.get("/risk-scores/{farmer_id}", response_model=RiskScoreDetailResponse)
def get_farmer_risk(farmer_id: int, db: Session = Depends(get_db)):
    result = risk_score_service.get_farmer_risk(db, farmer_id)
    if not result:
        raise HTTPException(404, "No risk score for this farmer")
    return result
