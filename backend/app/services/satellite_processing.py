"""Satellite image preprocessing for Sentinel-2.

Implements:
- Cloud masking using SCL band
- Zonal statistics per farm polygon
- Temporal interpolation for gap-filling
- Cloud-free compositing
"""
import logging
import math
from datetime import date, timedelta
from typing import Optional
import numpy as np

logger = logging.getLogger(__name__)


# Sentinel-2 Scene Classification (SCL) values
SCL_CLOUD_CLASSES = [8, 9, 10]  # Cloud medium/high probability, cirrus
SCL_SHADOW_CLASSES = [3]  # Cloud shadow
SCL_VALID_CLASSES = [4, 5, 6, 7]  # Vegetation, bare soil, water, snow


def cloud_mask_scl(scl_band: np.ndarray) -> np.ndarray:
    """Apply cloud mask using Sentinel-2 SCL band.

    Args:
        scl_band: 2D array of Scene Classification values.

    Returns:
        Boolean mask where True = clear (usable) pixels.
    """
    mask = np.ones_like(scl_band, dtype=bool)
    for cls in SCL_CLOUD_CLASSES + SCL_SHADOW_CLASSES:
        mask[scl_band == cls] = False
    return mask


def cloud_mask_probability(cloud_prob: np.ndarray, threshold: float = 0.5) -> np.ndarray:
    """Apply cloud mask using cloud probability band.

    Args:
        cloud_prob: 2D array of cloud probability (0-1).
        threshold: Probability threshold above which pixel is cloudy.

    Returns:
        Boolean mask where True = clear pixels.
    """
    return cloud_prob < threshold


def compute_zonal_statistics(
    values: np.ndarray,
    mask: Optional[np.ndarray] = None,
) -> dict:
    """Compute per-farm zonal statistics from a raster band.

    Args:
        values: 2D array of pixel values within farm boundary.
        mask: Optional boolean mask (True = valid pixels).

    Returns:
        Dict with mean, median, std, percentiles, fraction.
    """
    if mask is not None:
        valid = values[mask]
    else:
        valid = values.flatten()

    if len(valid) == 0:
        return {
            "mean": 0, "median": 0, "std": 0,
            "p10": 0, "p25": 0, "p75": 0, "p90": 0,
            "fraction_valid": 0,
        }

    return {
        "mean": round(float(np.mean(valid)), 4),
        "median": round(float(np.median(valid)), 4),
        "std": round(float(np.std(valid)), 4),
        "p10": round(float(np.percentile(valid, 10)), 4),
        "p25": round(float(np.percentile(valid, 25)), 4),
        "p75": round(float(np.percentile(valid, 75)), 4),
        "p90": round(float(np.percentile(valid, 90)), 4),
        "fraction_valid": round(float(len(valid) / values.size), 3),
    }


def compute_ndvi_zonal(red_band: np.ndarray, nir_band: np.ndarray, mask: np.ndarray) -> dict:
    """Compute NDVI with zonal statistics.

    Args:
        red_band: Sentinel-2 B4 (Red) reflectance.
        nir_band: Sentinel-2 B8 (NIR) reflectance.
        mask: Cloud mask (True = clear).

    Returns:
        Dict with NDVI statistics.
    """
    red = red_band[mask].astype(float)
    nir = nir_band[mask].astype(float)

    denom = nir + red
    valid = denom > 0

    ndvi = np.where(valid, (nir - red) / denom, 0)

    return compute_zonal_statistics(ndvi)


def temporal_interpolation(
    observations: list[dict],
    max_gap_days: int = 15,
) -> list[dict]:
    """Fill gaps in time-series using linear interpolation.

    Args:
        observations: List of dicts with 'date', 'ndvi', etc.
        max_gap_days: Maximum gap to interpolate across.

    Returns:
        List with interpolated values filling gaps.
    """
    try:
        return _temporal_interpolation(observations, max_gap_days)
    except Exception as exc:
        logger.exception("Temporal interpolation failed; returning raw observations")
        return observations


