import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
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

export const runAnalysis = async (regionId, polygon, targetDate = null) => {
  const payload = {
    region_id: regionId,
    polygon: polygon,
  };
  
  if (targetDate) {
    payload.target_date = targetDate;
  }
  
  const response = await api.post('/analyze', payload);
  return response.data;
};

export default api;
