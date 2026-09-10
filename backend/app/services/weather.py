"""Weather data ingestion via free APIs.

Real free data sources:
- CHIRPS rainfall: https://data.chc.ucsb.edu/products/CHIRPS-2.0/
  - REST API via CHC: https://www.chc.ucsb.edu/data/chirps
- ERA5 temperature: https://cds.climate.copernicus.eu/
  - CDS API: requires free CDS account
- MRC flood data: https://portal.mrcmekong.org/
  - API available for flood alerts

Setup:
1. CHIRPS: No auth needed for basic REST
2. ERA5: Register at https://cds.climate.copernicus.eu/, get API key
3. MRC: Register at https://portal.mrcmekong.org/
"""
import os
import math
import logging
from datetime import date, timedelta
from typing import Optional

logger = logging.getLogger("sarp.weather")

# API configuration
CHIRPS_BASE_URL = os.getenv("CHIRPS_API_URL", "https://data.chc.ucsb.edu/products/CHIRPS-2.0")
ERA5_API_URL = os.getenv("ERA5_API_URL", "")
ERA5_API_KEY = os.getenv("ERA5_API_KEY", "")
MRC_API_URL = os.getenv("MRC_API_URL", "")


# ============================================================
# CHIRPS Rainfall
# ============================================================

def get_rainfall_30d(lat: float, lon: float, ref_date: date) -> dict:
    """Get 30-day rainfall from CHIRPS.

    Free via: https://data.chc.ucsb.edu/products/CHIRPS-2.0/
    """
    if CHIRPS_BASE_URL and not CHIRPS_BASE_URL.startswith("https://data.chc.ucsb.edu"):
        return _fetch_chirps_api(lat, lon, ref_date, days=30)
    return _simulate_rainfall(lat, lon, ref_date, days=30)


def get_rainfall_60d(lat: float, lon: float, ref_date: date) -> dict:
    """Get 60-day rainfall from CHIRPS."""
    if CHIRPS_BASE_URL and not CHIRPS_BASE_URL.startswith("https://data.chc.ucsb.edu"):
        return _fetch_chirps_api(lat, lon, ref_date, days=60)
    return _simulate_rainfall(lat, lon, ref_date, days=60)


def _fetch_chirps_api(lat, lon, ref_date, days=30):
    """Real CHIRPS rainfall fetch via CHC API."""
    try:
        import httpx

        start = ref_date - timedelta(days=days)

        # CHIRPS API endpoint (daily precipitation)
        url = (
            f"https://data.chc.ucsb.edu/products/CHIRPS-2.0/"
            f"daily/p05/{ref_date.year}/"
            f"chirps-v2.0.{ref_date.year}.{ref_date.month:02d}.{ref_date.day:02d}.tif"
        )

        # Alternative: Use CHIRPS netCDF timeseries via OPeNDAP
        # For simplicity, use the direct file approach
        resp = httpx.get(url, timeout=10, follow_redirects=True)

        if resp.status_code == 200:
            # Parse the GeoTIFF response
            # For now, use the CHIRPS global summary
            total = _parse_chirps_tif(resp.content, lat, lon)
        else:
            total = None

        if total is None:
            return _simulate_rainfall(lat, lon, ref_date, days)

        normal = _get_chirps_normal(lat, lon, start, ref_date)
        deviation = ((total - normal) / normal * 100) if normal > 0 else 0

        return {
            "rainfall_30d_mm": round(total, 1),
            "normal_30d_mm": round(normal, 1),
            "deviation_pct": round(deviation, 1),
            "source": "chirps",
        }

    except Exception as e:
        logger.warning(f"CHIRPS fetch failed: {e}")
        return _simulate_rainfall(lat, lon, ref_date, days)


def _parse_chirps_tif(tif_bytes, lat, lon):
    """Extract rainfall value from CHIRPS GeoTIFF for a point."""
    try:
        import rasterio
        import io
        with rasterio.open(io.BytesIO(tif_bytes)) as src:
            for val in src.sample([(lon, lat)]):
                if val[0] != src.nodata:
                    return float(val[0])
    except Exception:
        pass
    return None


def _get_chirps_normal(lat, lon, start, end):
    """Get normal (average) rainfall for the region."""
    day_of_year = start.timetuple().tm_yday
    if 120 <= day_of_year <= 300:  # Wet season
        return 5.0 * (end - start).days
    return 1.5 * (end - start).days


# ============================================================
# ERA5 Temperature
# ============================================================

def get_temperature_summary(lat: float, lon: float, ref_date: date) -> dict:
    """Get temperature summary from ERA5.

    Free via: https://cds.climate.copernicus.eu/
    Requires: CDS API key
    """
    if ERA5_API_URL and ERA5_API_KEY:
        return _fetch_era5_api(lat, lon, ref_date)
    return _simulate_temperature(lat, lon, ref_date)


