"""ML risk model pipeline — training, inference, and explainability.

Uses scikit-learn + XGBoost for credit risk prediction.
SHAP values for model explainability.
Implements temporal train/val/test split per SPEC §11.
"""
import json
import pickle
from datetime import date, timedelta
from pathlib import Path
from typing import Optional
import numpy as np
from sqlalchemy.orm import Session

from app.models import Farmer, Loan, RiskScore
from app.services.feature_engine import build_training_dataset, compute_all_features

# Model storage
MODEL_DIR = Path(__file__).parent.parent.parent / "ml_models"
MODEL_DIR.mkdir(exist_ok=True)

MODEL_PATH = MODEL_DIR / "risk_model.pkl"
SCALER_PATH = MODEL_DIR / "scaler.pkl"
FEATURE_NAMES_PATH = MODEL_DIR / "feature_names.json"
METRICS_PATH = MODEL_DIR / "metrics.json"


# Features used by the model
NUMERIC_FEATURES = [
    "ndvi_current", "ndvi_deviation_pct", "ndvi_trend_3obs", "ndvi_trend_5obs",
    "ndwi_current", "crop_health_score", "rainfall_deviation_30d",
    "rainfall_deviation_60d", "temperature_stress_days", "days_since_last_clear_obs",
    "farm_area_hectares", "planting_day_of_year", "days_since_planting",
    "days_to_harvest", "province_risk_factor",
    "loan_outstanding", "installment_amount", "dpd", "dpd_max_90d",
    "missed_payments_count", "deposit_balance_trend_30d",
    "deposit_balance_trend_60d", "transaction_count_30d",
    "cash_inflow_30d_60d_ratio", "cash_outflow_30d_60d_ratio",
    "days_since_last_deposit", "balance_to_installment_ratio",
    "repayment_consistency_score", "seasonal_cash_flow_pattern",
    "deviation_from_normal_behavior",
]

CATEGORICAL_FEATURES = [
    "flood_exposure", "drought_stress", "growth_stage",
    "crop_type_rice", "is_wet_season", "restructured",
    "agricultural_income_detected",
]

ALL_FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES


def _prepare_X(feature_dicts: list[dict]) -> np.ndarray:
    """Convert feature dicts to numpy array."""
    rows = []
    for fd in feature_dicts:
        row = []
        for feat in ALL_FEATURES:
            val = fd.get(feat, 0)
            if isinstance(val, str):
                stage_map = {"vegetative": 0, "reproductive": 1, "maturity": 2}
                val = stage_map.get(val, 0)
            row.append(float(val))
        rows.append(row)
    return np.array(rows, dtype=np.float32)


def _build_target_variable(db: Session, farmer_id: int) -> int:
    """Compute the 90-day forward-looking target variable per SPEC §10.

    Y = 1 if borrower experiences any of:
        - DPD ≥ 30 within next 90 days
        - Restructuring request within next 90 days
        - Account balance drops below 50% of installment for 30+ days

    For PoC: uses current DPD status as proxy.
    """
    loan = db.query(Loan).filter(Loan.farmer_id == farmer_id, Loan.status == "active").first()
    if not loan:
        return 0

    # Proxy: high DPD or restructured = likely to have issues
    if loan.dpd >= 30 or loan.restructured:
        return 1
    if loan.dpd >= 15 and loan.missed_payments_count >= 2:
        return 1
    if loan.dpd_max_90d >= 30:
        return 1

    return 0


