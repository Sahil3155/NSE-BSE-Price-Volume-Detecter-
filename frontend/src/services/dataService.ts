import { apiClient } from './api';

export interface MarketDataStatus {
  total_stocks: number;
  total_market_records: number;
  total_featured_records: number;
  latest_trading_date: string | null;
  earliest_trading_date: string | null;
  exchanges: string[];
}

export interface UploadResult {
  status: string;
  filename: string;
  exchange: string;
  total_records: number;
  valid_records: number;
  invalid_records: number;
  message: string;
}

export const fetchMarketDataStatus = async (): Promise<MarketDataStatus> => {
  const response = await apiClient.get<MarketDataStatus>('/market-data/status');
  return response.data;
};

export const uploadDatasetFile = async (
  file: File,
  exchange: string = 'NSE'
): Promise<UploadResult> => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('exchange', exchange);

  const response = await apiClient.post<UploadResult>('/market-data/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};
