from sqlalchemy import Column, Integer, Float, Date, Boolean

from app.database import Base


class FinancialSnapshot(Base):
    """Periodic financial features per farmer for model input."""
    __tablename__ = "financial_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    farmer_id = Column(Integer, index=True)
    snapshot_date = Column(Date)
    deposit_balance_avg_30d = Column(Float)
    deposit_balance_avg_60d = Column(Float)
    deposit_balance_trend_30d = Column(Float)  # % change
    deposit_balance_trend_60d = Column(Float)
    transaction_count_30d = Column(Integer)
    cash_inflow_30d = Column(Float)
    cash_outflow_30d = Column(Float)
    cash_inflow_30d_60d_ratio = Column(Float)
    cash_outflow_30d_60d_ratio = Column(Float)
    days_since_last_deposit = Column(Integer)
    balance_to_installment_ratio = Column(Float)
    agricultural_income_detected = Column(Boolean, default=False)
