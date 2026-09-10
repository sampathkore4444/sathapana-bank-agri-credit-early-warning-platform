"""Feature engineering pipeline for the credit risk model.

Computes per-farm features from satellite indices, weather data,
and financial snapshots — ready for model training/inference.
"""
import json
from datetime import date, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models import (
    Farm, Farmer, Loan, CropHealth, RiskScore,
    FinancialSnapshot, Alert,
)


def compute_satellite_features(db: Session, farm_id: int) -> dict:
    """Compute satellite/environmental features for a single farm."""
    # Get latest crop health
    latest = (
        db.query(CropHealth)
        .filter(CropHealth.farm_id == farm_id)
        .order_by(CropHealth.observation_date.desc())
        .first()
    )
    if not latest:
        return {}

    # Get last 3 and 5 observations for trend
    recent = (
        db.query(CropHealth)
        .filter(CropHealth.farm_id == farm_id)
        .order_by(CropHealth.observation_date.desc())
        .limit(5)
        .all()
    )

    ndvi_values = [r.ndvi_current for r in reversed(recent)]

    # Compute NDVI trend (slope over last observations)
    def trend_slope(values):
        if len(values) < 2:
            return 0
        n = len(values)
        x_mean = (n - 1) / 2
        y_mean = sum(values) / n
        num = sum((i - x_mean) * (v - y_mean) for i, v in enumerate(values))
        den = sum((i - x_mean) ** 2 for i in range(n))
        return round(num / den, 4) if den > 0 else 0

    ndvi_trend_3 = trend_slope(ndvi_values[-3:]) if len(ndvi_values) >= 3 else 0
    ndvi_trend_5 = trend_slope(ndvi_values) if len(ndvi_values) >= 2 else 0

    # Days since last clear observation
    days_since_obs = (date.today() - latest.observation_date).days

    # Get 60-day rainfall if available (two records back)
    rainfall_60d_dev = latest.rainfall_deviation_30d  # fallback
    if len(recent) >= 4:
        rainfall_60d_dev = (sum(r.rainfall_30d for r in recent[:4]) / 4 - 145) / 145 * 100

    return {
        "ndvi_current": latest.ndvi_current,
        "ndvi_deviation_pct": latest.ndvi_deviation_pct,
        "ndvi_trend_3obs": ndvi_trend_3,
        "ndvi_trend_5obs": ndvi_trend_5,
        "ndwi_current": latest.ndwi_current,
        "crop_health_score": latest.crop_health_score,
        "growth_stage": latest.growth_stage,
        "flood_exposure": int(latest.flood_exposure),
        "drought_stress": int(latest.drought_stress),
        "rainfall_deviation_30d": latest.rainfall_deviation_30d,
        "rainfall_deviation_60d": round(rainfall_60d_dev, 1),
        "temperature_stress_days": latest.temperature_stress_days,
        "days_since_last_clear_obs": days_since_obs,
    }


def compute_farm_features(db: Session, farm_id: int) -> dict:
    """Compute farm/agricultural features."""
    farm = db.query(Farm).filter(Farm.id == farm_id).first()
    if not farm:
        return {}

    days_since_planting = 0
    days_to_harvest = 0
    if farm.planting_date:
        days_since_planting = (date.today() - farm.planting_date).days
    if farm.expected_harvest:
        days_to_harvest = (farm.expected_harvest - date.today()).days

    # Province risk factor: historical high-risk ratio
    farmer = db.query(Farmer).filter(Farmer.id == farm.farmer_id).first()
    province_risk = 0.0
    if farmer:
        province_farmer_ids = [
            f.id for f in db.query(Farmer.id).filter(Farmer.province == farmer.province).all()
        ]
        total = db.query(func.count(RiskScore.id)).filter(
            RiskScore.farmer_id.in_(province_farmer_ids)
        ).scalar() or 1
        high_risk = db.query(func.count(RiskScore.id)).filter(
            RiskScore.farmer_id.in_(province_farmer_ids),
            RiskScore.risk_bucket.in_(["ORANGE", "RED"]),
        ).scalar() or 0
        province_risk = round(high_risk / total, 3)

    return {
        "farm_area_hectares": farm.area_hectares,
        "crop_type_rice": 1 if farm.crop_type == "rice" else 0,
        "planting_day_of_year": farm.planting_date.timetuple().tm_yday if farm.planting_date else 0,
        "days_since_planting": days_since_planting,
        "days_to_harvest": max(0, days_to_harvest),
        "is_wet_season": 1 if farm.season == "wet" else 0,
        "province_risk_factor": province_risk,
    }


