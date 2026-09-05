export interface ForecastPoint {
  period: string;
  value: number;
  lower_bound: number;
  upper_bound: number;
}

export interface ModelMetrics {
  mae: number;
  rmse: number;
  mape: number;
}

export interface RevenueForecast {
  model_used: string;
  forecast: ForecastPoint[];
  evaluation: ModelMetrics;
  history: { period: string; revenue: number }[];
}

export interface ChurnExplanationFactor {
  feature: string;
  value: number;
  population_average: number;
  description: string;
}

export interface ChurnRiskCustomer {
  customer_id: number;
  customer_name: string;
  churn_probability: number;
  days_since_last_purchase: number;
  top_factors: ChurnExplanationFactor[];
}

export interface ChurnRisk {
  total_customers_analyzed: number;
  high_risk_count: number;
  customers: ChurnRiskCustomer[];
  global_feature_importance: { feature: string; importance: number }[];
}

export interface SegmentCount {
  segment: string;
  count: number;
}

export interface SegmentationResult {
  customers_segmented: number;
  by_segment: SegmentCount[];
}

export interface Anomaly {
  metric: string;
  period: string;
  severity: "critical" | "warning" | "information";
  expected_value: number;
  actual_value: number;
  explanation: string;
  recommended_action: string;
}

export interface AnomaliesResponse {
  anomalies: Anomaly[];
}
