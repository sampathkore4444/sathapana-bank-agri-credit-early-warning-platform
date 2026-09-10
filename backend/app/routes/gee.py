"""GEE Data Ingestion API routes.

Endpoints to trigger, monitor, and query satellite data ingestion.
"""
from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.services import gee_ingestion

router = APIRouter()


@router.post("/gee/ingest")
def trigger_ingestion(db: Session = Depends(get_db)):
    """Run satellite ingestion for ALL pilot farms.

    Fetches real Sentinel-2/1 data from GEE (if configured)
    or simulated data (fallback). Creates CropHealth records.
    """
    return gee_ingestion.run_full_ingestion(db)


@router.post("/gee/ingest/{farm_id}")
def ingest_single_farm(farm_id: int, db: Session = Depends(get_db)):
    """Ingest satellite data for a single farm."""
    from app.models import Farm
    farm = db.query(Farm).filter(Farm.id == farm_id).first()
    if not farm:
        from fastapi import HTTPException
        raise HTTPException(404, "Farm not found")

    result = gee_ingestion.ingest_farm(db, farm)
    db.commit()
    return result or {"error": "Ingestion failed"}


@router.get("/gee/status")
def ingestion_status(db: Session = Depends(get_db)):
    """Check ingestion status — GEE config, observation counts, latest date."""
    return gee_ingestion.get_ingestion_status(db)


@router.get("/gee/test-connection")
def test_gee_connection():
    """Test if GEE is configured and accessible."""
    ee = gee_ingestion._get_ee()
    if not ee:
        return {
            "connected": False,
            "reason": "GEE_PROJECT_ID not set" if not gee_ingestion.GEE_PROJECT_ID else "GEE init failed",
            "project": gee_ingestion.GEE_PROJECT_ID or "not set",
            "setup_url": "https://earthengine.google.com/",
        }

    try:
        # Quick test query
        test = ee.Number(1).getInfo()
        return {
            "connected": True,
            "project": gee_ingestion.GEE_PROJECT_ID,
            "test_result": test,
        }
    except Exception as e:
        return {
            "connected": False,
            "reason": str(e),
            "project": gee_ingestion.GEE_PROJECT_ID,
        }


@router.get("/gee/fetch-farm/{farm_id}")
def fetch_farm_satellite_data(farm_id: int, days: int = Query(15), db: Session = Depends(get_db)):
    """Fetch satellite data for a farm WITHOUT saving to DB.

    Useful for previewing what data GEE would return.
    """
    from app.models import Farm
    from fastapi import HTTPException

    farm = db.query(Farm).filter(Farm.id == farm_id).first()
    if not farm:
        raise HTTPException(404, "Farm not found")

    end = date.today()
    start = end - __import__("datetime").timedelta(days=days)

    s2 = gee_ingestion.fetch_sentinel2_for_farm(
        farm.centroid_lat, farm.centroid_lon, start, end,
    )
    s1 = gee_ingestion.fetch_sentinel1_for_farm(
        farm.centroid_lat, farm.centroid_lon, start, end,
    )

    return {
        "farm_id": farm.farm_code,
        "lat": farm.centroid_lat,
        "lon": farm.centroid_lon,
        "date_range": f"{start} to {end}",
        "sentinel2": s2,
        "sentinel1": s1,
    }


@router.get("/gee/cambodia-coverage")
def cambodia_coverage_check():
    """Check Sentinel-2 image count over Cambodia for the last 30 days."""
    ee = gee_ingestion._get_ee()
    if not ee:
        return {
            "gee_available": False,
            "reason": "GEE not configured",
            "setup_steps": [
                "1. Sign up at https://earthengine.google.com/",
                "2. Create project at https://console.cloud.google.com/",
                "3. Enable Earth Engine API",
                "4. Run: earthengine authenticate",
                "5. Set GEE_PROJECT_ID env var",
            ],
        }

    try:
        from datetime import timedelta
        cambodia = ee.Geometry.Rectangle([102, 10, 108, 15])
        end = date.today()
        start = end - timedelta(days=30)

        s2_count = (
            ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
            .filterBounds(cambodia)
            .filterDate(start.isoformat(), end.isoformat())
            .size()
            .getInfo()
        )

        s1_count = (
            ee.ImageCollection("COPERNICUS/S1_GRD")
            .filterBounds(cambodia)
            .filterDate(start.isoformat(), end.isoformat())
            .size()
            .getInfo()
        )

        return {
            "gee_available": True,
            "project": gee_ingestion.GEE_PROJECT_ID,
            "cambodia_bbox": [102, 10, 108, 15],
            "date_range": f"{start} to {end}",
            "sentinel2_images": s2_count,
            "sentinel1_images": s1_count,
            "status": "Connected to real GEE data" if s2_count > 0 else "Connected but no images found",
        }

    except Exception as e:
        return {"gee_available": False, "error": str(e)}

