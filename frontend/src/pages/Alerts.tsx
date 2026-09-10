import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api";
import type { Alert } from "../types";

function fmtDate(s: string) {
  return new Date(s).toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });
}

function severityBadge(s: string) {
  switch (s) {
    case "CRITICAL": return "badge-red";
    case "HIGH": return "badge-orange";
    case "MEDIUM": return "badge-amber";
    default: return "badge-green";
  }
}

function statusBadge(s: string) {
  switch (s) {
    case "open": return "badge-open";
    case "acknowledged": return "badge-acknowledged";
    case "resolved": return "badge-resolved";
    case "dismissed": return "badge-dismissed";
    default: return "badge-amber";
  }
}

export default function Alerts() {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [filterStatus, setFilterStatus] = useState("");
  const [filterSeverity, setFilterSeverity] = useState("");
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  const loadAlerts = () => {
    setLoading(true);
    api.getAlerts(filterStatus || undefined, filterSeverity || undefined).then((data) => {
      setAlerts(data);
      setLoading(false);
    });
  };

  useEffect(() => {
    loadAlerts();
  }, [filterStatus, filterSeverity]);

  const handleAcknowledge = async (id: number) => {
    await api.acknowledgeAlert(id);
    loadAlerts();
  };

  const handleDismiss = async (id: number) => {
    await api.dismissAlert(id, "False positive — reviewed by RM");
    loadAlerts();
  };

  const handleResolve = async (id: number) => {
    await api.resolveAlert(id, "Farmer contacted, situation assessed");
    loadAlerts();
  };

  return (
    <div>
      <div className="page-header">
        <h1>🔔 Alert Management</h1>
        <p>Monitor and act on agricultural credit early warnings</p>
      </div>

      <div className="filter-bar">
        <select value={filterStatus} onChange={(e) => setFilterStatus(e.target.value)}>
          <option value="">All Statuses</option>
          <option value="open">Open</option>
          <option value="acknowledged">Acknowledged</option>
          <option value="resolved">Resolved</option>
          <option value="dismissed">Dismissed</option>
        </select>
        <select value={filterSeverity} onChange={(e) => setFilterSeverity(e.target.value)}>
          <option value="">All Severities</option>
          <option value="CRITICAL">Critical</option>
          <option value="HIGH">High</option>
          <option value="MEDIUM">Medium</option>
          <option value="LOW">Low</option>
        </select>
      </div>

      {loading ? (
        <div className="loading">Loading alerts...</div>
      ) : alerts.length === 0 ? (
        <div className="card">
          <div className="loading">No alerts matching filters</div>
        </div>
      ) : (
        <div className="card">
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Alert Code</th>
                  <th>Type</th>
                  <th>Severity</th>
                  <th>Title</th>
                  <th>Risk Score</th>
                  <th>Assigned To</th>
                  <th>Status</th>
                  <th>Created</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {alerts.map((a) => (
                  <tr key={a.id}>
                    <td style={{ color: "var(--text-primary)", fontWeight: 500 }}>{a.alert_code}</td>
                    <td style={{ textTransform: "capitalize" }}>{a.alert_type.replace(/_/g, " ")}</td>
                    <td>
                      <span className={`badge ${severityBadge(a.severity)}`}>{a.severity}</span>
                    </td>
                    <td>
                      <div>{a.title}</div>
                      <div style={{ fontSize: 11, color: "var(--text-muted)", maxWidth: 300, overflow: "hidden", textOverflow: "ellipsis" }}>
                        {a.description}
                      </div>
                    </td>
                    <td>
                      {a.risk_score_value != null
                        ? `${(a.risk_score_value * 100).toFixed(1)}%`
                        : "—"}
                    </td>
                    <td>{a.assigned_to || "—"}</td>
                    <td>
                      <span className={`badge ${statusBadge(a.status)}`}>{a.status}</span>
                    </td>
                    <td style={{ fontSize: 12 }}>{fmtDate(a.created_at)}</td>
                    <td>
                      <div className="alert-actions">
                        {a.status === "open" && (
                          <>
                            <button className="btn btn-primary" onClick={() => handleAcknowledge(a.id)}>
                              Acknowledge
                            </button>
                            <button className="btn" onClick={() => navigate(`/farmers/${a.farm_id}`)}>
                              View Farmer
                            </button>
                          </>
                        )}
                        {a.status === "acknowledged" && (
                          <>
                            <button className="btn btn-success" onClick={() => handleResolve(a.id)}>
                              Resolve
                            </button>
                            <button className="btn" onClick={() => handleDismiss(a.id)}>
                              Dismiss
                            </button>
                          </>
                        )}
                        {(a.status === "resolved" || a.status === "dismissed") && (
                          <span style={{ fontSize: 12, color: "var(--text-muted)" }}>
                            {a.action_taken || "Completed"}
                          </span>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
