/** Type definitions for the surveillance frontend. */

export type RiskLevel = 'LOW' | 'MEDIUM' | 'HIGH';
export type ExchangeType = 'NSE' | 'BSE';

export interface Stock {
  id: number;
  symbol: string;
  name: string;
  exchange: ExchangeType;
  exchange_code?: string;
  isin?: string;
  sector?: string;
  market_cap_category?: string;
  is_active: boolean;
}

export interface HistoricalRecord {
  id: number;
  stock_id: number;
  trading_date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  turnover?: number;
  upper_circuit_limit?: number;
  lower_circuit_limit?: number;
  is_circuit_hit?: boolean;
}

export interface AnomalyAlert {
  id: number;
  stock_symbol: string;
  exchange: ExchangeType;
  detection_date: string;
  anomaly_score: number;
  risk_level: RiskLevel;
  reasons: string[];
  status: 'PENDING_REVIEW' | 'INVESTIGATING' | 'DISMISSED' | 'CONFIRMED_ANOMALY';
  model_breakdown?: {
    isolation_forest_score: number;
    lstm_reconstruction_error: number;
    rule_score: number;
  };
}

export interface SystemHealth {
  status: string;
  app_name: string;
  environment: string;
  database_connected: boolean;
  timestamp: string;
  version: string;
}
