"""Pilot vs Control group management and comparison.

Handles randomization, stratification, and outcome measurement
for the A/B experiment design described in the SPEC.
"""
import random
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models import Farmer, Loan, RiskScore
from app.models.pilot_group import PilotGroup, PilotOutcome


def assign_pilot_groups(
    db: Session,
    pilot_ratio: float = 0.7,
    seed: int = 42,
) -> dict:
    """Randomly assign farmers to pilot and control groups.

    Stratifies by province and loan size to ensure balance.
    """
    # Clear existing assignments
    db.query(PilotGroup).delete()
    db.commit()

    farmers = db.query(Farmer).all()
    random.seed(seed)

    # Stratify by province
    provinces = {}
    for farmer in farmers:
        provinces.setdefault(farmer.province, []).append(farmer)

    assigned = {"pilot": 0, "control": 0}

    for province, prov_farmers in provinces.items():
        # Get loan sizes for stratification
        for farmer in prov_farmers:
            loan = (
                db.query(Loan)
                .filter(Loan.farmer_id == farmer.id, Loan.status == "active")
                .first()
            )
            outstanding = loan.outstanding_principal if loan else 0

            if outstanding < 3000:
                bucket = "small"
            elif outstanding < 8000:
                bucket = "medium"
            else:
                bucket = "large"

            group = "pilot" if random.random() < pilot_ratio else "control"

            db.add(PilotGroup(
                farmer_id=farmer.id,
                group_type=group,
                province=province,
                loan_size_bucket=bucket,
                crop_type="rice",
            ))
            assigned[group] += 1

    db.commit()

    return {
        "total": len(farmers),
        "pilot": assigned["pilot"],
        "control": assigned["control"],
        "pilot_ratio": round(assigned["pilot"] / len(farmers), 2) if farmers else 0,
    }


def get_group_assignments(db: Session) -> dict:
    """Get current pilot/control group assignments."""
    groups = db.query(PilotGroup).all()

    result = {
        "pilot": {"count": 0, "provinces": {}},
        "control": {"count": 0, "provinces": {}},
        "total": len(groups),
    }

    for g in groups:
        group = result[g.group_type]
        group["count"] += 1
        group["provinces"].setdefault(g.province, 0)
        group["provinces"][g.province] += 1

    return result


def compare_outcomes(db: Session) -> dict:
    """Compare outcomes between pilot and control groups.

    Returns:
        Dict with comparison metrics per group.
    """
    groups = db.query(PilotGroup).all()
    pilot_farmer_ids = [g.farmer_id for g in groups if g.group_type == "pilot"]
    control_farmer_ids = [g.farmer_id for g in groups if g.group_type == "control"]

    def compute_group_metrics(farmer_ids: list[int]) -> dict:
        if not farmer_ids:
            return {"count": 0}

        # Get loans
        loans = db.query(Loan).filter(Loan.farmer_id.in_(farmer_ids)).all()
        total_outstanding = sum(l.outstanding_principal for l in loans)
        dpd_count = sum(1 for l in loans if l.dpd > 0)
        dpd_30_plus = sum(1 for l in loans if l.dpd >= 30)

        # Get risk scores
        risk_scores = (
            db.query(RiskScore)
            .filter(RiskScore.farmer_id.in_(farmer_ids))
            .all()
        )
        high_risk = sum(1 for r in risk_scores if r.risk_bucket in ("ORANGE", "RED"))

        return {
            "count": len(farmer_ids),
            "total_outstanding": round(total_outstanding, 2),
            "dpd_rate": round(dpd_count / len(loans) * 100, 1) if loans else 0,
            "dpd_30_plus_rate": round(dpd_30_plus / len(loans) * 100, 1) if loans else 0,
            "high_risk_count": high_risk,
            "high_risk_pct": round(high_risk / len(risk_scores) * 100, 1) if risk_scores else 0,
            "avg_risk_score": round(
                sum(r.risk_probability for r in risk_scores) / len(risk_scores), 3
            ) if risk_scores else 0,
        }

    pilot_metrics = compute_group_metrics(pilot_farmer_ids)
    control_metrics = compute_group_metrics(control_farmer_ids)

    # Compute differences
    comparison = {}
    for key in ["dpd_rate", "dpd_30_plus_rate", "high_risk_pct", "avg_risk_score"]:
        p_val = pilot_metrics.get(key, 0)
        c_val = control_metrics.get(key, 0)
        comparison[key] = {
            "pilot": p_val,
            "control": c_val,
            "difference": round(p_val - c_val, 3),
            "relative_diff_pct": round((p_val - c_val) / c_val * 100, 1) if c_val > 0 else 0,
        }

    return {
        "pilot": pilot_metrics,
        "control": control_metrics,
        "comparison": comparison,
        "statistical_note": "Full statistical significance testing requires production data with sufficient sample size.",
    }


def record_outcome(
    db: Session,
    farmer_id: int,
    dpd_30_ever: bool = False,
    dpd_60_ever: bool = False,
    npl_migration: bool = False,
    restructured: bool = False,
    days_to_rm_intervention: Optional[int] = None,
    rm_intervened: bool = False,
    recovered: bool = False,
    loss_amount: float = 0.0,
) -> dict:
    """Record an outcome for a farmer."""
    group = db.query(PilotGroup).filter(PilotGroup.farmer_id == farmer_id).first()
    if not group:
        return {"error": "Farmer not assigned to any group"}

    outcome = PilotOutcome(
        farmer_id=farmer_id,
        group_type=group.group_type,
        dpd_30_ever=dpd_30_ever,
        dpd_60_ever=dpd_60_ever,
        npl_migration=npl_migration,
        restructured=restructured,
        days_to_rm_intervention=days_to_rm_intervention,
        rm_intervened=rm_intervened,
        recovered=recovered,
        loss_amount=loss_amount,
    )
    db.add(outcome)
    db.commit()

    return {"status": "recorded", "group": group.group_type}
