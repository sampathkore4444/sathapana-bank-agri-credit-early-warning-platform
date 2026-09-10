import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api";
import type { Farmer, PortfolioSummary, RiskScore } from "../types";

export default function Farmers() {
  const [farmers, setFarmers] = useState<Farmer[]>([]);
  const [riskMap, setRiskMap] = useState<Record<number, RiskScore>>({});
  const [search, setSearch] = useState("");
  const [province, setProvince] = useState("");
  const [summary, setSummary] = useState<PortfolioSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    api.getPortfolioSummary().then(setSummary);
  }, []);

  useEffect(() => {
    setLoading(true);
    api.getFarmers(province || undefined).then((f) => {
      setFarmers(f);
      // Fetch risk scores for each farmer
      const promises = f.map((farmer) =>
        api.getFarmerRisk(farmer.id).catch(() => null)
      );
      Promise.all(promises).then((scores) => {
        const map: Record<number, RiskScore> = {};
        scores.forEach((s) => {
          if (s) map[s.farmer_id] = s;
        });
        setRiskMap(map);
        setLoading(false);
      });
    });
  }, [province]);

  const provinces = summary?.provinces.map((p) => p.province) || [];

  const filtered = farmers.filter((f) => {
    if (!search) return true;
    const q = search.toLowerCase();
    return (
      f.farmer_code.toLowerCase().includes(q) ||
      f.name.toLowerCase().includes(q) ||
      f.district.toLowerCase().includes(q)
    );
  });

  function riskColor(bucket: string) {
    switch (bucket) {
      case "GREEN": return "green";
      case "AMBER": return "amber";
      case "ORANGE": return "orange";
      case "RED": return "red";
      default: return "amber";
    }
  }

  return (
    <div>
      <div className="page-header">
        <h1>Farmers</h1>
        <p>{filtered.length} farmers in pilot program</p>
      </div>

      <div className="filter-bar">
        <input
          type="text"
          placeholder="Search by code, name, district..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <select value={province} onChange={(e) => setProvince(e.target.value)}>
          <option value="">All Provinces</option>
          {provinces.map((p) => (
            <option key={p} value={p}>{p}</option>
          ))}
        </select>
      </div>

      {loading ? (
        <div className="loading">Loading farmers...</div>
      ) : (
        <div className="card">
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Code</th>
                  <th>Name</th>
                  <th>Province</th>
                  <th>District</th>
                  <th>Risk Bucket</th>
                  <th>Risk Score</th>
                  <th>Confidence</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((f) => {
                  const rs = riskMap[f.id];
                  return (
                    <tr key={f.id} style={{ cursor: "pointer" }} onClick={() => navigate(`/farmers/${f.id}`)}>
                      <td style={{ color: "var(--text-primary)", fontWeight: 500 }}>{f.farmer_code}</td>
                      <td>{f.name}</td>
                      <td>{f.province}</td>
                      <td>{f.district}</td>
                      <td>
                        {rs ? (
                          <span className={`badge badge-${riskColor(rs.risk_bucket)}`}>{rs.risk_bucket}</span>
                        ) : (
                          <span className="badge badge-amber">N/A</span>
                        )}
                      </td>
                      <td>
                        {rs ? `${(rs.risk_probability * 100).toFixed(1)}%` : "—"}
                      </td>
                      <td>{rs ? `${(rs.confidence * 100).toFixed(0)}%` : "—"}</td>
                      <td style={{ color: "var(--accent)", fontSize: 12 }}>View →</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