def _temporal_interpolation(observations: list[dict], max_gap_days: int) -> list[dict]:
    if len(observations) < 2:
        return observations

    # Sort by date
    sorted_obs = sorted(observations, key=lambda x: x["date"])

    # Find gaps
    filled = [sorted_obs[0]]
    for i in range(1, len(sorted_obs)):
        prev = sorted_obs[i - 1]
        curr = sorted_obs[i]
        gap = (curr["date"] - prev["date"]).days

        if gap > max_gap_days:
            # Interpolate missing observations
            n_missing = gap // 5 - 1  # assume 5-day intervals
            for j in range(1, n_missing + 1):
                frac = j / (n_missing + 1)
                interp = {}
                for key in prev:
                    if key == "date":
                        interp[key] = prev["date"] + timedelta(days=j * 5)
                    elif isinstance(prev[key], (int, float)):
                        interp[key] = round(
                            prev[key] + frac * (curr[key] - prev[key]), 4
                        )
                    else:
                        interp[key] = prev[key]
                interp["interpolated"] = True
                filled.append(interp)

        filled.append(curr)

    return filled


def build_cloud_free_composite(
    daily_observations: list[dict],
    composite_window_days: int = 5,
) -> list[dict]:
    """Build cloud-free composites from daily observations.

    Groups observations by time window and computes the median/cloud-free values.

    Args:
        daily_observations: List of dicts with 'date', pixel values, cloud mask.
        composite_window_days: Window size for compositing.

    Returns:
        List of composite observations.
    """
    try:
        return _build_cloud_free_composite(daily_observations, composite_window_days)
    except Exception as exc:
        logger.exception("Cloud-free compositing failed")
        return []


def _build_cloud_free_composite(
    daily_observations: list[dict],
    composite_window_days: int,
) -> list[dict]:
    if not daily_observations:
        return []

    sorted_obs = sorted(daily_observations, key=lambda x: x["date"])
    composites = []

    window_start = sorted_obs[0]["date"]
    window_obs = [sorted_obs[0]]

    for obs in sorted_obs[1:]:
        if (obs["date"] - window_start).days <= composite_window_days:
            window_obs.append(obs)
        else:
            # Create composite from window
            composite = _median_composite(window_obs)
            composite["date"] = window_start + timedelta(days=composite_window_days // 2)
            composites.append(composite)

            window_start = obs["date"]
            window_obs = [obs]

    # Final window
    if window_obs:
        composite = _median_composite(window_obs)
        composite["date"] = window_start + timedelta(days=composite_window_days // 2)
        composites.append(composite)

    return composites


def _median_composite(observations: list[dict]) -> dict:
    """Compute median composite from a set of observations."""
    if len(observations) == 1:
        return observations[0]

    result = {"date": observations[0]["date"], "source": "composite"}
    for key in observations[0]:
        if key in ("date", "source", "interpolated"):
            continue
        values = [obs[key] for obs in observations if key in obs and isinstance(obs[key], (int, float))]
        if values:
            result[key] = round(float(np.median(values)), 4)

    return result


def sar_preprocessing(vv: np.ndarray, vh: np.ndarray) -> dict:
    """Basic Sentinel-1 SAR preprocessing.

    In production this would include:
    - Orbit correction
    - Radiometric calibration
    - Speckle filtering (Lee, Refined Lee)
    - Terrain correction

    For PoC: basic radiometric normalization.
    """
    # Linear to dB conversion (if input is linear power)
    vv_db = 10 * np.log10(np.maximum(vv, 1e-10))
    vh_db = 10 * np.log10(np.maximum(vh, 1e-10))

    # VH/VV ratio (crop type indicator)
    ratio = vh_db - vv_db

    return {
        "vv_db": round(float(np.mean(vv_db)), 2),
        "vh_db": round(float(np.mean(vh_db)), 2),
        "vv_vh_ratio": round(float(np.mean(ratio)), 2),
    }
