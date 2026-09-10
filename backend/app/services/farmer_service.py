from typing import Optional
from sqlalchemy.orm import Session

from app.models import Farmer


def list_farmers(
    db: Session,
    province: Optional[str] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
) -> list[Farmer]:
    q = db.query(Farmer)
    if province:
        q = q.filter(Farmer.province == province)
    if search:
        q = q.filter(
            (Farmer.farmer_code.contains(search))
            | (Farmer.name.contains(search))
        )
    return q.offset(skip).limit(limit).all()


def get_farmer(db: Session, farmer_id: int) -> Optional[Farmer]:
    return db.query(Farmer).filter(Farmer.id == farmer_id).first()


def create_farmer(db: Session, data: dict) -> Farmer:
    farmer = Farmer(**data)
    db.add(farmer)
    db.commit()
    db.refresh(farmer)
    return farmer


def get_province_ids(db: Session, province: str) -> list[int]:
    """Get all farmer IDs for a province."""
    return [f.id for f in db.query(Farmer.id).filter(Farmer.province == province).all()]
