"""Pilot vs Control group API routes."""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.services import pilot_service

router = APIRouter()


@router.post("/pilot/assign")
def assign_groups(
    pilot_ratio: float = Query(0.7, description="Fraction assigned to pilot group"),
    seed: int = Query(42, description="Random seed for reproducibility"),
    db: Session = Depends(get_db),
):
    """Randomly assign farmers to pilot and control groups."""
    return pilot_service.assign_pilot_groups(db, pilot_ratio=pilot_ratio, seed=seed)


@router.get("/pilot/groups")
def get_assignments(db: Session = Depends(get_db)):
    """Get current pilot/control group assignments."""
    return pilot_service.get_group_assignments(db)


@router.get("/pilot/compare")
def compare_outcomes(db: Session = Depends(get_db)):
    """Compare outcomes between pilot and control groups."""
    return pilot_service.compare_outcomes(db)


@router.post("/pilot/outcome/{farmer_id}")
def record_outcome(
    farmer_id: int,
    dpd_30_ever: bool = False,
    dpd_60_ever: bool = False,
    npl_migration: bool = False,
    restructured: bool = False,
    days_to_rm_intervention: Optional[int] = None,
    rm_intervened: bool = False,
    recovered: bool = False,
    loss_amount: float = 0.0,
    db: Session = Depends(get_db),
):
    """Record an outcome measurement for a farmer."""
    return pilot_service.record_outcome(
        db, farmer_id,
        dpd_30_ever=dpd_30_ever,
        dpd_60_ever=dpd_60_ever,
        npl_migration=npl_migration,
        restructured=restructured,
        days_to_rm_intervention=days_to_rm_intervention,
        rm_intervened=rm_intervened,
        recovered=recovered,
        loss_amount=loss_amount,
    )
