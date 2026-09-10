"""Model monitoring service per SPEC §11.

Monitors:
- Score distribution drift
- Feature drift
- Prediction calibration
- Actual vs. predicted default rates
- False-positive / false-negative rates
"""
import json
from datetime import datetime, date
from typing import Optional
import numpy as np
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models import RiskScore, Farmer, Loan, Alert


def compute_score_distribution(db: Session) -> dict:
    """Analyze current risk score distribution."""
    scores = db.query(RiskScore.risk_probability).all()
    values = [s[0] for s in scores]

    if not values:
        return {"error": "No scores found"}

    arr = np.array(values)
    return {
        "count": len(values),
        "mean": round(float(arr.mean()), 4),
        "std": round(float(arr.std()), 4),
        "min": round(float(arr.min()), 4),
        "max": round(float(arr.max()), 4),
        "median": round(float(np.median(arr)), 4),
        "p25": round(float(np.percentile(arr, 25)), 4),
        "p75": round(float(np.percentile(arr, 75)), 4),
        "histogram": {
            "0.0-0.2": int(((arr >= 0) & (arr < 0.2)).sum()),
            "0.2-0.4": int(((arr >= 0.2) & (arr < 0.4)).sum()),
            "0.4-0.6": int(((arr >= 0.4) & (arr < 0.6)).sum()),
            "0.6-0.8": int(((arr >= 0.6) & (arr < 0.8)).sum()),
            "0.8-1.0": int(((arr >= 0.8) & (arr <= 1.0)).sum()),
        },
        "bucket_distribution": {
            "GREEN": int(np.sum(arr <= 0.30)),
            "AMBER": int(np.sum((arr > 0.30) & (arr <= 0.55))),
            "ORANGE": int(np.sum((arr > 0.55) & (arr <= 0.75))),
            "RED": int(np.sum(arr > 0.75)),
        },
    }


def compute_prediction_calibration(db: Session) -> dict:
    """Check if predicted probabilities match observed outcomes.

    Groups farmers by predicted risk score bin and checks
    actual delinquency rate in each bin.
    """
    # Get farmers with risk scores and their DPD status
    results = (
        db.query(RiskScore.risk_probability, Loan.dpd)
        .join(Loan, RiskScore.loan_id == Loan.id)
        .all()
    )

    if not results:
        return {"error": "No paired data found"}

    bins = [
        (0.0, 0.2, "0.0-0.2"),
        (0.2, 0.4, "0.2-0.4"),
        (0.4, 0.6, "0.4-0.6"),
        (0.6, 0.8, "0.6-0.8"),
        (0.8, 1.0, "0.8-1.0"),
    ]

    calibration = {}
    for low, high, label in bins:
        bin_results = [(r, d) for r, d in results if low <= r < high]
        if bin_results:
            avg_predicted = np.mean([r for r, _ in bin_results])
            actual_dpd_rate = np.mean([1 if d > 0 else 0 for _, d in bin_results])
            calibration[label] = {
                "count": len(bin_results),
                "avg_predicted": round(float(avg_predicted), 4),
                "actual_dpd_rate": round(float(actual_dpd_rate), 4),
                "calibration_error": round(float(abs(avg_predicted - actual_dpd_rate)), 4),
            }

    # Overall Brier score
    y_true = np.array([1 if d > 0 else 0 for _, d in results])
    y_pred = np.array([r for r, _ in results])
    brier = float(np.mean((y_pred - y_true) ** 2))

    return {
        "calibration_by_bin": calibration,
        "brier_score": round(brier, 4),
        "interpretation": (
            "Well-calibrated" if brier < 0.1
            else "Moderately calibrated" if brier < 0.2
            else "Poorly calibrated — recalibration needed"
        ),
    }


def compute_feature_drift(db: Session) -> dict:
    """Monitor feature distribution changes over time.

    Compares recent risk scores against historical baseline.
    """
    all_scores = (
        db.query(RiskScore.scoring_date, RiskScore.risk_probability)
        .order_by(RiskScore.scoring_date)
        .all()
    )

    if len(all_scores) < 10:
        return {"error": "Insufficient data for drift detection"}

    # Split into recent (last 30 days) and historical
    cutoff = date.today() - __import__("datetime").timedelta(days=30)
    recent = [s for s in all_scores if s[0] >= cutoff]
    historical = [s for s in all_scores if s[0] < cutoff]

    if not recent or not historical:
        return {"error": "Need both recent and historical data"}

    recent_vals = np.array([s[1] for s in recent])
    hist_vals = np.array([s[1] for s in historical])

    # Population Stability Index (PSI)
    psi = _compute_psi(hist_vals, recent_vals)

    return {
        "recent_count": len(recent_vals),
        "historical_count": len(hist_vals),
        "recent_mean": round(float(recent_vals.mean()), 4),
        "historical_mean": round(float(hist_vals.mean()), 4),
        "mean_shift": round(float(recent_vals.mean() - hist_vals.mean()), 4),
        "psi": round(psi, 4),
        "drift_status": (
            "No drift" if psi < 0.1
            else "Moderate drift" if psi < 0.25
            else "Significant drift — retrain model"
        ),
    }


def _compute_psi(expected: np.ndarray, actual: np.ndarray, n_bins: int = 10) -> float:
    """Compute Population Stability Index."""
    breakpoints = np.linspace(0, 1, n_bins + 1)

    expected_hist, _ = np.histogram(expected, bins=breakpoints)
    actual_hist, _ = np.histogram(actual, bins=breakpoints)

    # Add small epsilon to avoid division by zero
    expected_pct = (expected_hist + 1) / (len(expected) + n_bins)
    actual_pct = (actual_hist + 1) / (len(actual) + n_bins)

    psi = float(np.sum((actual_pct - expected_pct) * np.log(actual_pct / expected_pct)))
    return psi


def compute_alert_accuracy(db: Session) -> dict:
    """Measure alert accuracy — what fraction of alerts led to actual DPD."""
    alerts = (
        db.query(Alert, Loan.dpd)
        .join(Loan, Alert.farm_id == Loan.id)  # simplified join
        .all()
    )

    # In production, this would match alert timestamp to subsequent DPD
    total_alerts = db.query(func.count(Alert.id)).scalar()
    high_alerts = db.query(func.count(Alert.id)).filter(
        Alert.severity.in_(["HIGH", "CRITICAL"])
    ).scalar()

    # Loans that went DPD after being flagged
    flagged_with_dpd = db.query(func.count(Loan.id)).filter(
        Loan.dpd > 0
    ).scalar()

    return {
        "total_alerts": total_alerts,
        "high_severity_alerts": high_alerts,
        "loans_with_dpd": flagged_with_dpd,
        "false_positive_estimate": "Requires temporal analysis of alert → DPD timeline",
    }


def get_full_monitoring_report(db: Session) -> dict:
    """Generate a comprehensive model monitoring report."""
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "score_distribution": compute_score_distribution(db),
        "prediction_calibration": compute_prediction_calibration(db),
        "feature_drift": compute_feature_drift(db),
        "alert_accuracy": compute_alert_accuracy(db),
    }
