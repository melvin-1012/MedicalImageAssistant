/**
 * MediSight AI - Frontend API Client
 * Connects the frontend UI to the FastAPI backend (http://localhost:8000).
 */
(function (global) {
  'use strict';

  const API_BASE = 'http://localhost:8000';

  const api = {
    baseUrl: API_BASE,

    // Token helpers
    getToken: function () {
      return localStorage.getItem('auth_token') || '';
    },

    setToken: function (token) {
      if (token) localStorage.setItem('auth_token', token);
      else localStorage.removeItem('auth_token');
    },

    getCurrentUser: function () {
      try {
        return JSON.parse(localStorage.getItem('currentUser') || 'null');
      } catch (e) {
        return null;
      }
    },

    setCurrentUser: function (user) {
      if (user) localStorage.setItem('currentUser', JSON.stringify(user));
      else localStorage.removeItem('currentUser');
    },

    // Generic fetch helper
    request: async function (path, options = {}) {
      const url = `${API_BASE}${path}`;
      const headers = Object.assign({}, options.headers || {});
      const token = api.getToken();

      if (token && !headers['Authorization']) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      if (!(options.body instanceof FormData) && !headers['Content-Type']) {
        headers['Content-Type'] = 'application/json';
      }

      try {
        const response = await fetch(url, { ...options, headers });
        const data = await response.json().catch(() => ({}));
        if (!response.ok) {
          throw new Error(data.detail || data.message || `Request failed with status ${response.status}`);
        }
        return data;
      } catch (err) {
        console.warn(`[MediSight API] Error requesting ${url}:`, err.message);
        throw err;
      }
    },

    // Check backend health
    checkHealth: async function () {
      return api.request('/health', { method: 'GET' });
    },

    // Authentication
    login: async function (email, password) {
      const data = await api.request('/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email, password }),
      });
      if (data.access_token) {
        api.setToken(data.access_token);
        api.setCurrentUser(data.user || { email, role: data.role, full_name: data.full_name });
      }
      return data;
    },

    signup: async function (signupData) {
      return api.request('/auth/signup', {
        method: 'POST',
        body: JSON.stringify(signupData),
      });
    },

    getMe: async function () {
      return api.request('/auth/me', { method: 'GET' });
    },

    // GenAI Multimodal Analysis (Person 4 module)
    analyzeWithGenAI: async function (visionData, rawNotes) {
      return api.request('/genai/analyze', {
        method: 'POST',
        body: JSON.stringify({
          vision_data: visionData,
          raw_notes: rawNotes,
        }),
      });
    },

    // Imaging Upload
    uploadImaging: async function (formData) {
      return api.request('/imaging/upload', {
        method: 'POST',
        body: formData,
      });
    },

    // Patients
    getPatients: async function () {
      return api.request('/patients/', { method: 'GET' });
    },

    // Reports
    getReports: async function () {
      return api.request('/reports/', { method: 'GET' });
    },

    getReportPdfUrl: function (reportId) {
      return `${API_BASE}/reports/${reportId}/pdf`;
    },

    submitDoctorAssessment: async function (reportId, assessment) {
      return api.request(`/reports/${reportId}/doctor-assessment`, {
        method: 'POST',
        body: JSON.stringify(assessment),
      });
    },

    finalizeReport: async function (reportId) {
      return api.request(`/reports/${reportId}/finalize`, {
        method: 'POST',
      });
    },
  };

  global.MediSightAPI = api;
})(window);
