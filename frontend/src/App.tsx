import { BrowserRouter, Routes, Route, NavLink, Navigate, useNavigate } from "react-router-dom";
import { api } from "./api";
import Dashboard from "./pages/Dashboard";
import Farmers from "./pages/Farmers";
import FarmerDetail from "./pages/FarmerDetail";
import MapView from "./pages/MapView";
import Alerts from "./pages/Alerts";
import Login from "./pages/Login";
import "./App.css";

function Sidebar() {
  const navigate = useNavigate();
  const user = JSON.parse(localStorage.getItem("sarp_user") || "{}") as any;

  const handleLogout = () => {
    api.clearAuthToken();
    navigate("/login");
  };

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <h2>🌾 SARP</h2>
        <p className="sidebar-subtitle">Agricultural Risk Platform</p>
      </div>
      <nav className="sidebar-nav">
        <NavLink to="/dashboard" className={({ isActive }) => isActive ? "nav-link active" : "nav-link"}>
          <span className="nav-icon">📊</span>
          Dashboard
        </NavLink>
        <NavLink to="/map" className={({ isActive }) => isActive ? "nav-link active" : "nav-link"}>
          <span className="nav-icon">🗺️</span>
          Farm Map
        </NavLink>
        <NavLink to="/farmers" className={({ isActive }) => isActive ? "nav-link active" : "nav-link"}>
          <span className="nav-icon">👨‍🌾</span>
          Farmers
        </NavLink>
        <NavLink to="/alerts" className={({ isActive }) => isActive ? "nav-link active" : "nav-link"}>
          <span className="nav-icon">🔔</span>
          Alerts
        </NavLink>
      </nav>
      <div className="sidebar-footer">
        {user.full_name && (
          <div style={{ marginBottom: 8 }}>
            <div style={{ fontSize: 12, color: "var(--text-primary)" }}>{user.full_name}</div>
            <div style={{ fontSize: 11, color: "var(--text-muted)", textTransform: "uppercase" }}>{user.role}</div>
          </div>
        )}
        <button className="btn" onClick={handleLogout} style={{ width: "100%", fontSize: 12 }}>
          Sign Out
        </button>
      </div>
    </aside>
  );
}

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const token = api.getToken();
  if (!token) return <Navigate to="/login" replace />;
  return <>{children}</>;
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route
          path="/*"
          element={
            <ProtectedRoute>
              <div className="app">
                <Sidebar />
                <main className="main-content">
                  <Routes>
                    <Route path="/" element={<Navigate to="/dashboard" replace />} />
                    <Route path="/dashboard" element={<Dashboard />} />
                    <Route path="/map" element={<MapView />} />
                    <Route path="/farmers" element={<Farmers />} />
                    <Route path="/farmers/:farmerId" element={<FarmerDetail />} />
                    <Route path="/alerts" element={<Alerts />} />
                  </Routes>
                </main>
              </div>
            </ProtectedRoute>
          }
        />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
