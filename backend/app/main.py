"""Sathapana Agricultural Risk Platform (SARP) — Backend API."""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine, Base, SessionLocal
from app.routes import api_router
from app.services.scheduler import start_scheduler, stop_scheduler
from app.services.auth_service import seed_default_users

logger = logging.getLogger("sarp")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup/shutdown lifecycle."""
    # Startup
    logger.info("Starting SARP backend...")
    Base.metadata.create_all(bind=engine)

    # Seed default users
    db = SessionLocal()
    try:
        seed_default_users(db)
    finally:
        db.close()

    # Start background scheduler
    start_scheduler()
    logger.info("SARP backend started")

    yield

    # Shutdown
    stop_scheduler()
    logger.info("SARP backend stopped")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.DESCRIPTION,
    version=settings.VERSION,
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount all API routes
app.include_router(api_router)


@app.get("/")
def root():
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health")
def health():
    return {"status": "ok"}
