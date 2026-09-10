from datetime import date, timedelta
from typing import Optional
from sqlalchemy.orm import Session

from app.models import CropHealth


def get_crop_health_history(
    db: Session,
    farm_id: int,
    days: int = 90,
) -> list[CropHealth]:
    cutoff = date.today() - timedelta(days=days)
    return (
        db.query(CropHealth)
        .filter(CropHealth.farm_id == farm_id, CropHealth.observation_date >= cutoff)
        .order_by(CropHealth.observation_date)
        .all()
    )


def get_latest_crop_health(db: Session, farm_id: int) -> Optional[CropHealth]:
    return (
        db.query(CropHealth)
        .filter(CropHealth.farm_id == farm_id)
        .order_by(CropHealth.observation_date.desc())
        .first()
    )
