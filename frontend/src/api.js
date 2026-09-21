import axios from 'axios';

const api = axios.create({ baseURL: '/api' });

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('crimegpt_token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('crimegpt_token');
      localStorage.removeItem('crimegpt_user');
      window.location.href = '/login';
    }
    return Promise.reject(err);
  }
);

export const authAPI = {
  register: (data) => api.post('/auth/register', data),
  login: (data) => api.post('/auth/login', data),
  getMe: () => api.get('/auth/me'),
  updateMe: (data) => api.put('/auth/me', data),
};

export const casesAPI = {
  create: (data) => api.post('/cases/', data),
  list: (params) => api.get('/cases/', { params }),
  get: (id) => api.get(`/cases/${id}`),
  update: (id, data) => api.put(`/cases/${id}`, data),
  generateFIR: (id) => api.post(`/cases/generate-fir/${id}`),
  fromComplaint: (data) => api.post('/cases/from-complaint', data),
  getTimeline: (id) => api.get(`/cases/${id}/timeline`),
  addTimelineEvent: (id, data) => api.post(`/cases/${id}/timeline`, data),
  getLegalSuggestions: (id) => api.post(`/cases/${id}/legal-suggestions`),
  getLandmarkJudgments: (id) => api.get(`/cases/${id}/landmark-judgments`),
  classifyNLP: (text) => api.post('/cases/classify-nlp', { text }),
  getStats: () => api.get('/cases/stats'),
};

export const evidenceAPI = {
  upload: (caseId, formData) => api.post(`/evidence/${caseId}`, formData, { headers: { 'Content-Type': 'multipart/form-data' } }),
  list: (caseId) => api.get(`/evidence/${caseId}`),
  delete: (id) => api.delete(`/evidence/${id}`),
};

export const notificationsAPI = {
  list: () => api.get('/notifications'),
  markRead: (id) => api.put(`/notifications/${id}/read`),
  markAllRead: () => api.put('/notifications/read-all'),
  unreadCount: () => api.get('/notifications/unread-count'),
};

export const remindersAPI = {
  create: (caseId, data) => api.post(`/reminders/${caseId}`, data),
  list: () => api.get('/reminders'),
  complete: (id) => api.put(`/reminders/${id}/complete`),
};

export const chatAPI = {
  send: (data) => api.post('/chat/', data),
  history: () => api.get('/chat/history'),
};

export const kanoonAPI = {
  search: (query, page = 0) => api.get('/kanoon/search', { params: { query, page } }),
};

export const documentsAPI = {
  getTypes: () => api.get('/documents/types'),
  generate: (caseId, data) => api.post(`/documents/${caseId}/generate`, data),
};

export const datasetAPI = {
  seed: () => api.post('/dataset/seed'),
  getLegalSections: (params) => api.get('/dataset/legal-sections', { params }),
  getSampleFIRs: () => api.get('/dataset/sample-firs'),
};

export default api;
