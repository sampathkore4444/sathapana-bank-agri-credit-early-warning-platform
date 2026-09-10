const BASE = "http://localhost:8000/api";

function getToken(): string | null {
  return localStorage.getItem("sarp_token");
}

function setToken(token: string) {
  localStorage.setItem("sarp_token", token);
}

function clearToken() {
  localStorage.removeItem("sarp_token");
  localStorage.removeItem("sarp_user");
}

function authHeaders(): Record<string, string> {
  const token = getToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function fetchJSON<T>(url: string): Promise<T> {
  const res = await fetch(url, { headers: authHeaders() });
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

async function postJSON<T>(url: string, body?: any): Promise<T> {
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeaders() },
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

async function patchJSON<T>(url: string, body?: any): Promise<T> {
  const res = await fetch(url, {
    method: "PATCH",
    headers: { "Content-Type": "application/json", ...authHeaders() },
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

import type {
  Farmer,
  Farm,
  Loan,
  CropHealthRecord,
  RiskScore,
  RiskScoreDetail,
  Alert,
  PortfolioSummary,
  EarlyWarning,
  DashboardStats,
  GeoJSONFeatureCollection,
} from "./types";

export const api = {
  // Farmers
  getFarmers: (province?: string) =>
    fetchJSON<Farmer[]>(`${BASE}/farmers${province ? `?province=${province}` : ""}`),
  getFarmer: (id: number) =>
    fetchJSON<Farmer>(`${BASE}/farmers/${id}`),

  // Farms
  getFarms: () => fetchJSON<Farm[]>(`${BASE}/farms`),
  getFarm: (id: number) => fetchJSON<Farm>(`${BASE}/farms/${id}`),
  getAllFarmsGeoJSON: (province?: string) =>
    fetchJSON<GeoJSONFeatureCollection>(
      `${BASE}/farms/geojson/all${province ? `?province=${province}` : ""}`
    ),

  // Loans
  getLoans: (farmerId?: number) =>
    fetchJSON<Loan[]>(`${BASE}/loans${farmerId ? `?farmer_id=${farmerId}` : ""}`),
  getLoan: (id: number) => fetchJSON<Loan>(`${BASE}/loans/${id}`),

  // Crop Health
  getCropHealth: (farmId: number, days = 90) =>
    fetchJSON<CropHealthRecord[]>(`${BASE}/crop-health/${farmId}?days=${days}`),
  getLatestCropHealth: (farmId: number) =>
    fetchJSON<CropHealthRecord>(`${BASE}/crop-health/${farmId}/latest`),

  // Risk Scores
  getRiskScores: (bucket?: string) =>
    fetchJSON<RiskScore[]>(`${BASE}/risk-scores${bucket ? `?bucket=${bucket}` : ""}`),
  getFarmerRisk: (farmerId: number) =>
    fetchJSON<RiskScoreDetail>(`${BASE}/risk-scores/${farmerId}`),

  // Alerts
  getAlerts: (status?: string, severity?: string) => {
    const params = new URLSearchParams();
    if (status) params.set("status", status);
    if (severity) params.set("severity", severity);
    return fetchJSON<Alert[]>(`${BASE}/alerts?${params.toString()}`);
  },
  acknowledgeAlert: (id: number) =>
    patchJSON(`${BASE}/alerts/${id}/acknowledge`),
  resolveAlert: (id: number, action?: string) =>
    patchJSON(`${BASE}/alerts/${id}/resolve?action_taken=${action || "No action needed"}`),
  dismissAlert: (id: number, reason?: string) =>
    patchJSON(`${BASE}/alerts/${id}/dismiss?reason=${reason || ""}`),

  // Dashboard
  getPortfolioSummary: () => fetchJSON<PortfolioSummary>(`${BASE}/dashboard/summary`),
  getEarlyWarnings: (limit = 20) =>
    fetchJSON<EarlyWarning[]>(`${BASE}/dashboard/early-warnings?limit=${limit}`),
  getDashboardStats: () => fetchJSON<DashboardStats>(`${BASE}/dashboard/stats`),

  // Auth
  login: (username: string, password: string) =>
    postJSON<{ access_token: string; user: any }>(`${BASE}/auth/login`, { username, password }),
  getMe: () => fetchJSON<any>(`${BASE}/auth/me`),
  setAuthToken: setToken,
  clearAuthToken: clearToken,
  getToken: getToken,

  // ML Pipeline
  trainModel: () => postJSON<any>(`${BASE}/ml/train`),
  scoreAllFarmers: () => postJSON<any>(`${BASE}/ml/score-all`),
  scoreFarmer: (id: number) => fetchJSON<any>(`${BASE}/ml/score/${id}`),
  getModelMetrics: () => fetchJSON<any>(`${BASE}/ml/metrics`),
  getFarmerFeatures: (id: number) => fetchJSON<any>(`${BASE}/ml/features/${id}`),
  getGrowthCurve: (farmId: number) => fetchJSON<any>(`${BASE}/ml/growth-curve/${farmId}`),

  // Pilot
  assignPilotGroups: (ratio = 0.7) =>
    postJSON<any>(`${BASE}/pilot/assign?pilot_ratio=${ratio}`),
  getPilotGroups: () => fetchJSON<any>(`${BASE}/pilot/groups`),
  comparePilotOutcomes: () => fetchJSON<any>(`${BASE}/pilot/compare`),

  // KPIs
  getTechnicalKPIs: () => fetchJSON<any>(`${BASE}/kpi/technical`),
  getBusinessKPIs: () => fetchJSON<any>(`${BASE}/kpi/business`),

  // Scheduler
  getSchedulerJobs: () => fetchJSON<any>(`${BASE}/scheduler/jobs`),
  triggerJob: (jobId: string) => postJSON<any>(`${BASE}/scheduler/run/${jobId}`),
};
