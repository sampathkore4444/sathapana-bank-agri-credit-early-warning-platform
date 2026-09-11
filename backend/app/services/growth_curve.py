"""Crop growth curve model for rice in Cambodia.

Establishes normal NDVI growth curves per province and detects
deviations that indicate crop stress.
"""
from datetime import date, timedelta
from typing import Optional
import logging
import math
from sqlalchemy.orm import Session

from app.models import CropHealth, Farm, Farmer

logger = logging.getLogger(__name__)


# Normal rice growth curve parameters for Cambodia
# Based on published research (Zhang et al. 2026, FAO Cambodia)
RICE_GROWTH_CURVE = {
    "battambang": {
        "planting_day": 170,   # ~June 19
        "phases": [
            {"name": "bare_soil", "start": -10, "end": 15, "ndvi_mean": 0.25, "ndvi_std": 0.05},
            {"name": "early_vegetative", "start": 15, "end": 45, "ndvi_mean": 0.40, "ndvi_std": 0.08},
            {"name": "active_vegetative", "start": 45, "end": 90, "ndvi_mean": 0.65, "ndvi_std": 0.07},
            {"name": "reproductive", "start": 90, "end": 130, "ndvi_mean": 0.78, "ndvi_std": 0.06},
            {"name": "maturity", "start": 130, "end": 155, "ndvi_mean": 0.65, "ndvi_std": 0.08},
            {"name": "harvest", "start": 155, "end": 170, "ndvi_mean": 0.30, "ndvi_std": 0.06},
        ],
    },
    "siem reap": {
        "planting_day": 165,
        "phases": [
            {"name": "bare_soil", "start": -10, "end": 15, "ndvi_mean": 0.24, "ndvi_std": 0.05},
            {"name": "early_vegetative", "start": 15, "end": 45, "ndvi_mean": 0.38, "ndvi_std": 0.08},
            {"name": "active_vegetative", "start": 45, "end": 90, "ndvi_mean": 0.62, "ndvi_std": 0.07},
            {"name": "reproductive", "start": 90, "end": 130, "ndvi_mean": 0.76, "ndvi_std": 0.06},
            {"name": "maturity", "start": 130, "end": 155, "ndvi_mean": 0.63, "ndvi_std": 0.08},
            {"name": "harvest", "start": 155, "end": 170, "ndvi_mean": 0.28, "ndvi_std": 0.06},
        ],
    },
    "kampong cham": {
        "planting_day": 168,
        "phases": [
            {"name": "bare_soil", "start": -10, "end": 15, "ndvi_mean": 0.26, "ndvi_std": 0.05},
            {"name": "early_vegetative", "start": 15, "end": 45, "ndvi_mean": 0.42, "ndvi_std": 0.08},
            {"name": "active_vegetative", "start": 45, "end": 90, "ndvi_mean": 0.67, "ndvi_std": 0.07},
            {"name": "reproductive", "start": 90, "end": 130, "ndvi_mean": 0.80, "ndvi_std": 0.06},
            {"name": "maturity", "start": 130, "end": 155, "ndvi_mean": 0.67, "ndvi_std": 0.08},
            {"name": "harvest", "start": 155, "end": 170, "ndvi_mean": 0.32, "ndvi_std": 0.06},
        ],
    },
}

# Default curve for unknown provinces
DEFAULT_CURVE = {
    "planting_day": 168,
    "phases": [
        {"name": "bare_soil", "start": -10, "end": 15, "ndvi_mean": 0.25, "ndvi_std": 0.05},
        {"name": "early_vegetative", "start": 15, "end": 45, "ndvi_mean": 0.40, "ndvi_std": 0.08},
        {"name": "active_vegetative", "start": 45, "end": 90, "ndvi_mean": 0.65, "ndvi_std": 0.07},
        {"name": "reproductive", "start": 90, "end": 130, "ndvi_mean": 0.78, "ndvi_std": 0.06},
        {"name": "maturity", "start": 130, "end": 155, "ndvi_mean": 0.65, "ndvi_std": 0.08},
        {"name": "harvest", "start": 155, "end": 170, "ndvi_mean": 0.30, "ndvi_std": 0.06},
    ],
}


