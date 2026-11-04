import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1',
  headers: {
    'Content-Type': 'application/json',
    ...(import.meta.env.VITE_API_KEY ? { 'X-API-Key': import.meta.env.VITE_API_KEY } : {}),
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

export const runMonitoring = async (periodStart, regionId = 'sundarbans-transboundary-v1', refresh = true) => {
  const response = await api.post('/monitoring/run', { region_id: regionId, period_start: periodStart, refresh });
  return response.data;
};

export const fetchLiveMapTiles = async (periodStart, layer = 'ndvi') => {
  const response = await api.get('/map/tiles', { params: { period_start: periodStart, layer } });
  return response.data;
};

export const downloadMonitoringReport = async (decisionId) => {
  const response = await api.get(`/reports/${decisionId}`, { responseType: 'blob' });
  const url = URL.createObjectURL(response.data);
  const anchor = document.createElement('a');
  anchor.href = url;
  anchor.download = `mangrove-lens-decision-${decisionId}.pdf`;
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
  URL.revokeObjectURL(url);
};

export const fetchMonitoringJobs = async (limit = 50) => {
  const response = await api.get('/monitoring/jobs', { params: { limit } });
  return response.data;
};

export const waitForMonitoringJob = async (jobId, timeoutMs = 180000) => {
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    const jobs = await fetchMonitoringJobs();
    const job = jobs.find(item => item.id === jobId);
    if (job?.status === 'completed') return job;
    if (job?.status === 'failed') throw new Error(job.error || 'Monitoring job failed');
    await new Promise(resolve => setTimeout(resolve, 1500));
  }
  throw new Error('Monitoring job is still running; check the jobs endpoint for progress.');
};

export const fetchAoi = async () => {
  const response = await api.get('/aoi');
  return response.data;
};

export const fetchAlertOutbox = async (limit = 50) => {
  const response = await api.get('/alerts/outbox', { params: { limit } });
  return response.data;
};

export const approveAlert = async (alertId, approvedBy) => {
  const response = await api.post(`/alerts/outbox/${alertId}/approve`, { approved_by: approvedBy });
  return response.data;
};

export const dispatchAlert = async (alertId) => {
  const response = await api.post(`/alerts/outbox/${alertId}/dispatch`);
  return response.data;
};

export default api;
