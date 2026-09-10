"""API routes."""
from fastapi import APIRouter

from app.routes.farmer import router as farmer_router
from app.routes.farm import router as farm_router
from app.routes.loan import router as loan_router
from app.routes.crop_health import router as crop_health_router
from app.routes.risk_score import router as risk_score_router
from app.routes.alert import router as alert_router
from app.routes.dashboard import router as dashboard_router
from app.routes.ml import router as ml_router
from app.routes.satellite import router as satellite_router
from app.routes.pilot import router as pilot_router
from app.routes.kpi import router as kpi_router
from app.routes.auth import router as auth_router
from app.routes.scheduler import router as scheduler_router
from app.routes.monitoring import router as monitoring_router
from app.routes.ws import router as ws_router

api_router = APIRouter(prefix="/api")

api_router.include_router(auth_router)
api_router.include_router(farmer_router)
api_router.include_router(farm_router)
api_router.include_router(loan_router)
api_router.include_router(crop_health_router)
api_router.include_router(risk_score_router)
api_router.include_router(alert_router)
api_router.include_router(dashboard_router)
api_router.include_router(ml_router)
api_router.include_router(satellite_router)
api_router.include_router(pilot_router)
api_router.include_router(kpi_router)
api_router.include_router(scheduler_router)
api_router.include_router(monitoring_router)
api_router.include_router(ws_router)
