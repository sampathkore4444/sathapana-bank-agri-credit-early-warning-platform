from sqlalchemy import Column, Integer, Float, String, Text, DateTime, Boolean

from app.database import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    farmer_id = Column(Integer, index=True)
    account_number = Column(String(30))
    transaction_date = Column(DateTime)
    transaction_type = Column(String(20))  # deposit, withdrawal
    amount = Column(Float)
    balance_after = Column(Float)
    description = Column(Text, nullable=True)
    is_agricultural = Column(Boolean, default=False)