def _fetch_era5_api(lat, lon, ref_date):
    """Real ERA5 temperature fetch via CDS API."""
    try:
        import cdsapi

        start = ref_date - timedelta(days=30)

        client = cdsapi.Client(url=ERA5_API_URL, key=ERA5_API_KEY)

        result = client.retrieve(
            "reanalysis-era5-single-levels",
            {
                "product_type": "reanalysis",
                "variable": ["2m_temperature"],
                "year": str(ref_date.year),
                "month": f"{ref_date.month:02d}",
                "day": [f"{ref_date.day:02d}" for d in range(1, ref_date.day + 1)],
                "time": ["12:00"],  # noon snapshot
                "area": [lat + 0.1, lon - 0.1, lat - 0.1, lon + 0.1],
                "format": "netcdf",
            },
        )

        # Parse NetCDF
        import xarray as xr
        ds = xr.open_dataset(result)
        temps = ds["t2m"].values.flatten() - 273.15  # K to °C

        return {
            "temp_avg_c": round(float(temps.mean()), 1),
            "temp_max_c": round(float(temps.max()), 1),
            "temp_min_c": round(float(temps.min()), 1),
            "stress_days": int(sum(1 for t in temps if t > 38)),
            "source": "era5",
        }

    except Exception as e:
        logger.warning(f"ERA5 fetch failed: {e}")
        return _simulate_temperature(lat, lon, ref_date)


# ============================================================
# MRC Flood Data
# ============================================================

def get_flood_risk(lat: float, lon: float, ref_date: date) -> dict:
    """Get flood risk from MRC + rainfall analysis.

    MRC portal: https://portal.mrcmekong.org/
    """
    if MRC_API_URL:
        return _fetch_mrc_flood(lat, lon, ref_date)

    # Fallback: derive from rainfall
    rainfall = get_rainfall_30d(lat, lon, ref_date)

    risk_level = "low"
    if rainfall["deviation_pct"] > 50:
        risk_level = "high"
    elif rainfall["deviation_pct"] > 20:
        risk_level = "moderate"

    return {
        "risk_level": risk_level,
        "rainfall_anomaly": rainfall["deviation_pct"],
        "mrc_alert": False,
        "source": "rainfall_derived",
    }


def _fetch_mrc_flood(lat, lon, ref_date):
    """Real MRC flood data fetch."""
    try:
        import httpx

        # MRC Mekong Flood Monitoring API
        url = f"{MRC_API_URL}/api/flood-monitoring"
        resp = httpx.get(url, timeout=10)
        data = resp.json()

        # Check for alerts near this location
        alerts = data.get("alerts", [])
        nearby = [
            a for a in alerts
            if abs(a.get("lat", 0) - lat) < 0.5 and abs(a.get("lon", 0) - lon) < 0.5
        ]

        return {
            "risk_level": "high" if nearby else "low",
            "rainfall_anomaly": 0,
            "mrc_alert": bool(nearby),
            "mrc_alerts_count": len(nearby),
            "source": "mrc",
        }

    except Exception as e:
        logger.warning(f"MRC fetch failed: {e}")
        rainfall = get_rainfall_30d(lat, lon, ref_date)
        return {
            "risk_level": "low",
            "rainfall_anomaly": rainfall["deviation_pct"],
            "mrc_alert": False,
            "source": "rainfall_derived",
        }


# ============================================================
# Cambodia Admin Boundaries
# ============================================================

def get_cambodia_boundaries():
    """Get Cambodia admin boundaries from GADM.

    Free via: https://gadm.org/download_country.html
    """
    try:
        import geopandas as gpd
        # GADM provides free admin boundary shapefiles
        # Download once and cache
        import os
        cache_path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "gadm41_KHM_shp")

        if os.path.exists(cache_path):
            provinces = gpd.read_file(os.path.join(cache_path, "gadm41_KHM_1.shp"))
            districts = gpd.read_file(os.path.join(cache_path, "gadm41_KHM_2.shp"))
            return {
                "provinces": len(provinces),
                "districts": len(districts),
                "province_names": provinces["NAME_1"].tolist(),
                "source": "gadm_cached",
            }
        else:
            return {
                "message": "Download GADM data from https://gadm.org/download_country.html",
                "instructions": "Extract to backend/data/gadm41_KHM_shp/",
                "source": "not_downloaded",
            }
    except ImportError:
        return {"error": "Install geopandas for admin boundaries: pip install geopandas"}


# ============================================================
# Simulated Data Fallbacks
# ============================================================

def _simulate_rainfall(lat, lon, ref_date, days=30):
    seed = int((lat * 1000 + lon * 100 + ref_date.timetuple().tm_yday) % 100)
    day_of_year = ref_date.timetuple().tm_yday

    if 120 <= day_of_year <= 300:
        normal = 5.0 * days
    else:
        normal = 1.5 * days

    actual = normal * (0.4 + (seed % 12) / 10)
    deviation = ((actual - normal) / normal * 100) if normal > 0 else 0

    return {
        "rainfall_30d_mm": round(actual, 1),
        "normal_30d_mm": round(normal, 1),
        "deviation_pct": round(deviation, 1),
        "source": "simulated",
    }


def _simulate_temperature(lat, lon, ref_date):
    day_of_year = ref_date.timetuple().tm_yday
    avg = 28 + 4 * math.sin((day_of_year - 100) * math.pi / 182)
    return {
        "temp_avg_c": round(avg, 1),
        "temp_max_c": round(avg + 6, 1),
        "temp_min_c": round(avg - 5, 1),
        "stress_days": 2 if avg > 32 else 0,
        "source": "simulated",
    }