def get_province_curve(province: str) -> dict:
    """Get the growth curve for a province."""
    key = province.lower().strip()
    return RICE_GROWTH_CURVE.get(key, DEFAULT_CURVE)


def get_expected_ndvi(province: str, days_since_planting: int) -> dict:
    """Get expected NDVI and growth stage for a given crop age.

    Returns:
        Dict with expected_ndvi, stage_name, ndvi_range.
    """
    curve = get_province_curve(province)

    for phase in curve["phases"]:
        if phase["start"] <= days_since_planting < phase["end"]:
            return {
                "expected_ndvi": phase["ndvi_mean"],
                "stage_name": phase["name"],
                "ndvi_range": (
                    round(phase["ndvi_mean"] - 2 * phase["ndvi_std"], 3),
                    round(phase["ndvi_mean"] + 2 * phase["ndvi_std"], 3),
                ),
                "phase_progress": round(
                    (days_since_planting - phase["start"]) / (phase["end"] - phase["start"]), 2
                ),
            }

    # Default: pre-planting or post-harvest
    return {
        "expected_ndvi": 0.25,
        "stage_name": "off_season",
        "ndvi_range": (0.15, 0.35),
        "phase_progress": 0,
    }


def detect_growth_deviation(
    db: Session,
    farm_id: int,
) -> dict:
    """Compare observed NDVI against the normal growth curve.

    Returns:
        Dict with deviation analysis.
    """
    try:
        return _detect_growth_deviation(db, farm_id)
    except Exception as exc:
        logger.exception("Failed to detect growth deviation for farm_id=%s", farm_id)
        return {"error": "Failed to compute growth deviation", "detail": str(exc)}


def _detect_growth_deviation(db: Session, farm_id: int) -> dict:
    farm = db.query(Farm).filter(Farm.id == farm_id).first()
    if not farm or not farm.planting_date:
        return {"error": "No planting date available"}

    farmer = db.query(Farmer).filter(Farmer.id == farm.farmer_id).first()
    if not farmer:
        return {"error": "No farmer found"}

    days_since_planting = (date.today() - farm.planting_date).days
    expected = get_expected_ndvi(farmer.province, days_since_planting)

    # Get latest observation
    latest = (
        db.query(CropHealth)
        .filter(CropHealth.farm_id == farm_id)
        .order_by(CropHealth.observation_date.desc())
        .first()
    )
    if not latest:
        return {"error": "No crop health data"}

    actual_ndvi = latest.ndvi_current
    expected_ndvi = expected["expected_ndvi"]
    deviation = round((actual_ndvi - expected_ndvi) / expected_ndvi * 100, 1) if expected_ndvi > 0 else 0

    # Classify deviation severity
    curve = get_province_curve(farmer.province)
    std = 0.07  # average std
    for phase in curve["phases"]:
        if phase["start"] <= days_since_planting < phase["end"]:
            std = phase["ndvi_std"]
            break

    z_score = (actual_ndvi - expected_ndvi) / std if std > 0 else 0

    if z_score < -2.5:
        severity = "critical"
    elif z_score < -1.5:
        severity = "significant"
    elif z_score < -0.5:
        severity = "mild"
    else:
        severity = "normal"

    return {
        "farm_id": farm.farm_code,
        "province": farmer.province,
        "days_since_planting": days_since_planting,
        "growth_stage": expected["stage_name"],
        "phase_progress": expected["phase_progress"],
        "expected_ndvi": expected_ndvi,
        "actual_ndvi": actual_ndvi,
        "deviation_pct": deviation,
        "z_score": round(z_score, 2),
        "severity": severity,
        "ndvi_range_expected": expected["ndvi_range"],
    }
