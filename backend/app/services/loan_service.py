from typing import Optional
from sqlalchemy.orm import Session

from app.models import Loan


def list_loans(
    db: Session,
    farmer_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
) -> list[Loan]:
    q = db.query(Loan)
    if farmer_id:
        q = q.filter(Loan.farmer_id == farmer_id)
    return q.offset(skip).limit(limit).all()


def get_loan(db: Session, loan_id: int) -> Optional[Loan]:
    return db.query(Loan).filter(Loan.id == loan_id).first()
