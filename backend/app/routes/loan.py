from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.loan import LoanResponse
from app.services import loan_service

router = APIRouter()


@router.get("/loans", response_model=List[LoanResponse])
def list_loans(
    farmer_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    return loan_service.list_loans(db, farmer_id=farmer_id, skip=skip, limit=limit)


@router.get("/loans/{loan_id}", response_model=LoanResponse)
def get_loan(loan_id: int, db: Session = Depends(get_db)):
    loan = loan_service.get_loan(db, loan_id)
    if not loan:
        raise HTTPException(404, "Loan not found")
    return loan
