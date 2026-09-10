from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session

from app.models import Alert


def list_alerts(
    db: Session,
    status: Optional[str] = None,
    severity: Optional[str] = None,
    assigned_to: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
) -> list[Alert]:
    q = db.query(Alert)
    if status:
        q = q.filter(Alert.status == status)
    if severity:
        q = q.filter(Alert.severity == severity.upper())
    if assigned_to:
        q = q.filter(Alert.assigned_to == assigned_to)
    return q.order_by(Alert.created_at.desc()).offset(skip).limit(limit).all()


def get_alert(db: Session, alert_id: int) -> Optional[Alert]:
    return db.query(Alert).filter(Alert.id == alert_id).first()


def acknowledge_alert(db: Session, alert_id: int) -> Optional[Alert]:
    alert = get_alert(db, alert_id)
    if not alert:
        return None
    alert.status = "acknowledged"
    alert.acknowledged_at = datetime.utcnow()
    db.commit()
    return alert


def resolve_alert(db: Session, alert_id: int, action_taken: str = "No action needed") -> Optional[Alert]:
    alert = get_alert(db, alert_id)
    if not alert:
        return None
    alert.status = "resolved"
    alert.action_taken = action_taken
    alert.resolved_at = datetime.utcnow()
    db.commit()
    return alert


def dismiss_alert(db: Session, alert_id: int, reason: str = "") -> Optional[Alert]:
    alert = get_alert(db, alert_id)
    if not alert:
        return None
    alert.status = "dismissed"
    alert.action_taken = f"Dismissed: {reason}" if reason else "Dismissed"
    alert.resolved_at = datetime.utcnow()
    db.commit()
    return alert
