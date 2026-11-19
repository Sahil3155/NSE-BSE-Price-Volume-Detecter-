import { apiClient } from './api';

export interface DetectionRequest {
  exchange?: string;
  symbol?: string;
  start_date?: string;
  end_date?: string;
  model_name?: string;
}

export interface DetectionResult {
  id?: number;
  symbol: string;
  exchange: string;
  trading_date: string;
  anomaly_score: number;
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH';
  reasons: string[];
  model_breakdown: {
    isolation_forest_score: number;
    lstm_reconstruction_score: number;
    rule_score: number;
  };
}

export interface DetectionRunResponse {
  status: string;
  records_analyzed: number;
  anomalies_detected: number;
  high_risk_count: number;
  medium_risk_count: number;
  results: DetectionResult[];
}

export const runDetection = async (req: DetectionRequest): Promise<DetectionRunResponse> => {
  const response = await apiClient.post<DetectionRunResponse>('/detection/run', req);
  return response.data;
};

export const fetchDetectionResults = async (riskLevel?: string): Promise<DetectionResult[]> => {
  const params = riskLevel ? { risk_level: riskLevel } : {};
  const response = await apiClient.get<DetectionResult[]>('/detection/results', { params });
  return response.data;
};