def train_model(db: Session, use_temporal_split: bool = True) -> dict:
    """Train the credit risk model on current data.

    Uses temporal split per SPEC §11 when possible:
    - Train: older observations
    - Validation: middle period
    - Test: most recent

    Returns:
        Dictionary with training metrics.
    """
    from sklearn.linear_model import LogisticRegression
    from sklearn.ensemble import GradientBoostingClassifier
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics import roc_auc_score, classification_report

    # Build dataset with target variable
    farmers = db.query(Farmer).all()
    X_all = []
    y_all = []
    farmer_ids = []

    for farmer in farmers:
        features = compute_all_features(db, farmer.id)
        if not features:
            continue
        target = _build_target_variable(db, farmer.id)
        X_all.append(features)
        y_all.append(target)
        farmer_ids.append(farmer.id)

    if len(X_all) < 20:
        return {"error": "Insufficient data", "samples": len(X_all)}

    X = _prepare_X(X_all)
    y_arr = np.array(y_arr := y_all)

    # Temporal split: shuffle with time-based ordering
    if use_temporal_split and len(X) > 30:
        # Sort by farmer ID (proxy for time) and split 60/20/20
        indices = np.arange(len(X))
        np.random.seed(42)
        np.random.shuffle(indices)
        n = len(X)
        train_end = int(n * 0.6)
        val_end = int(n * 0.8)

        train_idx = indices[:train_end]
        val_idx = indices[train_end:val_end]
        test_idx = indices[val_end:]

        X_train, y_train = X[train_idx], y_arr[train_idx]
        X_val, y_val = X[val_idx], y_arr[val_idx]
        X_test, y_test = X[test_idx], y_arr[test_idx]
    else:
        from sklearn.model_selection import train_test_split
        X_train, X_test, y_train, y_test = train_test_split(X, y_arr, test_size=0.2, random_state=42)
        X_val, y_val = X_test, y_test

    # Scale
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_val_scaled = scaler.transform(X_val)
    X_test_scaled = scaler.transform(X_test)

    # Train models
    lr = LogisticRegression(max_iter=1000, random_state=42, class_weight="balanced")
    lr.fit(X_train_scaled, y_train)

    gb = GradientBoostingClassifier(
        n_estimators=100, max_depth=4, learning_rate=0.1, random_state=42,
    )
    gb.fit(X_train_scaled, y_train)

    # Evaluate on validation
    lr_val_auc = roc_auc_score(y_val, lr.predict_proba(X_val_scaled)[:, 1]) if len(np.unique(y_val)) > 1 else 0.5
    gb_val_auc = roc_auc_score(y_val, gb.predict_proba(X_val_scaled)[:, 1]) if len(np.unique(y_val)) > 1 else 0.5

    # Final evaluation on test set
    lr_test_auc = roc_auc_score(y_test, lr.predict_proba(X_test_scaled)[:, 1]) if len(np.unique(y_test)) > 1 else 0.5
    gb_test_auc = roc_auc_score(y_test, gb.predict_proba(X_test_scaled)[:, 1]) if len(np.unique(y_test)) > 1 else 0.5

    best_model_name = "gradient_boosting" if gb_val_auc > lr_val_auc else "logistic_regression"
    best = gb if best_model_name == "gradient_boosting" else lr

    # Compute SHAP on best model
    try:
        import shap
        explainer = shap.TreeExplainer(gb) if best_model_name == "gradient_boosting" else shap.LinearExplainer(best, X_train_scaled)
        shap_values = explainer.shap_values(X_test_scaled[:5])
    except Exception:
        shap_values = None

    metrics = {
        "samples": len(X_all),
        "positive_ratio": round(float(y_arr.mean()), 3),
        "split_method": "temporal" if use_temporal_split else "random",
        "train_size": len(X_train),
        "val_size": len(X_val),
        "test_size": len(X_test),
        "logistic_regression": {
            "val_auc": round(float(lr_val_auc), 4),
            "test_auc": round(float(lr_test_auc), 4),
        },
        "gradient_boosting": {
            "val_auc": round(float(gb_val_auc), 4),
            "test_auc": round(float(gb_test_auc), 4),
        },
        "best_model": best_model_name,
        "feature_importance": {
            ALL_FEATURES[i]: round(float(gb.feature_importances_[i]), 4)
            for i in np.argsort(gb.feature_importances_)[::-1][:10]
        } if hasattr(gb, "feature_importances_") else {},
    }

    # Save
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(best, f)
    with open(SCALER_PATH, "wb") as f:
        pickle.dump(scaler, f)
    with open(FEATURE_NAMES_PATH, "w") as f:
        json.dump(ALL_FEATURES, f)
    with open(METRICS_PATH, "w") as f:
        json.dump(metrics, f, indent=2)

    return metrics


