import axios from 'axios';

const getBaseURL = () => '/api';

const API = axios.create({
  baseURL: getBaseURL(),
  headers: {
    'Content-Type': 'application/json',
  },
});

API.interceptors.request.use((config) => {
  const token = localStorage.getItem('legalflow_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const authAPI = {
  register: (data) => API.post('/auth/register', data),
  login: (data) => API.post('/auth/login', data),
  guestLogin: () => API.post('/auth/guest'),
  getMe: () => API.get('/auth/me'),
};

export const documentAPI = {
  upload: (formData) => API.post('/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  list: () => API.get('/documents'),
  getById: (id) => API.get(`/documents/${id}`),
  delete: (id) => API.delete(`/documents/${id}`),
  analyze: (id) => API.post(`/analyze/${id}`),
  getAnalysis: (id) => API.get(`/analysis/${id}`),
  compare: (data) => API.post('/compare', data),
  timeline: (id) => API.get(`/timeline/${id}`),
};

export const chatAPI = {
  sendMessage: (docId, message, sessionId = null, language = 'English') =>
    API.post(`/chat/document/${docId}`, { message, session_id: sessionId, language }),
  getHistory: (docId) => API.get(`/chat/history/${docId}`),
  clearHistory: (docId) => API.delete(`/chat/history/${docId}`),
  getSessions: (docId) => API.get(`/chat/sessions/${docId}`),
};

export const redlineAPI = {
  exportDocx: (documentId) => API.get(`/export/docx/${documentId}`, { responseType: 'blob' }),
};

export const templateAPI = {
  list: () => API.get('/templates'),
  generate: (data) => API.post('/templates/generate', data, { responseType: 'blob' }),
};

export const systemAPI = {
  getOllamaStatus: () => API.get('/system/ollama-status'),
};

export default API;
