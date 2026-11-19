import { apiClient } from './api';
import { AnomalyAlert, RiskLevel } from '../types';

export interface AlertFilterParams {
  risk_level?: RiskLevel;
  status?: string;
  symbol?: string;
}

export const fetchAlerts = async (filters: AlertFilterParams = {}): Promise<AnomalyAlert[]> => {
  const response = await apiClient.get<AnomalyAlert[]>('/alerts', { params: filters });
  return response.data;
};

export const fetchAlertById = async (id: number): Promise<AnomalyAlert> => {
  const response = await apiClient.get<AnomalyAlert>(`/alerts/${id}`);
  return response.data;
};

export const updateAlertStatus = async (
  id: number,
  status: string,
  notes?: string
): Promise<AnomalyAlert> => {
  const response = await apiClient.patch<AnomalyAlert>(`/alerts/${id}/status`, {
    status,
    investigator_notes: notes,
  });
  return response.data;
};
