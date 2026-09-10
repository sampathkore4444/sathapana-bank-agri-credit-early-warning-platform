from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class AlertBase(BaseModel):
    farm_id: int
    alert_type: str
    severity: str
    title: str
    description: str
    risk_score_value: Optional[float] = None


class AlertCreate(AlertBase):
    pass


class AlertResponse(AlertBase):
    id: int
    alert_code: str
    risk_score_id: Optional[int] = None
    status: str
    assigned_to: Optional[str] = None
    action_taken: Optional[str] = None
    created_at: datetime
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None

    class Config:
        from_attributes = True
