from typing import List
from pydantic import BaseModel


class ProvinceBreakdown(BaseModel):
    province: str
    green: int
    amber: int
    orange: int
    red: int
    total_outstanding: float


class PortfolioSummary(BaseModel):
    total_farmers: int
    total_outstanding: float
    green_count: int
    amber_count: int
    orange_count: int
    red_count: int
    provinces: List[ProvinceBreakdown]
