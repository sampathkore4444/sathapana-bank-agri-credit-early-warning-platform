"""Google Earth Engine Data Ingestion Pipeline.

Fetches real Sentinel-2 and Sentinel-1 satellite data for all pilot farms
from Google Earth Engine (free tier). Stores computed indices as CropHealth
records in the database.

Usage:
    from app.services.gee_ingestion import run_full_ingestion
    result = run_full_ingestion(db)

Environment:
    GEE_PROJECT_ID must be set for real data.
    Falls back to simulated data if GEE is not configured.
"""
import os
import math
import logging
from datetime import date, timedelta, datetime
from typing import Optional

logger = logging.getLogger("sarp.gee")

GEE_PROJECT_ID = os.getenv("GEE_PROJECT_ID", "")


# ============================================================
# GEE Connection
# ============================================================

def _get_ee():
    """Initialize Earth Engine, return ee module or None."""
    if not GEE_PROJECT_ID:
        return None
    try:
        import ee
        ee.Initialize(project=GEE_PROJECT_ID)
        return ee
    except Exception as e:
        logger.error(f"GEE initialization failed: {e}")
        return None


# ============================================================
# Sentinel-2 Fetching
# ============================================================

def fetch_sentinel2_for_farm(lat: float, lon: float, start_date: date, end_date: date, cloud_max: int = 20) -> dict:
    """Fetch Sentinel-2 spectral indices for a single farm location.

    Returns dict with ndvi, ndwi, evi, cloud_cover, observation_date, source.
    """
    ee = _get_ee()
    if not ee:
        return _simulate_sentinel2(lat, lon, start_date, end_date)

    try:
        point = ee.Geometry.Point([lon, lat])

        collection = (
            ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
            .filterBounds(point)
            .filterDate(start_date.isoformat(), end_date.isoformat())
            .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", cloud_max))
            .sort("CLOUDY_PIXEL_PERCENTAGE")
        )

        count = collection.size().getInfo()
        if count == 0:
            logger.info(f"No S2 images for ({lat},{lon}) {start_date}-{end_date}")
            return _simulate_sentinel2(lat, lon, start_date, end_date)

        image = collection.first()

        # Compute indices
        ndvi = image.normalizedDifference(["B8", "B4"]).rename("NDVI")
        ndwi = image.normalizedDifference(["B3", "B8"]).rename("NDWI")
        evi = image.expression(
            "2.5 * ((NIR - RED) / (NIR + 6 * RED - 7.5 * BLUE + 1))",
            {"NIR": image.select("B8"), "RED": image.select("B4"), "BLUE": image.select("B2")},
        ).rename("EVI")

        # Sample at farm centroid (buffer 100m for zonal average)
        result = ee.Dictionary({
            "ndvi": ndvi.reduceRegion(ee.Reducer.mean(), point.buffer(100), 10).get("NDVI"),
            "ndwi": ndwi.reduceRegion(ee.Reducer.mean(), point.buffer(100), 10).get("NDWI"),
            "evi": evi.reduceRegion(ee.Reducer.mean(), point.buffer(100), 10).get("EVI"),
            "cloud_cover": image.get("CLOUDY_PIXEL_PERCENTAGE"),
            "date": image.date().format("YYYY-MM-dd").getInfo(),
            "images_found": count,
        }).getInfo()

        return {
            "ndvi": round(float(result.get("ndvi") or 0), 4),
            "ndwi": round(float(result.get("ndwi") or 0), 4),
            "evi": round(float(result.get("evi") or 0), 4),
            "cloud_cover": result.get("cloud_cover"),
            "observation_date": result.get("date"),
            "images_found": result.get("images_found"),
            "source": "sentinel2_gee",
        }

    except Exception as e:
        logger.error(f"GEE S2 fetch failed for ({lat},{lon}): {e}")
        return _simulate_sentinel2(lat, lon, start_date, end_date)


# ============================================================
# Sentinel-1 Fetching
# ============================================================

def fetch_sentinel1_for_farm(lat: float, lon: float, start_date: date, end_date: date) -> dict:
    """Fetch Sentinel-1 SAR backscatter for a single farm location.

    Returns dict with vv_db, vh_db, vh_vv_ratio, observation_date, source.
    """
    ee = _get_ee()
    if not ee:
        return _simulate_sentinel1(lat, lon, start_date, end_date)

    try:
        point = ee.Geometry.Point([lon, lat])

        collection = (
            ee.ImageCollection("COPERNICUS/S1_GRD")
            .filterBounds(point)
            .filterDate(start_date.isoformat(), end_date.isoformat())
            .filter(ee.Filter.listContains("transmitterReceiverPolarisation", "VV"))
            .filter(ee.Filter.listContains("transmitterReceiverPolarisation", "VH"))
            .filter(ee.Filter.eq("instrumentMode", "IW"))
            .sort("system:time_start", False)  # most recent first
        )

        count = collection.size().getInfo()
        if count == 0:
            return _simulate_sentinel1(lat, lon, start_date, end_date)

        image = collection.first()

        vv = image.select("VV").reduceRegion(
            ee.Reducer.mean(), point.buffer(100), 10,
        ).get("VV")
        vh = image.select("VH").reduceRegion(
            ee.Reducer.mean(), point.buffer(100), 10,
        ).get("VH")

        vv_val = float(vv.getInfo() or -12)
        vh_val = float(vh.getInfo() or -18)

        return {
            "vv_db": round(vv_val, 2),
            "vh_db": round(vh_val, 2),
            "vh_vv_ratio": round(vh_val - vv_val, 2),
            "observation_date": image.date().format("YYYY-MM-dd").getInfo(),
            "images_found": count,
            "source": "sentinel1_gee",
        }

    except Exception as e:
        logger.error(f"GEE S1 fetch failed for ({lat},{lon}): {e}")
        return _simulate_sentinel1(lat, lon, start_date, end_date)


