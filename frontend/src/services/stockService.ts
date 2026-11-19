import { apiClient } from './api';
import { Stock } from '../types';

export interface StockHistoryResponse {
  symbol: string;
  exchange: string;
  total_records: number;
  history: Array<{
    trading_date: string;
    open: number;
    high: number;
    low: number;
    close: number;
    volume: number;
    turnover?: number;
    daily_return?: number;
    consecutive_upper_circuits?: number;
  }>;
}

export const fetchStocks = async (exchange?: string): Promise<Stock[]> => {
  const params = exchange ? { exchange } : {};
  const response = await apiClient.get<Stock[]>('/stocks', { params });
  return response.data;
};

export const fetchStockHistory = async (
  symbol: string,
  startDate?: string,
  endDate?: string
): Promise<StockHistoryResponse> => {
  const params: Record<string, string> = {};
  if (startDate) params.start_date = startDate;
  if (endDate) params.end_date = endDate;
  const response = await apiClient.get<StockHistoryResponse>(`/stocks/${symbol}/history`, { params });
  return response.data;
};
