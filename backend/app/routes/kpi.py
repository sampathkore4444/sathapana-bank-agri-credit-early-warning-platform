"""KPI tracking API routes — technical and business KPIs from the SPEC."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models import (
    Farmer, Farm, Loan, CropHealth, RiskScore, Alert,
)

router = APIRouter()


@router.get("/kpi/technical")
def technical_kpis(db: Session = Depends(get_db)):
    """Compute technical KPIs as defined in SPEC §14."""
    total_farmers = db.query(func.count(Farmer.id)).scalar()
    total_farms = db.query(func.count(Farm.id)).scalar()

    # Stage 1: Farm mapping
    farms_with_boundary = db.query(func.count(Farm.id)).filter(Farm.boundary_geojson.isnot(None)).scalar()
    mapping_rate = round(farms_with_boundary / total_farms * 100, 1) if total_farms > 0 else 0

    # Area estimation error
    farms_with_both = db.query(Farm).filter(
        Farm.area_hectares.isnot(None),
        Farm.area_satellite.isnot(None),
    ).all()
    if farms_with_both:
        area_errors = [
            abs(f.area_hectares - f.area_satellite) / f.area_hectares
            for f in farms_with_both if f.area_hectares > 0
        ]
        avg_area_error = round(sum(area_errors) / len(area_errors) * 100, 1) if area_errors else 0
    else:
        avg_area_error = 0

    # Stage 2: Crop health
    farms_with_health = db.query(func.count(func.distinct(CropHealth.farm_id))).scalar()
    monitoring_coverage = round(farms_with_health / total_farms * 100, 1) if total_farms > 0 else 0

    health_records = db.query(CropHealth).count()
    avg_confidence = db.query(func.avg(CropHealth.confidence)).scalar() or 0

    # Stage 3: Risk model
    farmers_scored = db.query(func.count(func.distinct(RiskScore.farmer_id))).scalar()
    scoring_rate = round(farmers_scored / total_farmers * 100, 1) if total_farmers > 0 else 0

    # Alerts
    total_alerts = db.query(func.count(Alert.id)).scalar()
    open_alerts = db.query(func.count(Alert.id)).filter(Alert.status == "open").scalar()
    resolved_alerts = db.query(func.count(Alert.id)).filter(
        Alert.status.in_(["resolved", "dismissed"])
    ).scalar()
    investigation_rate = round(resolved_alerts / total_alerts * 100, 1) if total_alerts > 0 else 0

    return {
        "stage_1_farm_mapping": {
            "farm_mapping_rate_pct": mapping_rate,
            "target": ">=90%",
            "status": "✅" if mapping_rate >= 90 else "⚠️",
            "area_estimation_error_pct": avg_area_error,
            "area_error_target": "<=10%",
            "area_error_status": "✅" if avg_area_error <= 10 else "⚠️",
        },
        "stage_2_crop_health": {
            "monitoring_coverage_pct": monitoring_coverage,
            "target": ">=90%",
            "status": "✅" if monitoring_coverage >= 90 else "⚠️",
            "total_observations": health_records,
            "avg_confidence": round(float(avg_confidence), 3),
        },
        "stage_3_risk_model": {
            "farmers_scored_pct": scoring_rate,
            "farmers_scored": farmers_scored,
            "total_farmers": total_farmers,
        },
        "alerts": {
            "total_alerts": total_alerts,
            "open_alerts": open_alerts,
            "resolved_alerts": resolved_alerts,
            "investigation_rate_pct": investigation_rate,
            "investigation_target": ">=70%",
            "status": "✅" if investigation_rate >= 70 else "⚠️",
        },
    }


@router.get("/kpi/business")
def business_kpis(db: Session = Depends(get_db)):
    """Compute business KPIs as defined in SPEC §14."""
    total_loans = db.query(func.count(Loan.id)).scalar()
    total_outstanding = db.query(func.sum(Loan.outstanding_principal)).scalar() or 0

    dpd_count = db.query(func.count(Loan.id)).filter(Loan.dpd > 0).scalar()
    dpd_30_plus = db.query(func.count(Loan.id)).filter(Loan.dpd >= 30).scalar()
    dpd_60_plus = db.query(func.count(Loan.id)).filter(Loan.dpd >= 60).scalar()
    restructured = db.query(func.count(Loan.id)).filter(Loan.restructured == True).scalar()

    # Risk distribution
    risk_scores = db.query(RiskScore).all()
    high_risk_detected = sum(1 for r in risk_scores if r.risk_bucket in ("ORANGE", "RED"))

    # Alerts by severity
    critical_alerts = db.query(func.count(Alert.id)).filter(Alert.severity == "CRITICAL").scalar()
    high_alerts = db.query(func.count(Alert.id)).filter(Alert.severity == "HIGH").scalar()

    return {
        "portfolio": {
            "total_loans": total_loans,
            "total_outstanding_usd": round(total_outstanding, 2),
            "dpd_rate_pct": round(dpd_count / total_loans * 100, 1) if total_loans > 0 else 0,
            "dpd_30_plus_rate_pct": round(dpd_30_plus / total_loans * 100, 1) if total_loans > 0 else 0,
            "dpd_60_plus_rate_pct": round(dpd_60_plus / total_loans * 100, 1) if total_loans > 0 else 0,
            "restructuring_rate_pct": round(restructured / total_loans * 100, 1) if total_loans > 0 else 0,
        },
        "risk_detection": {
            "high_risk_detected": high_risk_detected,
            "total_scored": len(risk_scores),
            "detection_rate_pct": round(high_risk_detected / len(risk_scores) * 100, 1) if risk_scores else 0,
            "detection_target": ">=70-80%",
        },
        "alert_volume": {
            "critical_alerts": critical_alerts,
            "high_alerts": high_alerts,
        },
    }
