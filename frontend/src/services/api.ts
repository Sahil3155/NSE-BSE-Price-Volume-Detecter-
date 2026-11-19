import axios from 'axios';
import { SystemHealth } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 15000,
});

export const getHealthStatus = async (): Promise<SystemHealth> => {
  const response = await apiClient.get<SystemHealth>('/health');
  return response.data;
};
