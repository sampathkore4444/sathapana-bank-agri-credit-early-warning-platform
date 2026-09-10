from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.alert import AlertResponse
from app.services import alert_service

router = APIRouter()


@router.get("/alerts")
def list_alerts(
    status: Optional[str] = None,
    severity: Optional[str] = None,
    assigned_to: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    return alert_service.list_alerts(
        db, status=status, severity=severity, assigned_to=assigned_to, skip=skip, limit=limit,
    )


@router.get("/alerts/{alert_id}")
def get_alert(alert_id: int, db: Session = Depends(get_db)):
    alert = alert_service.get_alert(db, alert_id)
    if not alert:
        raise HTTPException(404, "Alert not found")
    return alert


@router.patch("/alerts/{alert_id}/acknowledge")
def acknowledge_alert(alert_id: int, db: Session = Depends(get_db)):
    result = alert_service.acknowledge_alert(db, alert_id)
    if not result:
        raise HTTPException(404, "Alert not found")
    return {"status": "acknowledged"}


@router.patch("/alerts/{alert_id}/resolve")
def resolve_alert(
    alert_id: int,
    action_taken: str = "No action needed",
    db: Session = Depends(get_db),
):
    result = alert_service.resolve_alert(db, alert_id, action_taken)
    if not result:
        raise HTTPException(404, "Alert not found")
    return {"status": "resolved"}


@router.patch("/alerts/{alert_id}/dismiss")
def dismiss_alert(
    alert_id: int,
    reason: str = "",
    db: Session = Depends(get_db),
):
    result = alert_service.dismiss_alert(db, alert_id, reason)
    if not result:
        raise HTTPException(404, "Alert not found")
    return {"status": "dismissed"}