def compute_financial_features(db: Session, farmer_id: int) -> dict:
    """Compute financial/banking features from latest snapshot + loan."""
    # Latest financial snapshot
    snap = (
        db.query(FinancialSnapshot)
        .filter(FinancialSnapshot.farmer_id == farmer_id)
        .order_by(FinancialSnapshot.snapshot_date.desc())
        .first()
    )

    # Active loan
    loan = (
        db.query(Loan)
        .filter(Loan.farmer_id == farmer_id, Loan.status == "active")
        .order_by(Loan.id.desc())
        .first()
    )

    features = {
        "loan_outstanding": 0.0,
        "installment_amount": 0.0,
        "dpd": 0,
        "dpd_max_90d": 0,
        "missed_payments_count": 0,
        "restructured": 0,
        "deposit_balance_trend_30d": 0.0,
        "deposit_balance_trend_60d": 0.0,
        "transaction_count_30d": 0,
        "cash_inflow_30d_60d_ratio": 1.0,
        "cash_outflow_30d_60d_ratio": 1.0,
        "days_since_last_deposit": 999,
        "balance_to_installment_ratio": 0.0,
        "agricultural_income_detected": 0,
    }

    if loan:
        features.update({
            "loan_outstanding": loan.outstanding_principal,
            "installment_amount": loan.monthly_installment,
            "dpd": loan.dpd,
            "dpd_max_90d": loan.dpd_max_90d,
            "missed_payments_count": loan.missed_payments_count,
            "restructured": int(loan.restructured),
        })

    if snap:
        features.update({
            "deposit_balance_trend_30d": snap.deposit_balance_trend_30d,
            "deposit_balance_trend_60d": snap.deposit_balance_trend_60d,
            "transaction_count_30d": snap.transaction_count_30d,
            "cash_inflow_30d_60d_ratio": snap.cash_inflow_30d_60d_ratio,
            "cash_outflow_30d_60d_ratio": snap.cash_outflow_30d_60d_ratio,
            "days_since_last_deposit": snap.days_since_last_deposit,
            "balance_to_installment_ratio": snap.balance_to_installment_ratio,
            "agricultural_income_detected": int(snap.agricultural_income_detected),
        })

        # Temporal / behavioral features (SPEC §10)
        # Repayment consistency: inverse of missed payments
        repayment_consistency = max(0, 1.0 - loan.missed_payments_count * 0.2) if loan else 0.5
        # Seasonal cash flow: based on deposit balance trends
        seasonal_pattern = 0.5
        if snap.deposit_balance_trend_30d < -0.2 and snap.deposit_balance_trend_60d < 0:
            seasonal_pattern = 0.2  # declining pattern
        elif snap.deposit_balance_trend_30d > 0.1:
            seasonal_pattern = 0.8  # improving pattern
        # Anomaly: deviation from expected transaction behavior
        anomaly_score = 0.0
        if snap.cash_inflow_30d_60d_ratio < 0.7:
            anomaly_score += 0.3
        if snap.days_since_last_deposit > 30:
            anomaly_score += 0.2
        if snap.transaction_count_30d < 3:
            anomaly_score += 0.1

        features.update({
            "repayment_consistency_score": round(repayment_consistency, 3),
            "seasonal_cash_flow_pattern": round(seasonal_pattern, 3),
            "deviation_from_normal_behavior": round(min(anomaly_score, 1.0), 3),
        })

    return features


def compute_all_features(db: Session, farmer_id: int) -> dict:
    """Compute the full feature vector for a farmer."""
    # Find farm
    farm = db.query(Farm).filter(Farm.farmer_id == farmer_id).first()
    if not farm:
        return {}

    satellite = compute_satellite_features(db, farm.id)
    farm_feats = compute_farm_features(db, farm.id)
    financial = compute_financial_features(db, farmer_id)

    # Merge all features
    features = {}
    features.update(satellite)
    features.update(farm_feats)
    features.update(financial)

    return features


def build_training_dataset(db: Session) -> tuple[list[dict], list[int], list[int]]:
    """Build feature matrix and labels for model training.

    Returns:
        (X, y, farmer_ids) where X is list of feature dicts,
        y is binary labels, farmer_ids for reference.
    """
    farmers = db.query(Farmer).all()
    X = []
    y = []
    farmer_ids = []

    for farmer in farmers:
        features = compute_all_features(db, farmer.id)
        if not features:
            continue

        # Build label: is this farmer currently high-risk?
        rs = (
            db.query(RiskScore)
            .filter(RiskScore.farmer_id == farmer.id)
            .order_by(RiskScore.scoring_date.desc())
            .first()
        )
        if not rs:
            continue

        label = 1 if rs.risk_bucket in ("ORANGE", "RED") else 0
        X.append(features)
        y.append(label)
        farmer_ids.append(farmer.id)

    return X, y, farmer_ids
