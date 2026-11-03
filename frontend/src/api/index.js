import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

export const fetchHealth = async () => {
  const response = await api.get('/health');
  return response.data;
};

export const fetchAlerts = async (limit = 10) => {
  const response = await api.get(`/alerts?limit=${limit}`);
  return response.data;
};

export const fetchHistory = async (limit = 100) => {
  const response = await api.get(`/history?limit=${limit}`);
  return response.data;
};

export const fetchMonitoringFeatures = async (regionId = 'sundarbans-transboundary-v1', limit = 120) => {
  const response = await api.get('/monitoring/features', { params: { region_id: regionId, limit } });
  return response.data;
};

export const fetchMonitoringDecisions = async (regionId = 'sundarbans-transboundary-v1', limit = 20) => {
  const response = await api.get('/monitoring/decisions', { params: { region_id: regionId, limit } });
  return response.data;
};

export const runMonitoring = async (periodStart, regionId = 'sundarbans-transboundary-v1') => {
  const response = await api.post('/monitoring/run', { region_id: regionId, period_start: periodStart });
  return response.data;
};

export const fetchAoi = async () => {
  const response = await api.get('/aoi');
  return response.data;
};

export default api;
