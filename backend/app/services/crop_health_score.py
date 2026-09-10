"""Crop Health Score computation using the SPEC §9 weighted formula.

Score = NDVI_deviation (30%) + NDVI_trend (20%) + NDWI (15%)
      + SAR_moisture (10%) + Rainfall_deviation (15%) + Temperature_stress (10%)

Each component is normalized to 0-100, then combined with weights.
"""
from typing import Optional
import numpy as np


# Weights from SPEC §9
WEIGHTS = {
    "ndvi_deviation": 0.30,
    "ndvi_trend": 0.20,
    "ndwi": 0.15,
    "sar_moisture": 0.10,
    "rainfall_deviation": 0.15,
    "temperature_stress": 0.10,
}


def normalize_ndvi_deviation(deviation_pct: float) -> float:
    """Convert NDVI deviation to 0-100 score.

    -50% → 0 (severe stress)
     0%  → 50 (normal)
    +20% → 100 (excellent)
    """
    score = 50 + deviation_pct * 2.5
    return max(0, min(100, score))


def normalize_ndvi_trend(trend_slope: float) -> float:
    """Convert NDVI trend slope to 0-100 score.

    -0.02 → 0 (rapid decline)
     0.00 → 50 (stable)
    +0.02 → 100 (improving)
    """
    score = 50 + trend_slope * 2500
    return max(0, min(100, score))


def normalize_ndwi(ndwi: float) -> float:
    """Convert NDWI to 0-100 score.

    -0.2 → 0 (very dry)
     0.0 → 50 (moderate)
    +0.3 → 100 (well-watered)
    """
    score = (ndwi + 0.2) / 0.5 * 100
    return max(0, min(100, score))


def normalize_sar_moisture(vh_backscatter: float) -> float:
    """Convert SAR VH backscatter to 0-100 score.

    -20 dB → 0 (dry/flooded)
    -12 dB → 50 (normal)
     -5 dB → 100 (high moisture)
    """
    score = (vh_backscatter + 20) / 15 * 100
    return max(0, min(100, score))


def normalize_rainfall(deviation_pct: float) -> float:
    """Convert rainfall deviation to 0-100 score.

    -60% → 0 (severe drought)
     0%  → 50 (normal)
    +50% → 100 (excess)
    """
    score = 50 + deviation_pct * 0.83
    return max(0, min(100, score))


def normalize_temperature_stress(stress_days: int, max_days: int = 30) -> float:
    """Convert temperature stress days to 0-100 score.

    0 stress days → 100 (no stress)
    30 stress days → 0 (constant stress)
    """
    score = 100 * (1 - stress_days / max_days)
    return max(0, min(100, score))


def compute_crop_health_score(
    ndvi_deviation_pct: float = 0,
    ndvi_trend_slope: float = 0,
    ndwi: float = 0,
    sar_vh_backscatter: float = -12,
    rainfall_deviation_pct: float = 0,
    temperature_stress_days: int = 0,
) -> dict:
    """Compute the composite Crop Health Score.

    Returns:
        Dict with total_score (0-100), component scores, and status.
    """
    components = {
        "ndvi_deviation": normalize_ndvi_deviation(ndvi_deviation_pct),
        "ndvi_trend": normalize_ndvi_trend(ndvi_trend_slope),
        "ndwi": normalize_ndwi(ndwi),
        "sar_moisture": normalize_sar_moisture(sar_vh_backscatter),
        "rainfall_deviation": normalize_rainfall(rainfall_deviation_pct),
        "temperature_stress": normalize_temperature_stress(temperature_stress_days),
    }

    # Weighted sum
    total = sum(
        components[k] * WEIGHTS[k] for k in WEIGHTS
    )
    total = round(max(0, min(100, total)), 1)

    # Status classification (SPEC §9)
    if total >= 80:
        status = "green"
    elif total >= 60:
        status = "yellow"
    elif total >= 40:
        status = "orange"
    else:
        status = "red"

    return {
        "crop_health_score": round(total),
        "status": status,
        "components": {k: round(v, 1) for k, v in components.items()},
        "weights": WEIGHTS,
        "confidence": 0.85,
    }


def recompute_farm_health(db, farm_id: int) -> Optional[dict]:
    """Recompute crop health score from latest observations.

    Uses actual satellite data instead of pre-seeded values.
    """
    from app.models import CropHealth
    from app.services.growth_curve import detect_growth_deviation
    from datetime import timedelta

    # Get recent observations
    recent = (
        db.query(CropHealth)
        .filter(CropHealth.farm_id == farm_id)
        .order_by(CropHealth.observation_date.desc())
        .limit(5)
        .all()
    )
    if not recent:
        return None

    latest = recent[0]

    # Compute NDVI trend slope
    ndvi_values = [r.ndvi_current for r in reversed(recent)]
    if len(ndvi_values) >= 2:
        n = len(ndvi_values)
        x_mean = (n - 1) / 2
        y_mean = sum(ndvi_values) / n
        num = sum((i - x_mean) * (v - y_mean) for i, v in enumerate(ndvi_values))
        den = sum((i - x_mean) ** 2 for i in range(n))
        trend_slope = num / den if den > 0 else 0
    else:
        trend_slope = 0

    # Compute score
    result = compute_crop_health_score(
        ndvi_deviation_pct=latest.ndvi_deviation_pct,
        ndvi_trend_slope=trend_slope,
        ndwi=latest.ndwi_current,
        sar_vh_backscatter=latest.sar_vh_backscatter,
        rainfall_deviation_pct=latest.rainfall_deviation_30d,
        temperature_stress_days=latest.temperature_stress_days,
    )

    # Update the record
    latest.crop_health_score = result["crop_health_score"]
    latest.status = result["status"]
    latest.ndvi_trend = "declining" if trend_slope < -0.005 else "improving" if trend_slope > 0.005 else "stable"

    db.commit()
    return result
