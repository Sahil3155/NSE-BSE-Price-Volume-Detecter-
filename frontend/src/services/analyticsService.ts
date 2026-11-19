import { apiClient } from './api';

export interface OverviewMetrics {
  total_stocks_monitored: number;
  stocks_with_anomalies: number;
  high_risk_alerts: number;
  medium_risk_alerts: number;
  latest_detection_date: string | null;
  highest_anomaly_stocks: Array<{ symbol: string; score: number }>;
}

export interface AnomalyTrendPoint {
  date: string;
  total_detections: number;
  high_risk: number;
  medium_risk: number;
  average_score: number;
}

export interface ModelBenchmark {
  model_name: string;
  threshold: number;
  precision: number;
  recall: number;
  f1_score: number;
  roc_auc: number;
  pr_auc: number;
  false_positive_rate: number;
  confusion_matrix: { tn: number; fp: number; fn: number; tp: number };
}

export const fetchOverviewMetrics = async (): Promise<OverviewMetrics> => {
  const response = await apiClient.get<OverviewMetrics>('/analytics/overview');
  return response.data;
};

export const fetchAnomalyTrends = async (days: number = 30): Promise<AnomalyTrendPoint[]> => {
  const response = await apiClient.get<AnomalyTrendPoint[]>('/analytics/anomaly-trends', {
    params: { days },
  });
  return response.data;
};

export const fetchModelBenchmarks = async (): Promise<ModelBenchmark[]> => {
  const response = await apiClient.get<ModelBenchmark[]>('/analytics/model-comparison');
  return response.data;
};
