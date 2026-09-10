"""Model monitoring, feature store, and crop health score API routes."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.services import model_monitoring, feature_store, crop_health_score

router = APIRouter()


@router.get("/monitoring/report")
def monitoring_report(db: Session = Depends(get_db)):
    """Full model monitoring report (drift, calibration, accuracy)."""
    return model_monitoring.get_full_monitoring_report(db)


@router.get("/monitoring/score-distribution")
def score_distribution(db: Session = Depends(get_db)):
    """Risk score distribution analysis."""
    return model_monitoring.compute_score_distribution(db)


@router.get("/monitoring/calibration")
def prediction_calibration(db: Session = Depends(get_db)):
    """Prediction calibration analysis."""
    return model_monitoring.compute_prediction_calibration(db)


@router.get("/monitoring/drift")
def feature_drift(db: Session = Depends(get_db)):
    """Score drift detection."""
    return model_monitoring.compute_feature_drift(db)


# Feature Store
@router.post("/feature-store/sync")
def sync_feature_store(db: Session = Depends(get_db)):
    """Compute and store features for all farmers."""
    return feature_store.store_all_features(db)


@router.get("/feature-store/summary")
def feature_store_summary():
    """Get feature store status."""
    return feature_store.get_feature_store_summary()


# Crop Health Score
@router.get("/crop-health-score/{farm_id}/compute")
def compute_health_score(farm_id: int, db: Session = Depends(get_db)):
    """Recompute crop health score using the weighted formula."""
    result = crop_health_score.recompute_farm_health(db, farm_id)
    return result or {"error": "No data for this farm"}


@router.get("/crop-health-score/weighted")
def weighted_score_demo(
    ndvi_deviation_pct: float = -20,
    ndvi_trend_slope: float = -0.01,
    ndwi: float = 0.1,
    sar_vh: float = -15,
    rainfall_deviation_pct: float = -30,
    temperature_stress_days: int = 3,
):
    """Demo endpoint: compute weighted crop health score from inputs."""
    return crop_health_score.compute_crop_health_score(
        ndvi_deviation_pct=ndvi_deviation_pct,
        ndvi_trend_slope=ndvi_trend_slope,
        ndwi=ndwi,
        sar_vh_backscatter=sar_vh,
        rainfall_deviation_pct=rainfall_deviation_pct,
        temperature_stress_days=temperature_stress_days,
    )
