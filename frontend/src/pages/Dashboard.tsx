import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api";
import type { PortfolioSummary, EarlyWarning, DashboardStats } from "../types";

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

export default function Dashboard() {
  const [summary, setSummary] = useState<PortfolioSummary | null>(null);
  const [warnings, setWarnings] = useState<EarlyWarning[]>([]);
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    Promise.all([
      api.getPortfolioSummary(),
      api.getEarlyWarnings(15),
      api.getDashboardStats(),
    ]).then(([s, w, st]) => {
      setSummary(s);
      setWarnings(w);
      setStats(st);
      setLoading(false);
    });
  }, []);

  if (loading) return <div className="loading">Loading dashboard...</div>;
  if (!summary) return <div className="loading">Failed to load data</div>;

  return (
    <div>
      <div className="page-header">
        <h1>Agricultural Credit Monitor</h1>
        <p>Sathapana Agricultural Risk Platform — Portfolio Overview</p>
      </div>

      {/* Summary Stats */}
      <div className="stat-grid">
        <div className="stat-card">
          <div className="label">Total Farmers</div>
          <div className="value">{summary.total_farmers}</div>
          <div className="sub">In pilot program</div>
        </div>
        <div className="stat-card">
          <div className="label">Outstanding</div>
          <div className="value">{fmt(summary.total_outstanding)}</div>
          <div className="sub">Agricultural portfolio</div>
        </div>
        <div className="stat-card green">
          <div className="label">🟢 Normal</div>
          <div className="value">{summary.green_count}</div>
          <div className="sub">{((summary.green_count / summary.total_farmers) * 100).toFixed(1)}% of portfolio</div>
        </div>
        <div className="stat-card amber">
          <div className="label">🟡 Watch</div>
          <div className="value">{summary.amber_count}</div>
          <div className="sub">Enhanced monitoring</div>
        </div>
        <div className="stat-card orange">
          <div className="label">🟠 High Risk</div>
          <div className="value">{summary.orange_count}</div>
          <div className="sub">RM contact needed</div>
        </div>
        <div className="stat-card red">
          <div className="label">🔴 Critical</div>
          <div className="value">{summary.red_count}</div>
          <div className="sub">Urgent intervention</div>
        </div>
      </div>

      <div className="two-col">
        {/* Province Breakdown */}
        <div className="card">
          <div className="card-header">
            <h2>Province Breakdown</h2>
          </div>
          <div className="province-grid">
            {summary.provinces.map((p) => (
              <div className="province-row" key={p.province}>
                <div>
                  <div className="province-name">{p.province}</div>
                  <div style={{ fontSize: 11, color: "var(--text-muted)", marginTop: 2 }}>
                    {fmt(p.total_outstanding)}
                  </div>
                </div>
                <div className="province-buckets">
                  <span style={{ color: "var(--green)" }}>🟢 {p.green}</span>
                  <span style={{ color: "var(--amber)" }}>🟡 {p.amber}</span>
                  <span style={{ color: "var(--orange)" }}>🟠 {p.orange}</span>
                  <span style={{ color: "var(--red)" }}>🔴 {p.red}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Quick Stats */}
        <div className="card">
          <div className="card-header">
            <h2>Risk Summary</h2>
          </div>
          {stats && (
            <div>
              <div className="detail-field">
                <div className="label">Average Risk Score</div>
                <div className="value">{(stats.average_risk_score * 100).toFixed(1)}%</div>
              </div>
              <div className="detail-field">
                <div className="label">Total Alerts</div>
                <div className="value">{stats.total_alerts}</div>
                <div className="sub">
                  <span style={{ color: "var(--red)" }}>{stats.open_alerts} open</span> ·{" "}
                  <span style={{ color: "var(--amber)" }}>{stats.acknowledged_alerts} ack'd</span> ·{" "}
                  <span style={{ color: "var(--green)" }}>{stats.resolved_alerts} resolved</span>
                </div>
              </div>
              <div className="detail-field">
                <div className="label">DPD Rate</div>
                <div className="value">{stats.dpd_rate}%</div>
                <div className="sub">{stats.loans_with_dpd} of {stats.total_loans} loans past due</div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Early Warning List */}
      <div className="card">
        <div className="card-header">
          <h2>⚠️ Top Early-Warning Borrowers</h2>
        </div>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Farmer</th>
                <th>Province</th>
                <th>Risk</th>
                <th>Confidence</th>
                <th>Outstanding</th>
                <th>DPD</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {warnings.map((w) => (
                <tr
                  key={w.farmer_id}
                  style={{ cursor: "pointer" }}
                  onClick={() => navigate(`/farmers/${w.farmer_id.replace("F", "")}`)}
                >
                  <td style={{ color: "var(--text-primary)", fontWeight: 500 }}>
                    {w.farmer_id} — {w.farmer_name}
                  </td>
                  <td>{w.province}</td>
                  <td>
                    <span className={`badge badge-${riskColor(w.risk_bucket)}`}>
                      {w.risk_bucket} {(w.risk_probability * 100).toFixed(0)}%
                    </span>
                  </td>
                  <td>{(w.confidence * 100).toFixed(0)}%</td>
                  <td>{fmt(w.outstanding)}</td>
                  <td style={{ color: w.dpd > 0 ? "var(--red)" : "var(--text-secondary)" }}>
                    {w.dpd}
                  </td>
                  <td style={{ fontSize: 11 }}>{w.recommended_action}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
