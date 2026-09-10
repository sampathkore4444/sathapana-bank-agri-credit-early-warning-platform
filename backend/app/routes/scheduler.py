"""Scheduler API routes — view jobs, trigger manually."""
from fastapi import APIRouter

from app.services.scheduler import get_jobs_status, run_job_now

router = APIRouter()


@router.get("/scheduler/jobs")
def list_jobs():
    """List all scheduled jobs and their next run times."""
    return get_jobs_status()


@router.post("/scheduler/run/{job_id}")
def trigger_job(job_id: str):
    """Manually trigger a scheduled job."""
    return run_job_now(job_id)