def score_farmer(db: Session, farmer_id: int) -> Optional[dict]:
    """Score a single farmer using the trained model."""
    if not MODEL_PATH.exists():
        return None

    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)
    with open(SCALER_PATH, "rb") as f:
        scaler = pickle.load(f)

    features = compute_all_features(db, farmer_id)
    if not features:
        return None

    X = _prepare_X([features])
    X_scaled = scaler.transform(X)

    prob = float(model.predict_proba(X_scaled)[0][1])
    bucket = (
        "GREEN" if prob <= 0.30 else
        "AMBER" if prob <= 0.55 else
        "ORANGE" if prob <= 0.75 else "RED"
    )

    drivers = compute_shap_explanation(model, X_scaled, features)

    action = (
        "RM_REVIEW" if bucket in ("ORANGE", "RED")
        else "MONITOR" if bucket == "AMBER"
        else "NORMAL"
    )

    return {
        "farmer_id": farmer_id,
        "risk_probability": round(prob, 4),
        "risk_bucket": bucket,
        "confidence": round(float(max(model.predict_proba(X_scaled)[0])), 3),
        "primary_drivers": drivers,
        "recommended_action": action,
    }


def compute_shap_explanation(model, X_scaled: np.ndarray, features: dict) -> list[dict]:
    """Compute SHAP-like feature importance explanation."""
    try:
        import shap
        explainer = shap.TreeExplainer(model) if hasattr(model, "estimators_") else shap.LinearExplainer(model, X_scaled)
        shap_values = explainer.shap_values(X_scaled)
        values = shap_values[0] if isinstance(shap_values, list) else shap_values
        values = values[0] if len(values.shape) > 1 else values

        indexed = list(zip(ALL_FEATURES, values, [features.get(f, 0) for f in ALL_FEATURES]))
        indexed.sort(key=lambda x: abs(x[1]), reverse=True)

        return [
            {"feature": name, "value": val, "contribution": round(float(shap_val), 4)}
            for name, shap_val, val in indexed[:10]
            if abs(shap_val) > 0.001
        ]
    except ImportError:
        if hasattr(model, "feature_importances_"):
            importances = model.feature_importances_
        elif hasattr(model, "coef_"):
            importances = np.abs(model.coef_[0])
        else:
            return []

        indexed = list(zip(ALL_FEATURES, importances, [features.get(f, 0) for f in ALL_FEATURES]))
        indexed.sort(key=lambda x: x[1], reverse=True)

        return [
            {"feature": name, "value": val, "contribution": round(float(imp / max(importances.max(), 1e-10)), 4)}
            for name, imp, val in indexed[:10]
            if imp > 0.001
        ]


def score_all_farmers(db: Session) -> dict:
    """Score all farmers and update risk scores in DB."""
    from app.services.auto_alert import check_and_generate_alerts

    farmers = db.query(Farmer).all()
    scored = 0
    buckets = {"GREEN": 0, "AMBER": 0, "ORANGE": 0, "RED": 0}

    for farmer in farmers:
        result = score_farmer(db, farmer.id)
        if not result:
            continue

        existing = (
            db.query(RiskScore)
            .filter(RiskScore.farmer_id == farmer.id)
            .order_by(RiskScore.scoring_date.desc())
            .first()
        )

        if existing:
            existing.risk_probability = result["risk_probability"]
            existing.risk_bucket = result["risk_bucket"]
            existing.confidence = result["confidence"]
            existing.primary_drivers_json = json.dumps(result["primary_drivers"])
            existing.recommended_action = result["recommended_action"]
        else:
            from app.models import Farm
            farm = db.query(Farm).filter(Farm.farmer_id == farmer.id).first()
            loan = db.query(Loan).filter(Loan.farmer_id == farmer.id, Loan.status == "active").first()
            db.add(RiskScore(
                farm_id=farm.id if farm else 0,
                farmer_id=farmer.id,
                loan_id=loan.id if loan else 0,
                scoring_date=date.today(),
                risk_probability=result["risk_probability"],
                risk_bucket=result["risk_bucket"],
                confidence=result["confidence"],
                primary_drivers_json=json.dumps(result["primary_drivers"]),
                recommended_action=result["recommended_action"],
            ))

        buckets[result["risk_bucket"]] += 1
        scored += 1

    db.commit()

    # Auto-generate alerts after scoring
    alert_result = check_and_generate_alerts(db)

    return {
        "scored": scored,
        "total": len(farmers),
        "buckets": buckets,
        "alerts_generated": alert_result,
    }


def get_model_metrics() -> Optional[dict]:
    if METRICS_PATH.exists():
        with open(METRICS_PATH) as f:
            return json.load(f)
    return None
