from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.farm import FarmResponse
from app.services import farm_service

router = APIRouter()


@router.get("/farms", response_model=List[FarmResponse])
def list_farms(
    province: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    return farm_service.list_farms(db, province=province, skip=skip, limit=limit)


@router.get("/farms/{farm_id}", response_model=FarmResponse)
def get_farm(farm_id: int, db: Session = Depends(get_db)):
    farm = farm_service.get_farm(db, farm_id)
    if not farm:
        raise HTTPException(404, "Farm not found")
    return farm


@router.get("/farms/{farm_id}/geojson")
def get_farm_geojson(farm_id: int, db: Session = Depends(get_db)):
    """Return the farm boundary as a GeoJSON Feature."""
    result = farm_service.get_farm_geojson(db, farm_id)
    if not result:
        raise HTTPException(404, "Farm not found")
    return result


@router.get("/farms/geojson/all")
def get_all_farms_geojson(province: Optional[str] = None, db: Session = Depends(get_db)):
    """Return all farms as a GeoJSON FeatureCollection for map rendering."""
    return farm_service.get_all_farms_geojson(db, province=province)
