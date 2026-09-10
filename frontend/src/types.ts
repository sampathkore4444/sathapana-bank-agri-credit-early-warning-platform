export interface Farmer {
  id: number;
  farmer_code: string;
  name: string;
  phone: string | null;
  province: string;
  district: string;
  commune: string | null;
  village: string | null;
  created_at: string;
}

export interface Farm {
  id: number;
  farm_code: string;
  farmer_id: number;
  centroid_lat: number;
  centroid_lon: number;
  boundary_geojson: string | null;
  area_hectares: number;
  area_satellite: number | null;
  crop_type: string;
  planting_date: string | null;
  expected_harvest: string | null;
  season: string;
  boundary_source: string;
  boundary_confidence: number;
  crop_classification_confidence: number;
  created_at: string;
}

export interface Loan {
  id: number;
  loan_code: string;
  farmer_id: number;
  outstanding_principal: number;
  monthly_installment: number;
  disbursement_date: string | null;
  maturity_date: string | null;
  interest_rate: number | null;
  dpd: number;
  dpd_max_90d: number;
  missed_payments_count: number;
  restructured: boolean;
  status: string;
  created_at: string;
}

export interface CropHealthRecord {
  id: number;
  farm_id: number;
  observation_date: string;
  ndvi_current: number;
  ndvi_historical: number;
  ndvi_deviation_pct: number;
  ndvi_trend: string;
  ndwi_current: number;
  growth_stage: string;
  flood_exposure: boolean;
  drought_stress: boolean;
  rainfall_30d: number;
  rainfall_deviation_30d: number;
  temperature_stress_days: number;
  sar_vh_backscatter: number;
  crop_health_score: number;
  status: string;
  confidence: number;
  created_at: string;
}

export interface RiskScore {
  id: number;
  farmer_id: number;
  farm_id: number;
  loan_id: number;
  scoring_date: string;
  risk_probability: number;
  risk_bucket: string;
  confidence: number;
  primary_drivers_json: string;
  recommended_action: string;
  created_at: string;
}

export interface RiskScoreDetail extends RiskScore {
  primary_drivers: FeatureContribution[];
}

export interface FeatureContribution {
  feature: string;
  value: number;
  contribution: number;
}

export interface Alert {
  id: number;
  alert_code: string;
  farm_id: number;
  risk_score_id: number | null;
  alert_type: string;
  severity: string;
  title: string;
  description: string;
  risk_score_value: number | null;
  status: string;
  assigned_to: string | null;
  action_taken: string | null;
  created_at: string;
  acknowledged_at: string | null;
  resolved_at: string | null;
}

export interface ProvinceBreakdown {
  province: string;
  green: number;
  amber: number;
  orange: number;
  red: number;
  total_outstanding: number;
}

export interface PortfolioSummary {
  total_farmers: number;
  total_outstanding: number;
  green_count: number;
  amber_count: number;
  orange_count: number;
  red_count: number;
  provinces: ProvinceBreakdown[];
}

export interface EarlyWarning {
  farmer_id: string;
  farmer_name: string;
  farm_id: string;
  loan_id: string;
  province: string;
  risk_probability: number;
  risk_bucket: string;
  confidence: number;
  outstanding: number;
  dpd: number;
  recommended_action: string;
}

export interface DashboardStats {
  total_alerts: number;
  open_alerts: number;
  acknowledged_alerts: number;
  resolved_alerts: number;
  average_risk_score: number;
  total_loans: number;
  loans_with_dpd: number;
  dpd_rate: number;
}

export interface GeoJSONFeature {
  type: "Feature";
  geometry: {
    type: string;
    coordinates: number[][][];
  };
  properties: {
    farm_id: string;
    farm_db_id: number;
    farmer_id: number;
    farmer_code: string;
    farmer_name: string;
    province: string;
    area_hectares: number;
    crop_type: string;
    risk_bucket: string;
    risk_probability: number;
    crop_health_score: number | null;
  };
}

export interface GeoJSONFeatureCollection {
  type: "FeatureCollection";
  features: GeoJSONFeature[];
}
