from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.farmer import FarmerCreate, FarmerResponse
from app.services import farmer_service

router = APIRouter()


@router.get("/farmers", response_model=List[FarmerResponse])
def list_farmers(
    province: Optional[str] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    return farmer_service.list_farmers(db, province=province, search=search, skip=skip, limit=limit)


@router.get("/farmers/{farmer_id}", response_model=FarmerResponse)
def get_farmer(farmer_id: int, db: Session = Depends(get_db)):
    farmer = farmer_service.get_farmer(db, farmer_id)
    if not farmer:
        raise HTTPException(404, "Farmer not found")
    return farmer


@router.post("/farmers", response_model=FarmerResponse, status_code=201)
def create_farmer(data: FarmerCreate, db: Session = Depends(get_db)):
    return farmer_service.create_farmer(db, data.model_dump())