# ============================================================
# Crop Health Score Computation
# ============================================================

def compute_health_score_from_satellite(
    ndvi: float, ndvi_historical: float,
    ndwi: float, vv_db: float,
    rainfall_dev: float, temp_stress_days: int,
) -> dict:
    """Compute Crop Health Score using SPEC §9 weighted formula.

    Score = NDVI_deviation(30%) + NDVI_trend(20%) + NDWI(15%)
          + SAR(10%) + Rainfall(15%) + Temperature(10%)
    """
    # NDVI deviation
    ndvi_dev = ((ndvi - ndvi_historical) / ndvi_historical * 100) if ndvi_historical > 0 else 0
    ndvi_dev_score = max(0, min(100, 50 + ndvi_dev * 2.5))

    # NDVI trend (use deviation as proxy for single observation)
    trend_score = max(0, min(100, 50 + ndvi_dev * 1.5))

    # NDWI
    ndwi_score = max(0, min(100, (ndwi + 0.2) / 0.5 * 100))

    # SAR moisture
    sar_score = max(0, min(100, (vv_db + 20) / 15 * 100))

    # Rainfall
    rain_score = max(0, min(100, 50 + rainfall_dev * 0.83))

    # Temperature stress
    temp_score = max(0, 100 * (1 - temp_stress_days / 30))

    # Weighted sum
    total = (
        ndvi_dev_score * 0.30 +
        trend_score * 0.20 +
        ndwi_score * 0.15 +
        sar_score * 0.10 +
        rain_score * 0.15 +
        temp_score * 0.10
    )
    total = round(max(0, min(100, total)))

    if total >= 80:
        status = "green"
    elif total >= 60:
        status = "yellow"
    elif total >= 40:
        status = "orange"
    else:
        status = "red"

    return {
        "crop_health_score": total,
        "status": status,
        "ndvi_deviation_pct": round(ndvi_dev, 1),
        "confidence": 0.85,
    }


# ============================================================
# Batch Ingestion
# ============================================================

def ingest_farm(db, farm) -> Optional[dict]:
    """Ingest satellite data for a single farm and create CropHealth record.

    Returns the new CropHealth record data, or None on failure.
    """
    from app.models import CropHealth, Farmer

    farmer = db.query(Farmer).filter(Farmer.id == farm.farmer_id).first()
    if not farmer:
        return None

    # Date range: last 15 days for latest observation
    end = date.today()
    start = end - timedelta(days=15)

    # Fetch satellite data
    s2 = fetch_sentinel2_for_farm(farm.centroid_lat, farm.centroid_lon, start, end)
    s1 = fetch_sentinel1_for_farm(farm.centroid_lat, farm.centroid_lon, start, end)

    # Get historical NDVI baseline
    hist_start = end - timedelta(days=365)
    hist_end = end - timedelta(days=30)
    s2_hist = fetch_sentinel2_for_farm(farm.centroid_lat, farm.centroid_lon, hist_start, hist_end, cloud_max=40)
    ndvi_historical = s2_hist.get("ndvi", 0.65)

    # Compute health score
    from app.services.weather import get_rainfall_30d, get_temperature_summary
    rainfall = get_rainfall_30d(farm.centroid_lat, farm.centroid_lon, end)
    temp = get_temperature_summary(farm.centroid_lat, farm.centroid_lon, end)

    health = compute_health_score_from_satellite(
        ndvi=s2.get("ndvi", 0),
        ndvi_historical=ndvi_historical,
        ndwi=s2.get("ndwi", 0),
        vv_db=s1.get("vv_db", -12),
        rainfall_dev=rainfall.get("deviation_pct", 0),
        temp_stress_days=temp.get("stress_days", 0),
    )

    # Determine growth stage from planting date
    growth_stage = "vegetative"
    if farm.planting_date:
        days_since = (end - farm.planting_date).days
        if days_since < 30:
            growth_stage = "bare_soil"
        elif days_since < 60:
            growth_stage = "vegetative"
        elif days_since < 100:
            growth_stage = "reproductive"
        else:
            growth_stage = "maturity"

    # Create CropHealth record
    obs_date = date.fromisoformat(s2.get("observation_date", end.isoformat())) if s2.get("observation_date") else end

    record = CropHealth(
        farm_id=farm.id,
        observation_date=obs_date,
        ndvi_current=s2.get("ndvi", 0),
        ndvi_historical=ndvi_historical,
        ndvi_deviation_pct=health["ndvi_deviation_pct"],
        ndvi_trend="stable",
        ndwi_current=s2.get("ndwi", 0),
        growth_stage=growth_stage,
        flood_exposure=rainfall.get("deviation_pct", 0) > 50,
        drought_stress=rainfall.get("deviation_pct", 0) < -30,
        rainfall_30d=rainfall.get("rainfall_30d_mm", 0),
        rainfall_deviation_30d=rainfall.get("deviation_pct", 0),
        temperature_stress_days=temp.get("stress_days", 0),
        sar_vh_backscatter=s1.get("vh_db", -18),
        crop_health_score=health["crop_health_score"],
        status=health["status"],
        confidence=health["confidence"],
    )
    db.add(record)

    return {
        "farm_id": farm.farm_code,
        "farmer_id": farmer.farmer_code,
        "observation_date": obs_date.isoformat(),
        "ndvi": s2.get("ndvi"),
        "ndwi": s2.get("ndwi"),
        "evi": s2.get("evi"),
        "vv_db": s1.get("vv_db"),
        "vh_db": s1.get("vh_db"),
        "rainfall_mm": rainfall.get("rainfall_30d_mm"),
        "temp_stress_days": temp.get("stress_days"),
        "health_score": health["crop_health_score"],
        "status": health["status"],
        "source_s2": s2.get("source"),
        "source_s1": s1.get("source"),
    }


