"""Background scheduler for periodic data ingestion and model scoring.

Runs:
- Every 6 hours: ingest latest satellite data for all farms
- Daily: fetch weather data and update features
- Daily: re-score all farmers with the risk model
- Weekly: re-train the ML model with accumulated data
"""
import logging
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from app.database import SessionLocal
from app.models import Farm, Farmer, CropHealth
from app.services import satellite, weather, ml_pipeline, feature_engine
from app.services.notification_service import send_alert_notifications
from app.services import gee_ingestion

logger = logging.getLogger("sarp.scheduler")

scheduler = BackgroundScheduler()


def job_ingest_satellite():
    """Fetch real Sentinel-2/1 data from GEE for all farms."""
    logger.info("GEE satellite ingestion job started")
    db = SessionLocal()
    try:
        result = gee_ingestion.run_full_ingestion(db)
        logger.info(f"GEE ingestion complete: {result}")
    except Exception as e:
        logger.error(f"GEE ingestion failed: {e}")
    finally:
        db.close()


def job_ingest_weather():
    """Fetch latest weather data for all farms."""
    logger.info("Weather ingestion job started")
    db = SessionLocal()
    try:
        farms = db.query(Farm).all()
        updated = 0
        for farm in farms:
            try:
                rainfall = weather.get_rainfall_30d(
                    farm.centroid_lat, farm.centroid_lon,
                    datetime.now().date(),
                )
                temp = weather.get_temperature_summary(
                    farm.centroid_lat, farm.centroid_lon,
                    datetime.now().date(),
                )
                # Update latest crop health record with weather data
                latest = (
                    db.query(CropHealth)
                    .filter(CropHealth.farm_id == farm.id)
                    .order_by(CropHealth.observation_date.desc())
                    .first()
                )
                if latest:
                    latest.rainfall_30d = rainfall.get("rainfall_30d_mm", 0)
                    latest.rainfall_deviation_30d = rainfall.get("deviation_pct", 0)
                    latest.temperature_stress_days = temp.get("stress_days", 0)
                    updated += 1
            except Exception as e:
                logger.warning(f"Failed to ingest weather for farm {farm.id}: {e}")

        db.commit()
        logger.info(f"Weather ingestion complete: {updated}/{len(farms)} farms updated")
    finally:
        db.close()


def job_score_all_farmers():
    """Re-score all farmers with the latest model."""
    logger.info("Risk scoring job started")
    db = SessionLocal()
    try:
        result = ml_pipeline.score_all_farmers(db)
        logger.info(f"Risk scoring complete: {result}")
    finally:
        db.close()


def job_retrain_model():
    """Re-train the ML model with accumulated data."""
    logger.info("Model re-training job started")
    db = SessionLocal()
    try:
        metrics = ml_pipeline.train_model(db)
        logger.info(f"Model re-training complete: {metrics}")
    finally:
        db.close()


def job_send_notifications():
    """Check for new alerts and send email notifications to assigned RMs."""
    logger.info("Notification job started")
    db = SessionLocal()
    try:
        send_alert_notifications(db)
        logger.info("Notification job complete")
    finally:
        db.close()


def start_scheduler():
    """Initialize and start all scheduled jobs."""
    # Satellite ingestion: every 6 hours
    scheduler.add_job(
        job_ingest_satellite,
        trigger=IntervalTrigger(hours=6),
        id="satellite_ingestion",
        name="Satellite Data Ingestion",
        replace_existing=True,
    )

    # Weather ingestion: daily at 06:00 UTC (13:00 Cambodia)
    scheduler.add_job(
        job_ingest_weather,
        trigger=CronTrigger(hour=6, minute=0),
        id="weather_ingestion",
        name="Weather Data Ingestion",
        replace_existing=True,
    )

    # Risk scoring: daily at 07:00 UTC (14:00 Cambodia)
    scheduler.add_job(
        job_score_all_farmers,
        trigger=CronTrigger(hour=7, minute=0),
        id="risk_scoring",
        name="Risk Score Computation",
        replace_existing=True,
    )

    # Model re-training: weekly on Sunday at 02:00 UTC
    scheduler.add_job(
        job_retrain_model,
        trigger=CronTrigger(day_of_week="sun", hour=2, minute=0),
        id="model_retraining",
        name="Weekly Model Re-training",
        replace_existing=True,
    )

    # Notifications: daily at 08:00 UTC (15:00 Cambodia)
    scheduler.add_job(
        job_send_notifications,
        trigger=CronTrigger(hour=8, minute=0),
        id="notifications",
        name="RM Alert Notifications",
        replace_existing=True,
    )

    scheduler.start()
    logger.info("Scheduler started with 5 jobs")
    return scheduler


def stop_scheduler():
    """Shutdown the scheduler gracefully."""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Scheduler stopped")


def get_jobs_status() -> list[dict]:
    """Get status of all scheduled jobs."""
    jobs = []
    for job in scheduler.get_jobs():
        jobs.append({
            "id": job.id,
            "name": job.name,
            "next_run": str(job.next_run_time) if job.next_run_time else None,
            "trigger": str(job.trigger),
        })
    return jobs


def run_job_now(job_id: str) -> dict:
    """Manually trigger a job by ID."""
    job = scheduler.get_job(job_id)
    if not job:
        return {"error": f"Job {job_id} not found"}
    job.modify(next_run_time=datetime.now())
    return {"status": f"Job {job_id} scheduled for immediate execution"}
