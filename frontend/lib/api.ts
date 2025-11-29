import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Create axios instance
const api = axios.create({
  baseURL: `${API_URL}/api`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Unauthorized - clear token and redirect to login
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/auth/login';
    }
    return Promise.reject(error);
  }
);

export default api;

// API functions
export const authAPI = {
  register: (data: any) => api.post('/auth/register', data),
  login: (data: any) => api.post('/auth/login', data),
  getMe: () => api.get('/auth/me'),
};

export const fileAPI = {
  uploadPDF: (formData: FormData) => 
    api.post('/upload/pdf', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  listFiles: () => api.get('/upload/files'),
  getFileStatus: (fileId: number) => api.get(`/upload/files/${fileId}/status`),
  getFileMetadata: (fileId: number) => api.get(`/upload/files/${fileId}/metadata`),
  deleteFile: (fileId: number) => api.delete(`/upload/files/${fileId}`),
};

export const scrapeAPI = {
  scrapeURL: (data: any) => api.post('/scrape/url', data),
};

export const chatAPI = {
  sendMessage: (data: any) => api.post('/chat/message', data),
  sendMessageV2: (data: any) => api.post('/chat/v2/message', data),
  getHistory: (sessionId: string) => api.get(`/chat/history/${sessionId}`),
  listSessions: () => api.get('/chat/sessions'),
  deleteSession: (sessionId: string) => api.delete(`/chat/sessions/${sessionId}`),
};

export const automationAPI = {
  sendEmail: (data: any) => api.post('/automations/email/send', data),
  sendWhatsApp: (data: any) => api.post('/automations/whatsapp/send', data),
  sendPush: (data: any) => api.post('/automations/push/send', data),
};
