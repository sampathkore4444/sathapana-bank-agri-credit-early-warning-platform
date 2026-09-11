import json
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models import RiskScore, Farmer, Farm, Loan
from app.schemas.risk_score import RiskScoreDetailResponse


def _parse_drivers(raw: Optional[str]) -> list[dict]:
    try:
        return json.loads(raw) if raw else []
    except (TypeError, ValueError):
        return []


def list_risk_scores(
    db: Session,
    bucket: Optional[str] = None,
    province: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
) -> list[RiskScore]:
    q = db.query(RiskScore).join(Farm).join(Farmer)
    if bucket:
        q = q.filter(RiskScore.risk_bucket == bucket.upper())
    if province:
        q = q.filter(Farmer.province == province)
    return q.order_by(RiskScore.risk_probability.desc()).offset(skip).limit(limit).all()


def get_farmer_risk(db: Session, farmer_id: int) -> Optional[RiskScoreDetailResponse]:
    rs = (
        db.query(RiskScore)
        .filter(RiskScore.farmer_id == farmer_id)
        .order_by(RiskScore.scoring_date.desc())
        .first()
    )
    if not rs:
        return None
    return RiskScoreDetailResponse(
        id=rs.id,
        farmer_id=rs.farmer_id,
        farm_id=rs.farm_id,
        loan_id=rs.loan_id,
        scoring_date=rs.scoring_date,
        risk_probability=rs.risk_probability,
        risk_bucket=rs.risk_bucket,
        confidence=rs.confidence,
        primary_drivers=_parse_drivers(rs.primary_drivers_json),
        recommended_action=rs.recommended_action,
    )


def get_bucket_counts(db: Session) -> dict:
    """Get risk bucket counts grouped by bucket."""
    rows = (
        db.query(RiskScore.risk_bucket, func.count(RiskScore.id))
        .group_by(RiskScore.risk_bucket)
        .all()
    )
    return {b: c for b, c in rows}
