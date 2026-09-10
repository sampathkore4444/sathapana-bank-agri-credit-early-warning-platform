from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models import Farmer, Farm, Loan, RiskScore, Alert


def portfolio_summary(db: Session) -> dict:
    total_farmers = db.query(func.count(Farmer.id)).scalar()
    total_outstanding = db.query(func.sum(Loan.outstanding_principal)).scalar() or 0

    # Risk bucket counts
    bucket_counts = (
        db.query(RiskScore.risk_bucket, func.count(RiskScore.id))
        .group_by(RiskScore.risk_bucket)
        .all()
    )
    counts = {b: c for b, c in bucket_counts}

    # Province breakdown
    provinces = []
    prov_rows = db.query(Farmer.province).distinct().all()
    for (prov,) in prov_rows:
        farmer_ids = [f.id for f in db.query(Farmer.id).filter(Farmer.province == prov).all()]
        loan_outstanding = (
            db.query(func.sum(Loan.outstanding_principal))
            .filter(Loan.farmer_id.in_(farmer_ids))
            .scalar() or 0
        )
        prov_buckets = (
            db.query(RiskScore.risk_bucket, func.count(RiskScore.id))
            .filter(RiskScore.farmer_id.in_(farmer_ids))
            .group_by(RiskScore.risk_bucket)
            .all()
        )
        prov_counts = {b: c for b, c in prov_buckets}
        provinces.append({
            "province": prov,
            "green": prov_counts.get("GREEN", 0),
            "amber": prov_counts.get("AMBER", 0),
            "orange": prov_counts.get("ORANGE", 0),
            "red": prov_counts.get("RED", 0),
            "total_outstanding": round(loan_outstanding, 2),
        })

    return {
        "total_farmers": total_farmers,
        "total_outstanding": round(total_outstanding, 2),
        "green_count": counts.get("GREEN", 0),
        "amber_count": counts.get("AMBER", 0),
        "orange_count": counts.get("ORANGE", 0),
        "red_count": counts.get("RED", 0),
        "provinces": provinces,
    }


def early_warnings(db: Session, limit: int = 20) -> list[dict]:
    """Top early-warning borrowers sorted by risk probability."""
    results = (
        db.query(RiskScore, Farmer, Farm, Loan)
        .join(Farmer, RiskScore.farmer_id == Farmer.id)
        .join(Farm, RiskScore.farm_id == Farm.id)
        .join(Loan, RiskScore.loan_id == Loan.id)
        .filter(RiskScore.risk_bucket.in_(["AMBER", "ORANGE", "RED"]))
        .order_by(RiskScore.risk_probability.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "farmer_id": farmer.farmer_code,
            "farmer_name": farmer.name,
            "farm_id": farm.farm_code,
            "loan_id": loan.loan_code,
            "province": farmer.province,
            "risk_probability": rs.risk_probability,
            "risk_bucket": rs.risk_bucket,
            "confidence": rs.confidence,
            "outstanding": loan.outstanding_principal,
            "dpd": loan.dpd,
            "recommended_action": rs.recommended_action,
        }
        for rs, farmer, farm, loan in results
    ]


def dashboard_stats(db: Session) -> dict:
    total_alerts = db.query(func.count(Alert.id)).scalar()
    open_alerts = db.query(func.count(Alert.id)).filter(Alert.status == "open").scalar()
    acknowledged = db.query(func.count(Alert.id)).filter(Alert.status == "acknowledged").scalar()
    resolved = db.query(func.count(Alert.id)).filter(Alert.status.in_(["resolved", "dismissed"])).scalar()
    avg_risk = db.query(func.avg(RiskScore.risk_probability)).scalar() or 0
    total_loans = db.query(func.count(Loan.id)).scalar()
    total_loans_dpd = db.query(func.count(Loan.id)).filter(Loan.dpd > 0).scalar()

    return {
        "total_alerts": total_alerts,
        "open_alerts": open_alerts,
        "acknowledged_alerts": acknowledged,
        "resolved_alerts": resolved,
        "average_risk_score": round(float(avg_risk), 3),
        "total_loans": total_loans,
        "loans_with_dpd": total_loans_dpd,
        "dpd_rate": round(total_loans_dpd / total_loans * 100, 1) if total_loans > 0 else 0,
    }
