from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel


class LoanBase(BaseModel):
    loan_code: str
    farmer_id: int
    outstanding_principal: float
    monthly_installment: float
    disbursement_date: Optional[date] = None
    maturity_date: Optional[date] = None
    interest_rate: Optional[float] = None
    dpd: int = 0
    dpd_max_90d: int = 0
    missed_payments_count: int = 0
    restructured: bool = False
    status: str = "active"


class LoanCreate(LoanBase):
    pass


class LoanResponse(LoanBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
