import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { api } from "../api";
import type { Farmer, Farm, Loan, CropHealthRecord, RiskScoreDetail } from "../types";

function fmt(n: number) {
  return n.toLocaleString("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 });
}

function riskColor(bucket: string) {
  switch (bucket) {
    case "GREEN": return "green";
    case "AMBER": return "amber";
    case "ORANGE": return "orange";
    case "RED": return "red";
    default: return "amber";
  }
}

function scoreColor(score: number) {
  if (score >= 80) return "var(--green)";
  if (score >= 60) return "var(--amber)";
  if (score >= 40) return "var(--orange)";
  return "var(--red)";
}

function NdviChart({ records }: { records: CropHealthRecord[] }) {
  if (!records.length) return <div className="chart-placeholder">No NDVI data</div>;
  const width = 700;
  const height = 200;
  const pad = { top: 20, right: 20, bottom: 30, left: 40 };
  const plotW = width - pad.left - pad.right;
  const plotH = height - pad.top - pad.bottom;

  const minVal = Math.min(...records.map((r) => r.ndvi_current), ...records.map((r) => r.ndvi_historical)) - 0.05;
  const maxVal = Math.max(...records.map((r) => r.ndvi_current), ...records.map((r) => r.ndvi_historical)) + 0.05;

  const x = (i: number) => pad.left + (i / (records.length - 1)) * plotW;
  const y = (v: number) => pad.top + (1 - (v - minVal) / (maxVal - minVal)) * plotH;

  const currentPath = records.map((r, i) => `${i === 0 ? "M" : "L"}${x(i)},${y(r.ndvi_current)}`).join(" ");
  const histPath = records.map((r, i) => `${i === 0 ? "M" : "L"}${x(i)},${y(r.ndvi_historical)}`).join(" ");

  return (
    <div className="ndvi-chart">
      <svg viewBox={`0 0 ${width} ${height}`}>
        {/* Grid lines */}
        {[0.3, 0.5, 0.7, 0.9].map((v) => (
          <g key={v}>
            <line x1={pad.left} y1={y(v)} x2={width - pad.right} y2={y(v)} stroke="var(--border)" strokeDasharray="4 4" />
            <text x={pad.left - 6} y={y(v) + 4} textAnchor="end" fill="var(--text-muted)" fontSize="10">{v.toFixed(1)}</text>
          </g>
        ))}
        {/* Historical NDVI */}
        <path d={histPath} fill="none" stroke="var(--text-muted)" strokeWidth="1.5" strokeDasharray="6 3" opacity="0.6" />
        {/* Current NDVI */}
        <path d={currentPath} fill="none" stroke="var(--accent)" strokeWidth="2" />
        {/* Data points */}
        {records.map((r, i) => (
          <circle key={i} cx={x(i)} cy={y(r.ndvi_current)} r="3" fill="var(--accent)" />
        ))}
        {/* Legend */}
        <line x1={width - 180} y1={12} x2={width - 160} y2={12} stroke="var(--accent)" strokeWidth="2" />
        <text x={width - 155} y={16} fill="var(--text-secondary)" fontSize="10">Current NDVI</text>
        <line x1={width - 90} y1={12} x2={width - 70} y2={12} stroke="var(--text-muted)" strokeWidth="1.5" strokeDasharray="4 3" />
        <text x={width - 65} y={16} fill="var(--text-muted)" fontSize="10">Historical</text>
      </svg>
    </div>
  );
}

export default function FarmerDetail() {
  const { farmerId } = useParams();
  const navigate = useNavigate();
  const [farmer, setFarmer] = useState<Farmer | null>(null);
  const [farm, setFarm] = useState<Farm | null>(null);
  const [loans, setLoans] = useState<Loan[]>([]);
  const [cropHealth, setCropHealth] = useState<CropHealthRecord[]>([]);
  const [latestHealth, setLatestHealth] = useState<CropHealthRecord | null>(null);
  const [risk, setRisk] = useState<RiskScoreDetail | null>(null);
  const [loading, setLoading] = useState(true);

  const id = parseInt(farmerId || "0");

  useEffect(() => {
    if (!id) return;
    Promise.all([
      api.getFarmer(id),
      api.getLoans(id),
      api.getFarmerRisk(id).catch(() => null),
    ]).then(([f, l, r]) => {
      setFarmer(f);
      setLoans(l);
      setRisk(r);
      // Get farm
      if (l.length > 0) {
        api.getFarms().then((farms) => {
          const farmMatch = farms.find((fm) => fm.farmer_id === f.id);
          if (farmMatch) {
            setFarm(farmMatch);
            api.getCropHealth(farmMatch.id).then(setCropHealth);
            api.getLatestCropHealth(farmMatch.id).then(setLatestHealth).catch(() => {});
          }
          setLoading(false);
        });
      } else {
        setLoading(false);
      }
    });
  }, [id]);

  if (loading) return <div className="loading">Loading farmer details...</div>;
  if (!farmer) return <div className="loading">Farmer not found</div>;

  const latestLoan = loans[0];
  const drivers = risk?.primary_drivers || [];

  return (
    <div>
      <div className="page-header">
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <button className="btn" onClick={() => navigate(-1)}>← Back</button>
          <div>
            <h1>{farmer.farmer_code} — {farmer.name}</h1>
            <p>{farmer.province} · {farmer.district}</p>
          </div>
        </div>
      </div>

      <div className="stat-grid">
        {latestHealth && (
          <>
            <div className="stat-card">
              <div className="label">Crop Health Score</div>
              <div className="value" style={{ color: scoreColor(latestHealth.crop_health_score) }}>
                {latestHealth.crop_health_score}
              </div>
              <div className="sub">Status: {latestHealth.status.toUpperCase()}</div>
            </div>
            <div className="stat-card">
              <div className="label">NDVI Current</div>
              <div className="value">{latestHealth.ndvi_current.toFixed(3)}</div>
              <div className="sub">
                Deviation: <span style={{ color: latestHealth.ndvi_deviation_pct < -20 ? "var(--red)" : "var(--text-secondary)" }}>
                  {latestHealth.ndvi_deviation_pct.toFixed(1)}%
                </span>
              </div>
            </div>
          </>
        )}
        {risk && (
          <div className={`stat-card ${riskColor(risk.risk_bucket).toLowerCase()}`}>
            <div className="label">Repayment Risk</div>
            <div className="value">{(risk.risk_probability * 100).toFixed(1)}%</div>
            <div className="sub">
              Bucket: <span className={`badge badge-${riskColor(risk.risk_bucket)}`}>{risk.risk_bucket}</span>
            </div>
          </div>
        )}
        {latestLoan && (
          <div className="stat-card">
            <div className="label">Loan Outstanding</div>
            <div className="value">{fmt(latestLoan.outstanding_principal)}</div>
            <div className="sub">
              DPD: <span style={{ color: latestLoan.dpd > 0 ? "var(--red)" : "var(--text-secondary)" }}>
                {latestLoan.dpd}
              </span>
              · Installment: {fmt(latestLoan.monthly_installment)}
            </div>
          </div>
        )}
      </div>

      <div className="detail-grid">
        {/* Left Column */}
        <div>
          {/* NDVI Time Series */}
          <div className="card">
            <div className="card-header">
              <h2>📈 NDVI Time Series (90 days)</h2>
            </div>
            <NdviChart records={cropHealth} />
          </div>

          {/* Crop Health Details */}
          {latestHealth && (
            <div className="card">
              <div className="card-header">
                <h2>🌱 Current Crop Health</h2>
              </div>
              <div className="two-col">
                <div>
                  <div className="detail-field">
                    <div className="label">Growth Stage</div>
                    <div className="value" style={{ textTransform: "capitalize" }}>{latestHealth.growth_stage}</div>
                  </div>
                  <div className="detail-field">
                    <div className="label">NDWI (Moisture)</div>
                    <div className="value">{latestHealth.ndwi_current.toFixed(3)}</div>
                  </div>
                  <div className="detail-field">
                    <div className="label">Rainfall (30d)</div>
                    <div className="value">{latestHealth.rainfall_30d}mm</div>
                    <div className="sub">
                      Deviation: {latestHealth.rainfall_deviation_30d.toFixed(1)}%
                    </div>
                  </div>
                </div>
                <div>
                  <div className="detail-field">
                    <div className="label">Flood Exposure</div>
                    <div className="value" style={{ color: latestHealth.flood_exposure ? "var(--red)" : "var(--green)" }}>
                      {latestHealth.flood_exposure ? "⚠️ Yes" : "✅ No"}
                    </div>
                  </div>
                  <div className="detail-field">
                    <div className="label">Drought Stress</div>
                    <div className="value" style={{ color: latestHealth.drought_stress ? "var(--red)" : "var(--green)" }}>
                      {latestHealth.drought_stress ? "⚠️ Yes" : "✅ No"}
                    </div>
                  </div>
                  <div className="detail-field">
                    <div className="label">SAR Backscatter</div>
                    <div className="value">{latestHealth.sar_vh_backscatter} dB</div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Right Column */}
        <div>
          {/* Farm Info */}
          {farm && (
            <div className="card">
              <div className="card-header">
                <h2>🏡 Farm Profile</h2>
              </div>
              <div className="detail-field">
                <div className="label">Farm Code</div>
                <div className="value">{farm.farm_code}</div>
              </div>
              <div className="detail-field">
                <div className="label">Crop Type</div>
                <div className="value" style={{ textTransform: "capitalize" }}>{farm.crop_type}</div>
              </div>
              <div className="detail-field">
                <div className="label">Area</div>
                <div className="value">{farm.area_hectares} ha (GPS) / {farm.area_satellite} ha (satellite)</div>
              </div>
              <div className="detail-field">
                <div className="label">Planting Date</div>
                <div className="value">{farm.planting_date || "—"}</div>
              </div>
              <div className="detail-field">
                <div className="label">Expected Harvest</div>
                <div className="value">{farm.expected_harvest || "—"}</div>
              </div>
              <div className="detail-field">
                <div className="label">Location</div>
                <div className="value">{farm.centroid_lat.toFixed(4)}, {farm.centroid_lon.toFixed(4)}</div>
              </div>
            </div>
          )}

          {/* Risk Drivers */}
          {drivers.length > 0 && (
            <div className="card">
              <div className="card-header">
                <h2>🔍 Risk Drivers (SHAP)</h2>
              </div>
              <ul className="driver-list">
                {drivers.map((d, i) => (
                  <li key={i}>
                    <span className="driver-name">{d.feature}</span>
                    <span>
                      <span style={{ color: "var(--text-muted)", marginRight: 8 }}>
                        {typeof d.value === "number" ? d.value.toFixed(1) : d.value}
                      </span>
                      <span className="driver-contribution">+{(d.contribution * 100).toFixed(1)}%</span>
                    </span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* RM Actions */}
          {risk && (
            <div className="card">
              <div className="card-header">
                <h2>📞 Recommended Action</h2>
              </div>
              <div className="detail-field">
                <div className="value" style={{
                  color: risk.recommended_action === "RM_REVIEW" ? "var(--red)" :
                         risk.recommended_action === "MONITOR" ? "var(--amber)" : "var(--green)",
                  fontWeight: 600,
                }}>
                  {risk.recommended_action === "RM_REVIEW" ? "🔴 RM to contact farmer" :
                   risk.recommended_action === "MONITOR" ? "🟡 Enhanced monitoring" :
                   "🟢 Normal monitoring"}
                </div>
              </div>
              <div style={{ marginTop: 12, display: "flex", gap: 8 }}>
                <button className="btn btn-primary">Contact Farmer</button>
                <button className="btn">View on Map</button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
