"""Satellite data ingestion via Google Earth Engine (GEE).

Real free data sources:
- Sentinel-2 optical: CLOUD/S2_SR_HARMONIZED (ESA, free via GEE)
- Sentinel-1 SAR: CLOUD/S1_GRD (ESA, free via GEE)

Setup:
1. Create a GEE account at https://earthengine.google.com/
2. Create a GCP project and enable Earth Engine API
3. Set GEE_PROJECT_ID env var
4. Authenticate: `earthengine authenticate`
"""
import os
import math
import logging
from datetime import date, timedelta
from typing import Optional

logger = logging.getLogger("sarp.satellite")

GEE_PROJECT_ID = os.getenv("GEE_PROJECT_ID", "")


def _get_ee():
    """Initialize Earth Engine, return ee module or None."""
    if not GEE_PROJECT_ID:
        return None
    try:
        import ee
        ee.Initialize(project=GEE_PROJECT_ID)
        return ee
    except Exception as e:
        logger.warning(f"GEE initialization failed: {e}")
        return None


# ============================================================
# Sentinel-2 (Optical) — NDVI, NDWI, EVI
# ============================================================

def get_sentinel2_composite(
    lat: float,
    lon: float,
    start_date: date,
    end_date: date,
    cloud_max_pct: int = 20,
) -> dict:
    """Fetch Sentinel-2 cloud-free composite from GEE.

    Free via: https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_SR_HARMONIZED
    """
    ee = _get_ee()
    if not ee:
        return _simulate_sentinel2(lat, lon, start_date, end_date)

    try:
        point = ee.Geometry.Point([lon, lat])

        # Load Sentinel-2 Surface Reflectance (harmonized)
        collection = (
            ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
            .filterBounds(point)
            .filterDate(start_date.isoformat(), end_date.isoformat())
            .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", cloud_max_pct))
            .sort("CLOUDY_PIXEL_PERCENTAGE")
        )

        count = collection.size().getInfo()
        if count == 0:
            logger.info(f"No Sentinel-2 images for ({lat},{lon}) in date range")
            return _simulate_sentinel2(lat, lon, start_date, end_date)

        # Take the least cloudy image
        image = collection.first()

        # Compute spectral indices
        ndvi = image.normalizedDifference(["B8", "B4"]).rename("NDVI")
        ndwi = image.normalizedDifference(["B3", "B8"]).rename("NDWI")
        evi = image.expression(
            "2.5 * ((NIR - RED) / (NIR + 6 * RED - 7.5 * BLUE + 1))",
            {
                "NIR": image.select("B8"),
                "RED": image.select("B4"),
                "BLUE": image.select("B2"),
            },
        ).rename("EVI")

        # Sample at point
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
        logger.error(f"GEE Sentinel-2 fetch failed: {e}")
        return _simulate_sentinel2(lat, lon, start_date, end_date)


# ============================================================
# Sentinel-1 (SAR) — VV, VH backscatter
# ============================================================

def get_sentinel1_timeseries(
    lat: float,
    lon: float,
    start_date: date,
    end_date: date,
) -> list[dict]:
    """Fetch Sentinel-1 SAR time-series from GEE.

    Free via: https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_SR_HARMONIZED
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
        )

        count = collection.size().getInfo()
        if count == 0:
            return _simulate_sentinel1(lat, lon, start_date, end_date)

        results = []
        image_list = collection.toList(count)

        for i in range(min(count, 20)):  # limit to 20 observations
            image = ee.Image(image_list.get(i))
            date_str = image.date().format("YYYY-MM-dd").getInfo()

            vv = image.select("VV").reduceRegion(
                ee.Reducer.mean(), point.buffer(100), 10,
            ).get("VV")
            vh = image.select("VH").reduceRegion(
                ee.Reducer.mean(), point.buffer(100), 10,
            ).get("VH")

            vv_val = vv.getInfo() if vv else -12
            vh_val = vh.getInfo() if vh else -18

            results.append({
                "date": date_str,
                "vv_db": round(float(vv_val or -12), 2),
                "vh_db": round(float(vh_val or -18), 2),
                "vh_vv_ratio": round(float(vh_val or -18) - float(vv_val or -12), 2),
                "source": "sentinel1_gee",
            })

        return results

    except Exception as e:
        logger.error(f"GEE Sentinel-1 fetch failed: {e}")
        return _simulate_sentinel1(lat, lon, start_date, end_date)


# ============================================================
# MODIS Land Cover
# ============================================================

def get_modis_landcover(lat: float, lon: float) -> dict:
    """Fetch MODIS land cover classification from GEE.

    Free via: https://developers.google.com/earth-engine/datasets/catalog/MODIS_061_MCD12Q1
    """
    ee = _get_ee()
    if not ee:
        return {"landcover": "unknown", "source": "simulated"}

    try:
        point = ee.Geometry.Point([lon, lat])

        # MODIS Land Cover Type (annual)
        modis = ee.ImageCollection("MODIS/061/MCD12Q1") \
            .filterDate("2025-01-01", "2025-12-31") \
            .first()

        lc_band = modis.select("LC_Type1")
        value = lc_band.reduceRegion(ee.Reducer.first(), point, 500).get("LC_Type1").getInfo()

        # IGBP classification mapping
        igbp_classes = {
            1: "evergreen_needleleaf_forest",
            2: "evergreen_broadleaf_forest",
            4: "deciduous_broadleaf_forest",
            5: "mixed_forests",
            8: "woody_savannas",
            9: "savannas",
            10: "grasslands",
            12: "croplands",
            14: "cropland_natural_mosaic",
        }

        return {
            "landcover_code": value,
            "landcover": igbp_classes.get(value, f"class_{value}"),
            "is_cropland": value in [12, 14],
            "source": "modis_gee",
        }

    except Exception as e:
        logger.error(f"GEE MODIS fetch failed: {e}")
        return {"landcover": "unknown", "source": "simulated"}


# ============================================================
# Simulated Data Fallbacks
# ============================================================

def _simulate_sentinel2(lat, lon, start_date, end_date):
    """Realistic simulated Sentinel-2 data based on Cambodia climate."""
    seed = int((lat * 1000 + lon * 100) % 100)
    day_of_year = start_date.timetuple().tm_yday

    if 150 <= day_of_year <= 280:  # Wet season
        ndvi = 0.55 + 0.2 * math.sin((day_of_year - 150) * math.pi / 130)
    else:
        ndvi = 0.3 + 0.05 * math.sin(day_of_year * math.pi / 180)

    return {
        "ndvi": round(ndvi + (seed % 10) / 100, 3),
        "ndwi": round(0.1 + (seed % 15) / 100, 3),
        "evi": round(ndvi * 0.9 + 0.05, 3),
        "cloud_cover": 15 + (seed % 20),
        "source": "simulated",
    }


def _simulate_sentinel1(lat, lon, start_date, end_date):
    """Simulated Sentinel-1 SAR data."""
    seed = int((lat * 1000 + lon * 100) % 100)
    observations = []
    current = start_date
    while current <= end_date:
        observations.append({
            "date": current.isoformat(),
            "vv_db": round(-12.0 + (seed % 10) / 5, 2),
            "vh_db": round(-18.0 + (seed % 8) / 5, 2),
            "vh_vv_ratio": round(-6.0 + (seed % 5) / 5, 2),
            "source": "simulated",
        })
        current += timedelta(days=6)
    return observations
