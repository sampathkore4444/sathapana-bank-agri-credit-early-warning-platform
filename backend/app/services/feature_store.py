"""Parquet-based feature store for per-farm per-period features.

Persists computed features to Parquet files for:
- Fast model training/inference
- Historical feature tracking
- Audit trail
"""
import os
import json
from pathlib import Path
from datetime import date
from typing import Optional

import pandas as pd
from sqlalchemy.orm import Session

from app.models import Farmer, RiskScore
from app.services.feature_engine import compute_all_features

FEATURE_STORE_DIR = Path(__file__).parent.parent.parent / "feature_store"
FEATURE_STORE_DIR.mkdir(exist_ok=True)


def compute_and_store_features(db: Session, farmer_id: int) -> Optional[dict]:
    """Compute features for a farmer and store in Parquet."""
    features = compute_all_features(db, farmer_id)
    if not features:
        return None

    features["farmer_id"] = farmer_id
    features["snapshot_date"] = date.today().isoformat()

    # Append to per-date file
    date_str = date.today().isoformat()
    file_path = FEATURE_STORE_DIR / f"features_{date_str}.parquet"

    df = pd.DataFrame([features])

    if file_path.exists():
        existing = pd.read_parquet(file_path)
        # Remove old entry for this farmer if exists
        existing = existing[existing["farmer_id"] != farmer_id]
        df = pd.concat([existing, df], ignore_index=True)

    df.to_parquet(file_path, index=False)
    return features


def store_all_features(db: Session) -> dict:
    """Compute and store features for all farmers."""
    farmers = db.query(Farmer).all()
    stored = 0
    for farmer in farmers:
        result = compute_and_store_features(db, farmer.id)
        if result:
            stored += 1

    return {
        "stored": stored,
        "total": len(farmers),
        "file": f"features_{date.today().isoformat()}.parquet",
    }


def load_features(
    date_str: Optional[str] = None,
    farmer_id: Optional[int] = None,
) -> pd.DataFrame:
    """Load features from the store.

    Args:
        date_str: Date to load (YYYY-MM-DD). Latest if None.
        farmer_id: Specific farmer. All if None.
    """
    if date_str:
        file_path = FEATURE_STORE_DIR / f"features_{date_str}.parquet"
        if not file_path.exists():
            return pd.DataFrame()
        df = pd.read_parquet(file_path)
    else:
        # Load all available dates
        files = sorted(FEATURE_STORE_DIR.glob("features_*.parquet"))
        if not files:
            return pd.DataFrame()
        df = pd.concat([pd.read_parquet(f) for f in files], ignore_index=True)

    if farmer_id:
        df = df[df["farmer_id"] == farmer_id]

    return df


def get_feature_store_summary() -> dict:
    """Get summary of the feature store."""
    files = list(FEATURE_STORE_DIR.glob("features_*.parquet"))
    total_rows = 0
    for f in files:
        try:
            total_rows += len(pd.read_parquet(f))
        except Exception:
            pass

    return {
        "files": len(files),
        "total_rows": total_rows,
        "latest_file": files[-1].name if files else None,
        "store_path": str(FEATURE_STORE_DIR),
    }
