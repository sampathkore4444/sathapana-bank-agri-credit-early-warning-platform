"""Seed realistic mock data for the SARP PoC demo.

Usage: cd backend && python seed.py
"""
import random
import json
from datetime import date, timedelta

from app.database import SessionLocal, engine, Base
from app.models import Farmer, Farm, Loan, CropHealth, RiskScore, Alert, FinancialSnapshot
from app.utils.geojson import make_polygon

PROVINCES = [
    ("Battambang", ["Battambang", "Thma Koul", "Moung Ruessei"]),
    ("Siem Reap", ["Siem Reap", "Srei Snam", "Chi Kreng"]),
    ("Kampong Cham", ["Kampong Cham", "Kampong Siem", "Prey Chhor"]),
]

RMs = [
    "Sovannara", "Dara", "Chantrea", "Bopha", "Vannak",
    "Srey Touch", "Makara", "Rathana", "Chamroeun", "Kosal",
]


def seed_data():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    farmers = []
    farms = []
    loans = []
    all_risk_scores = []

    farmer_idx = 0
    for prov, districts in PROVINCES:
        n = random.randint(45, 60)
        for _ in range(n):
            farmer_idx += 1
            farmer_code = f"F{farmer_idx:04d}"
            district = random.choice(districts)
            lat = round(random.uniform(11.5, 14.5), 4)
            lon = round(random.uniform(103.0, 106.5), 4)

            farmer = Farmer(
                farmer_code=farmer_code,
                name=f"Farmer {farmer_code}",
                phone=f"012{random.randint(1000000, 9999999)}",
                province=prov,
                district=district,
                commune=f"Commune {random.randint(1, 20)}",
                village=f"Village {random.randint(1, 30)}",
            )
            db.add(farmer)
            db.flush()

            area = round(random.uniform(1.0, 8.0), 2)
            area_sat = round(area * random.uniform(0.88, 1.12), 2)
            planting = date(2026, 6, 1) + timedelta(days=random.randint(0, 30))
            harvest = planting + timedelta(days=random.randint(100, 140))

            farm = Farm(
                farm_code=f"FARM-{farmer_code}",
                farmer_id=farmer.id,
                centroid_lat=lat,
                centroid_lon=lon,
                boundary_geojson=make_polygon(lat, lon, area),
                area_hectares=area,
                area_satellite=area_sat,
                crop_type="rice",
                planting_date=planting,
                expected_harvest=harvest,
                season="wet",
            )
            db.add(farm)
            db.flush()

            outstanding = round(random.uniform(1000, 15000), 2)
            installment = round(outstanding / random.randint(6, 24), 2)
            dpd = random.choices(
                [0, 0, 0, 0, 0, 5, 15, 30, 60],
                weights=[50, 10, 10, 10, 5, 5, 5, 3, 2],
            )[0]
            missed = random.choices(
                [0, 0, 0, 0, 1, 2],
                weights=[40, 20, 15, 10, 10, 5],
            )[0]

            loan = Loan(
                loan_code=f"AGR-2026-{farmer_idx:05d}",
                farmer_id=farmer.id,
                outstanding_principal=outstanding,
                monthly_installment=installment,
                disbursement_date=date(2026, 3, 1) + timedelta(days=random.randint(0, 90)),
                maturity_date=date(2027, 3, 1),
                interest_rate=round(random.uniform(8.0, 14.0), 1),
                dpd=dpd,
                dpd_max_90d=max(dpd, random.randint(0, 30)),
                missed_payments_count=missed,
                restructured=random.random() < 0.05,
            )
            db.add(loan)
            db.flush()

            farmers.append(farmer)
            farms.append(farm)
            loans.append(loan)

            # Crop health time-series (90 days, every 5 days)
            risk_level = random.choices(
                ["normal", "watch", "high", "critical"],
                weights=[45, 25, 20, 10],
            )[0]

            base_ndvi = {"normal": 0.72, "watch": 0.60, "high": 0.45, "critical": 0.32}[risk_level]
            base_health = {"normal": 88, "watch": 68, "high": 52, "critical": 35}[risk_level]

            for day_offset in range(0, 90, 5):
                obs_date = date(2026, 9, 10) - timedelta(days=day_offset)
                ndvi = round(base_ndvi + random.uniform(-0.08, 0.08), 3)
                ndvi_hist = round(base_ndvi + 0.12 + random.uniform(-0.05, 0.05), 3)
                dev = round((ndvi - ndvi_hist) / ndvi_hist * 100, 1) if ndvi_hist > 0 else 0
                ndwi = round(random.uniform(-0.1, 0.3), 3)
                rain = round(random.uniform(0, 250), 1)
                rain_dev = round((rain - 145.0) / 145.0 * 100, 1)
                score = max(0, min(100, int(base_health + random.uniform(-8, 8))))
                status = (
                    "green" if score >= 80 else
                    "yellow" if score >= 60 else
                    "orange" if score >= 40 else "red"
                )

                db.add(CropHealth(
                    farm_id=farm.id,
                    observation_date=obs_date,
                    ndvi_current=ndvi,
                    ndvi_historical=ndvi_hist,
                    ndvi_deviation_pct=dev,
                    ndvi_trend=random.choice(["improving", "stable", "declining"]),
                    ndwi_current=ndwi,
                    growth_stage=random.choice(["vegetative", "reproductive", "maturity"]),
                    flood_exposure=random.random() < 0.08,
                    drought_stress=random.random() < 0.15,
                    rainfall_30d=rain,
                    rainfall_deviation_30d=rain_dev,
                    temperature_stress_days=random.randint(0, 5),
                    sar_vh_backscatter=round(random.uniform(-15, -5), 1),
                    crop_health_score=score,
                    status=status,
                    confidence=round(random.uniform(0.78, 0.95), 2),
                ))

            # Risk score
            risk_prob = {
                "normal": round(random.uniform(0.05, 0.25), 2),
                "watch": round(random.uniform(0.30, 0.50), 2),
                "high": round(random.uniform(0.55, 0.75), 2),
                "critical": round(random.uniform(0.76, 0.95), 2),
            }[risk_level]
            bucket = (
                "GREEN" if risk_prob <= 0.30 else
                "AMBER" if risk_prob <= 0.55 else
                "ORANGE" if risk_prob <= 0.75 else "RED"
            )
            drivers = [
                {"feature": "ndvi_deviation_pct", "value": round(-random.uniform(5, 40), 1), "contribution": round(random.uniform(0.05, 0.20), 2)},
                {"feature": "rainfall_deviation_30d", "value": round(-random.uniform(10, 60), 1), "contribution": round(random.uniform(0.03, 0.15), 2)},
                {"feature": "crop_health_score", "value": score, "contribution": round(random.uniform(0.02, 0.12), 2)},
            ]
            rs = RiskScore(
                farm_id=farm.id,
                farmer_id=farmer.id,
                loan_id=loan.id,
                scoring_date=date(2026, 9, 10),
                risk_probability=risk_prob,
                risk_bucket=bucket,
                confidence=round(random.uniform(0.75, 0.92), 2),
                primary_drivers_json=json.dumps(drivers),
                recommended_action=(
                    "RM_REVIEW" if bucket in ("ORANGE", "RED")
                    else "MONITOR" if bucket == "AMBER"
                    else "NORMAL"
                ),
            )
            db.add(rs)
            all_risk_scores.append((rs, farm, risk_level))

    # Alerts
    alert_counter = 0
    for rs, farm, risk_level in all_risk_scores:
        if risk_level in ("high", "critical"):
            alert_counter += 1
            sev = "HIGH" if risk_level == "high" else "CRITICAL"
            alert_type = random.choice(["crop_stress", "drought", "flood", "risk_escalation"])
            titles = {
                "crop_stress": "Significant crop stress detected",
                "drought": "Drought conditions affecting farm",
                "flood": "Flood exposure detected",
                "risk_escalation": "Risk score escalated to action level",
            }
            descriptions = {
                "crop_stress": f"NDVI deviation of {random.randint(-35, -15)}% detected. Crop health score below threshold.",
                "drought": f"30-day rainfall deficit of {random.randint(30, 60)}%. Drought stress indicators active.",
                "flood": "Farm area shows SAR flood signatures. Immediate assessment recommended.",
                "risk_escalation": f"Risk probability increased to {rs.risk_probability:.0%}. Multiple factors contributing.",
            }
            db.add(Alert(
                alert_code=f"ALT-2026-{alert_counter:06d}",
                farm_id=farm.id,
                risk_score_id=rs.id,
                alert_type=alert_type,
                severity=sev,
                title=titles[alert_type],
                description=descriptions[alert_type],
                risk_score_value=rs.risk_probability,
                status=random.choice(["open", "open", "acknowledged"]),
                assigned_to=random.choice(RMs),
            ))

    # Financial snapshots
    for farmer in farmers:
        for days_ago in [30, 60]:
            db.add(FinancialSnapshot(
                farmer_id=farmer.id,
                snapshot_date=date(2026, 9, 10) - timedelta(days=days_ago),
                deposit_balance_avg_30d=round(random.uniform(50, 2000), 2),
                deposit_balance_avg_60d=round(random.uniform(50, 2000), 2),
                deposit_balance_trend_30d=round(random.uniform(-0.4, 0.3), 2),
                deposit_balance_trend_60d=round(random.uniform(-0.3, 0.3), 2),
                transaction_count_30d=random.randint(2, 40),
                cash_inflow_30d=round(random.uniform(100, 5000), 2),
                cash_outflow_30d=round(random.uniform(100, 4000), 2),
                cash_inflow_30d_60d_ratio=round(random.uniform(0.5, 1.3), 2),
                cash_outflow_30d_60d_ratio=round(random.uniform(0.5, 1.3), 2),
                days_since_last_deposit=random.randint(0, 45),
                balance_to_installment_ratio=round(random.uniform(0.2, 5.0), 2),
                agricultural_income_detected=random.random() < 0.7,
            ))

    db.commit()
    print(f"Seeded: {len(farmers)} farmers, {len(farms)} farms, {len(loans)} loans, {alert_counter} alerts")
    db.close()


if __name__ == "__main__":
    seed_data()
