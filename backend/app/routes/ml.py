"""ML pipeline API routes — model training, scoring, and explainability."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.services import ml_pipeline, feature_engine, growth_curve

router = APIRouter()


@router.post("/ml/train")
def train_model(db: Session = Depends(get_db)):
    """Train the credit risk model on current data."""
    return ml_pipeline.train_model(db)


@router.post("/ml/score-all")
def score_all_farmers(db: Session = Depends(get_db)):
    """Score all farmers using the trained model."""
    return ml_pipeline.score_all_farmers(db)


@router.get("/ml/score/{farmer_id}")
def score_farmer(farmer_id: int, db: Session = Depends(get_db)):
    """Score a single farmer and get SHAP explanation."""
    result = ml_pipeline.score_farmer(db, farmer_id)
    if not result:
        return {"error": "Model not trained or farmer not found"}
    return result


@router.get("/ml/metrics")
def get_model_metrics():
    """Get stored model training metrics."""
    metrics = ml_pipeline.get_model_metrics()
    return metrics or {"error": "No model trained yet"}


@router.get("/ml/features/{farmer_id}")
def get_farmer_features(farmer_id: int, db: Session = Depends(get_db)):
    """Get computed feature vector for a farmer."""
    features = feature_engine.compute_all_features(db, farmer_id)
    return features or {"error": "Could not compute features"}


@router.get("/ml/growth-curve/{farm_id}")
def get_growth_curve_analysis(farm_id: int, db: Session = Depends(get_db)):
    """Get growth curve deviation analysis for a farm."""
    return growth_curve.detect_growth_deviation(db, farm_id)


@router.get("/ml/growth-curve/{province}/expected")
def get_expected_ndvi(province: str, days_since_planting: int):
    """Get expected NDVI for a province and crop age."""
    return growth_curve.get_expected_ndvi(province, days_since_planting)