def run_full_ingestion(db) -> dict:
    """Run satellite ingestion for ALL pilot farms.

    Returns summary of ingestion run.
    """
    from app.models import Farm

    farms = db.query(Farm).all()
    results = []
    errors = []
    sources = {"sentinel2_gee": 0, "sentinel1_gee": 0, "simulated": 0}

    for i, farm in enumerate(farms):
        try:
            result = ingest_farm(db, farm)
            if result:
                results.append(result)
                # Track data source
                if result.get("source_s2") == "sentinel2_gee":
                    sources["sentinel2_gee"] += 1
                else:
                    sources["simulated"] += 1
        except Exception as e:
            errors.append({"farm_id": farm.farm_code, "error": str(e)})
            logger.error(f"Ingestion failed for farm {farm.farm_code}: {e}")

        # Commit every 10 farms
        if (i + 1) % 10 == 0:
            db.commit()
            logger.info(f"Ingested {i + 1}/{len(farms)} farms")

    db.commit()

    gee_enabled = bool(GEE_PROJECT_ID)

    return {
        "total_farms": len(farms),
        "successful": len(results),
        "failed": len(errors),
        "errors": errors[:10],  # first 10 errors
        "data_sources": sources,
        "gee_enabled": gee_enabled,
        "gee_project": GEE_PROJECT_ID if gee_enabled else "not configured",
        "ingestion_time": datetime.utcnow().isoformat(),
    }


def get_ingestion_status(db) -> dict:
    """Check the status of satellite data for all farms."""
    from app.models import Farm, CropHealth

    farms = db.query(Farm).count()
    records = db.query(CropHealth).count()
    latest = (
        db.query(CropHealth.observation_date)
        .order_by(CropHealth.observation_date.desc())
        .first()
    )

    gee_enabled = bool(GEE_PROJECT_ID)

    return {
        "gee_enabled": gee_enabled,
        "gee_project": GEE_PROJECT_ID if gee_enabled else "not configured",
        "total_farms": farms,
        "total_observations": records,
        "latest_observation": latest[0].isoformat() if latest else None,
        "status": "real_data" if gee_enabled else "simulated_data",
    }


# ============================================================
# Simulated Fallbacks
# ============================================================

def _simulate_sentinel2(lat, lon, start_date, end_date):
    seed = int((lat * 1000 + lon * 100) % 100)
    doy = start_date.timetuple().tm_yday
    if 150 <= doy <= 280:
        ndvi = 0.55 + 0.2 * math.sin((doy - 150) * math.pi / 130)
    else:
        ndvi = 0.3 + 0.05 * math.sin(doy * math.pi / 180)
    return {
        "ndvi": round(ndvi + (seed % 10) / 100, 3),
        "ndwi": round(0.1 + (seed % 15) / 100, 3),
        "evi": round(ndvi * 0.9 + 0.05, 3),
        "cloud_cover": 15 + (seed % 20),
        "observation_date": end_date.isoformat(),
        "images_found": 1,
        "source": "simulated",
    }


def _simulate_sentinel1(lat, lon, start_date, end_date):
    seed = int((lat * 1000 + lon * 100) % 100)
    return {
        "vv_db": round(-12.0 + (seed % 10) / 5, 2),
        "vh_db": round(-18.0 + (seed % 8) / 5, 2),
        "vh_vv_ratio": round(-6.0 + (seed % 5) / 5, 2),
        "observation_date": end_date.isoformat(),
        "images_found": 1,
        "source": "simulated",
    }
