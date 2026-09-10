import json
from typing import Optional
from sqlalchemy.orm import Session

from app.models import Farm, Farmer, RiskScore, CropHealth


def list_farms(
    db: Session,
    province: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
) -> list[Farm]:
    q = db.query(Farm).join(Farmer)
    if province:
        q = q.filter(Farmer.province == province)
    return q.offset(skip).limit(limit).all()


def get_farm(db: Session, farm_id: int) -> Optional[Farm]:
    return db.query(Farm).filter(Farm.id == farm_id).first()


def get_farm_geojson(db: Session, farm_id: int) -> Optional[dict]:
    """Return a single farm as a GeoJSON Feature with risk properties."""
    farm = get_farm(db, farm_id)
    if not farm:
        return None

    boundary = json.loads(farm.boundary_geojson) if farm.boundary_geojson else None
    risk = (
        db.query(RiskScore)
        .filter(RiskScore.farm_id == farm_id)
        .order_by(RiskScore.id.desc())
        .first()
    )

    return {
        "type": "Feature",
        "geometry": boundary,
        "properties": {
            "farm_id": farm.farm_code,
            "farmer_code": farm.farmer.farmer_code if farm.farmer else None,
            "area_hectares": farm.area_hectares,
            "crop_type": farm.crop_type,
            "risk_bucket": risk.risk_bucket if risk else "UNKNOWN",
            "risk_probability": risk.risk_probability if risk else None,
        },
    }


def get_all_farms_geojson(
    db: Session,
    province: Optional[str] = None,
) -> dict:
    """Return all farms as a GeoJSON FeatureCollection for map rendering."""
    q = db.query(Farm).join(Farmer)
    if province:
        q = q.filter(Farmer.province == province)
    farms = q.all()

    features = []
    for farm in farms:
        boundary = json.loads(farm.boundary_geojson) if farm.boundary_geojson else None
        risk = (
            db.query(RiskScore)
            .filter(RiskScore.farm_id == farm.id)
            .order_by(RiskScore.id.desc())
            .first()
        )
        ch = (
            db.query(CropHealth)
            .filter(CropHealth.farm_id == farm.id)
            .order_by(CropHealth.observation_date.desc())
            .first()
        )

        features.append({
            "type": "Feature",
            "geometry": boundary,
            "properties": {
                "farm_id": farm.farm_code,
                "farm_db_id": farm.id,
                "farmer_id": farm.farmer_id,
                "farmer_code": farm.farmer.farmer_code if farm.farmer else None,
                "farmer_name": farm.farmer.name if farm.farmer else None,
                "province": farm.farmer.province if farm.farmer else None,
                "area_hectares": farm.area_hectares,
                "crop_type": farm.crop_type,
                "risk_bucket": risk.risk_bucket if risk else "UNKNOWN",
                "risk_probability": risk.risk_probability if risk else 0,
                "crop_health_score": ch.crop_health_score if ch else None,
            },
        })

    return {"type": "FeatureCollection", "features": features}
