import { useEffect, useState } from "react";
import { MapContainer, TileLayer, GeoJSON, useMap } from "react-leaflet";
import { useNavigate } from "react-router-dom";
import { api } from "../api";
import type { GeoJSONFeatureCollection } from "../types";
import "leaflet/dist/leaflet.css";

const RISK_COLORS: Record<string, string> = {
  GREEN: "#22c55e",
  AMBER: "#f59e0b",
  ORANGE: "#f97316",
  RED: "#ef4444",
  UNKNOWN: "#6b7280",
};

function MapUpdater({ center }: { center: [number, number] }) {
  const map = useMap();
  useEffect(() => {
    map.setView(center, 7);
  }, [center, map]);
  return null;
}

export default function MapView() {
  const [geojson, setGeojson] = useState<GeoJSONFeatureCollection | null>(null);
  const [province, setProvince] = useState("");
  const [summary, setSummary] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    api.getPortfolioSummary().then(setSummary);
  }, []);

  useEffect(() => {
    setLoading(true);
    api.getAllFarmsGeoJSON(province || undefined).then((data) => {
      setGeojson(data);
      setLoading(false);
    });
  }, [province]);

  const provinces = summary?.provinces?.map((p: any) => p.province) || [];
  const center: [number, number] = [12.5, 105.0];

  return (
    <div>
      <div className="page-header">
        <h1>Farm Map View</h1>
        <p>Interactive map showing farm boundaries color-coded by risk level</p>
      </div>

      <div className="filter-bar">
        <select value={province} onChange={(e) => setProvince(e.target.value)}>
          <option value="">All Provinces</option>
          {provinces.map((p: string) => (
            <option key={p} value={p}>{p}</option>
          ))}
        </select>
        <div style={{ display: "flex", gap: 16, alignItems: "center", marginLeft: 16 }}>
          {Object.entries(RISK_COLORS).filter(([k]) => k !== "UNKNOWN").map(([bucket, color]) => (
            <div key={bucket} style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 12, color: "var(--text-secondary)" }}>
              <div style={{ width: 12, height: 12, borderRadius: 3, background: color }} />
              {bucket}
            </div>
          ))}
        </div>
      </div>

      {loading ? (
        <div className="loading">Loading map data...</div>
      ) : (
        <div className="map-container">
          <MapContainer center={center} zoom={7} style={{ height: "100%", width: "100%" }}>
            <TileLayer
              attribution='&copy; <a href="https://carto.com/">CARTO</a>'
              url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
            />
            <MapUpdater center={center} />
            {geojson && (
              <GeoJSON
                key={JSON.stringify(geojson.features.length)}
                data={geojson as any}
                style={(feature) => {
                  const bucket = feature?.properties?.risk_bucket || "UNKNOWN";
                  return {
                    color: RISK_COLORS[bucket] || RISK_COLORS.UNKNOWN,
                    weight: 2,
                    opacity: 0.8,
                    fillColor: RISK_COLORS[bucket] || RISK_COLORS.UNKNOWN,
                    fillOpacity: 0.25,
                  };
                }}
                onEachFeature={(feature, layer) => {
                  const p = feature.properties;
                  layer.bindPopup(`
                    <div style="font-family: sans-serif; font-size: 13px;">
                      <strong>${p.farm_id}</strong><br/>
                      ${p.farmer_name || ""}<br/>
                      Area: ${p.area_hectares} ha<br/>
                      Risk: <strong>${p.risk_bucket}</strong> (${(p.risk_probability * 100).toFixed(1)}%)<br/>
                      Health Score: ${p.crop_health_score ?? "N/A"}<br/>
                      <a href="#" onclick="window.__nav && window.__nav('/farmers/${p.farmer_id}')">View Details →</a>
                    </div>
                  `);
                  layer.on("click", () => {
                    navigate(`/farmers/${p.farmer_id}`);
                  });
                }}
              />
            )}
          </MapContainer>
        </div>
      )}

      {geojson && (
        <div style={{ marginTop: 12, fontSize: 13, color: "var(--text-muted)" }}>
          Showing {geojson.features.length} farms
        </div>
      )}
    </div>
  );
}
