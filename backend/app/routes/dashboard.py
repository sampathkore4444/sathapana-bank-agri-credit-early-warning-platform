from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.dashboard import PortfolioSummary
from app.services import dashboard_service

router = APIRouter()


@router.get("/dashboard/summary", response_model=PortfolioSummary)
def portfolio_summary(db: Session = Depends(get_db)):
    return dashboard_service.portfolio_summary(db)


@router.get("/dashboard/early-warnings")
def early_warnings(limit: int = 20, db: Session = Depends(get_db)):
    return dashboard_service.early_warnings(db, limit=limit)


@router.get("/dashboard/stats")
def dashboard_stats(db: Session = Depends(get_db)):
    return dashboard_service.dashboard_stats(db)
