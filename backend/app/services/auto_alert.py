"""Automatic alert generation when risk scores cross thresholds.

Implements the SPEC §12 alert workflow:
- Risk score crosses threshold → alert generated
- Alert includes ID, farmer details, risk score, drivers, recommended action
"""
from datetime import datetime
from sqlalchemy.orm import Session

from app.models import Alert, RiskScore, Farmer, Farm, Loan
from app.services.notification_service import send_critical_alert


def check_and_generate_alerts(db: Session) -> dict:
    """Check all risk scores for threshold crossings and generate alerts.

    Returns:
        Summary of alerts generated.
    """
    farmers = db.query(Farmer).all()
    alerts_created = 0
    alerts_skipped = 0

    for farmer in farmers:
        # Get latest risk score
        rs = (
            db.query(RiskScore)
            .filter(RiskScore.farmer_id == farmer.id)
            .order_by(RiskScore.scoring_date.desc())
            .first()
        )
        if not rs:
            continue

        # Check if already has an open alert for this farmer
        existing = (
            db.query(Alert)
            .filter(
                Alert.farm_id == rs.farm_id,
                Alert.status.in_(["open", "acknowledged"]),
            )
            .first()
        )
        if existing:
            alerts_skipped += 1
            continue

        # Generate alert if threshold crossed
        alert = _create_alert_if_threshold_crossed(db, rs, farmer)
        if alert:
            alerts_created += 1

    db.commit()

    return {
        "alerts_created": alerts_created,
        "alerts_skipped_existing": alerts_skipped,
        "total_farmers_checked": len(farmers),
    }


def _create_alert_if_threshold_crossed(db: Session, rs: RiskScore, farmer: Farmer) -> Alert:
    """Create an alert if the risk score crosses a threshold."""
    from json import loads

    # Get farm
    farm = db.query(Farm).filter(Farm.id == rs.farm_id).first()
    if not farm:
        return None

    # Determine if this is a new escalation
    if rs.risk_bucket == "RED":
        severity = "CRITICAL"
        alert_type = "risk_escalation"
        title = "Risk score escalated to CRITICAL — urgent intervention required"
    elif rs.risk_bucket == "ORANGE":
        severity = "HIGH"
        alert_type = "risk_escalation"
        title = "Risk score escalated to HIGH — RM contact needed"
    elif rs.risk_bucket == "AMBER":
        severity = "MEDIUM"
        alert_type = "crop_stress"
        title = "Risk score in WATCH zone — enhanced monitoring"
    else:
        return None  # GREEN — no alert

    # Get primary drivers
    drivers = loads(rs.primary_drivers_json) if rs.primary_drivers_json else []
    driver_summary = ", ".join(
        d["feature"].replace("_", " ") for d in drivers[:3]
    ) if drivers else "multiple factors"

    # Get assigned RM (from loan or alert history)
    loan = db.query(Loan).filter(Loan.farmer_id == farmer.id).first()
    assigned_rm = _get_rm_for_province(farmer.province)

    # Create alert
    alert_count = db.query(Alert).count()
    alert = Alert(
        alert_code=f"ALT-2026-{alert_count + 1:06d}",
        farm_id=farm.id,
        risk_score_id=rs.id,
        alert_type=alert_type,
        severity=severity,
        title=title,
        description=(
            f"Risk probability: {rs.risk_probability:.0%}. "
            f"Primary drivers: {driver_summary}. "
            f"Loan outstanding: ${loan.outstanding_principal:,.0f}." if loan else
            f"Risk probability: {rs.risk_probability:.0%}. "
            f"Primary drivers: {driver_summary}."
        ),
        risk_score_value=rs.risk_probability,
        status="open",
        assigned_to=assigned_rm,
    )
    db.add(alert)

    # Send immediate notification for critical
    if severity == "CRITICAL":
        send_critical_alert(alert, farmer, farm, rs)

    return alert


def _get_rm_for_province(province: str) -> str:
    """Map province to assigned RM."""
    rm_map = {
        "Battambang": "Sovannara",
        "Siem Reap": "Dara",
        "Kampong Cham": "Chantrea",
    }
    return rm_map.get(province, "Sovannara")
