"""Satellite and weather data API routes."""
from datetime import date
from fastapi import APIRouter, Query

from app.services import satellite, weather

router = APIRouter()


@router.get("/satellite/ndvi")
def get_ndvi(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude"),
    start_date: str = Query("2026-08-01"),
    end_date: str = Query("2026-09-10"),
):
    """Get NDVI from Sentinel-2 for a location."""
    sd = date.fromisoformat(start_date)
    ed = date.fromisoformat(end_date)
    return satellite.get_sentinel2_composite(lat, lon, sd, ed)


@router.get("/satellite/sar")
def get_sar_timeseries(
    lat: float = Query(...),
    lon: float = Query(...),
    start_date: str = Query("2026-08-01"),
    end_date: str = Query("2026-09-10"),
):
    """Get Sentinel-1 SAR time-series for a location."""
    sd = date.fromisoformat(start_date)
    ed = date.fromisoformat(end_date)
    return satellite.get_sentinel1_timeseries(lat, lon, sd, ed)


@router.get("/weather/rainfall")
def get_rainfall(
    lat: float = Query(...),
    lon: float = Query(...),
    ref_date: str = Query("2026-09-10"),
    days: int = Query(30),
):
    """Get rainfall summary for a location."""
    d = date.fromisoformat(ref_date)
    if days <= 30:
        return weather.get_rainfall_30d(lat, lon, d)
    return weather.get_rainfall_60d(lat, lon, d)


@router.get("/weather/temperature")
def get_temperature(
    lat: float = Query(...),
    lon: float = Query(...),
    ref_date: str = Query("2026-09-10"),
):
    """Get temperature summary for a location."""
    d = date.fromisoformat(ref_date)
    return weather.get_temperature_summary(lat, lon, d)


@router.get("/weather/flood-risk")
def get_flood_risk(
    lat: float = Query(...),
    lon: float = Query(...),
    ref_date: str = Query("2026-09-10"),
):
    """Get flood risk assessment for a location."""
    d = date.fromisoformat(ref_date)
    return weather.get_flood_risk(lat, lon, d)
