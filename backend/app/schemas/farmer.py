from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class FarmerBase(BaseModel):
    farmer_code: str
    name: str
    phone: Optional[str] = None
    province: str
    district: str
    commune: Optional[str] = None
    village: Optional[str] = None


class FarmerCreate(FarmerBase):
    pass


class FarmerResponse(FarmerBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
