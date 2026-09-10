from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.crop_health import CropHealthResponse
from app.services import crop_health_service

router = APIRouter()


@router.get("/crop-health/{farm_id}", response_model=list[CropHealthResponse])
def get_crop_health(
    farm_id: int,
    days: int = Query(90, description="Number of days of history"),
    db: Session = Depends(get_db),
):
    return crop_health_service.get_crop_health_history(db, farm_id, days=days)


@router.get("/crop-health/{farm_id}/latest", response_model=CropHealthResponse)
def get_latest_crop_health(farm_id: int, db: Session = Depends(get_db)):
    latest = crop_health_service.get_latest_crop_health(db, farm_id)
    if not latest:
        raise HTTPException(404, "No crop health data for this farm")
    return latest
