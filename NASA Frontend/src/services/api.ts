import axios from 'axios';

// Dynamic API URL configuration for different environments
const getApiBaseUrl = () => {
  // Production: Use environment variable
  if (import.meta.env.PROD) {
    return import.meta.env.VITE_API_URL || 'https://nasa-backend.onrender.com';
  }
  
  // Development: Use local or environment variable
  return import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';
};

const API_BASE_URL = getApiBaseUrl();
const API_KEY = import.meta.env.VITE_API_KEY || 'i31G2AKUI24gGq2oaw8w8sYGryZEjMArrJEjffcT';

console.log(`🌐 API Base URL: ${API_BASE_URL}`);

// Create axios instance with base configuration
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
    'x-api-key': API_KEY,
  },
  timeout: 10000,
});

// Request interceptor for debugging
api.interceptors.request.use(
  (config) => {
    console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('❌ API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    console.log(`✅ API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error('❌ API Response Error:', error.response?.status, error.response?.data);
    
    if (error.response?.status === 401) {
      console.error('🔐 Authentication failed - check API key');
    } else if (error.response?.status === 404) {
      console.error('🔍 Endpoint not found');
    } else if (error.response?.status >= 500) {
      console.error('🔥 Server error');
    }
    
    return Promise.reject(error);
  }
);

// API service methods
export const nasaAPI = {
  // Health check
  healthCheck: () => api.get('/health'),
  
  // Search endpoints
  searchArticles: (query: string = '', limit: number = 10, includeNasaApis: boolean = true) => 
    api.get(`/api/search/`, { params: { query, limit, include_nasa_apis: includeNasaApis } }),
  
  searchCSV: (query: string = '', limit: number = 10) => 
    api.get(`/api/search/csv`, { params: { query, limit } }),
  
  searchNASAOnly: (query: string = '', limit: number = 20) => 
    api.get(`/api/search/nasa/search`, { params: { query, limit } }),
  
  testNASAAPIs: () => 
    api.get('/api/search/nasa/test'),
  
  getSearchStats: () => 
    api.get('/api/search/csv/stats'),
  
  // Graph endpoints
  getGraph: (params?: { node_type?: string; limit?: number; keyword?: string }) => 
    api.get('/api/graph/', { params }),
  
  getPublications: (params?: { limit?: number; author?: string; keyword?: string }) => 
    api.get('/api/graph/publications', { params }),
  
  getDatasets: (params?: { limit?: number; organism?: string; experiment_type?: string }) => 
    api.get('/api/graph/datasets', { params }),
  
  getProjects: (params?: { limit?: number; discipline?: string; status?: string }) => 
    api.get('/api/graph/projects', { params }),
  
  searchGraph: (query: string, limit: number = 20) => 
    api.get('/api/graph/search', { params: { query, limit } }),
  
  getNodeDetails: (nodeId: string) => 
    api.get(`/api/graph/node/${nodeId}`),
  
  // Summarize endpoints
  summarizeText: (data: { text: string; max_length?: number }) => 
    api.post('/api/summarize/', data),
  
  // Compare endpoints
  comparePublications: (data: { publication_ids: string[] }) => 
    api.post('/api/compare/', data),
  
  // Ingest endpoints
  ingestJSON: (data: any[]) => 
    api.post('/api/ingest/json', data),
  
  ingestCSV: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/api/ingest/csv', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
  },
};

// Connection test utility
export const testConnection = async () => {
  try {
    console.log('🧪 Testing NASA API Connection...');
    
    const healthResponse = await nasaAPI.healthCheck();
    console.log('✅ Health Check:', healthResponse.data);
    
    const searchResponse = await nasaAPI.searchArticles('microgravity', 3);
    console.log('✅ Search Test:', searchResponse.data);
    
    const graphResponse = await nasaAPI.getGraph({ limit: 5 });
    console.log('✅ Graph Test:', graphResponse.data);
    
    return {
      success: true,
      health: healthResponse.data,
      search: searchResponse.data,
      graph: graphResponse.data,
    };
  } catch (error: any) {
    console.error('❌ Connection Test Failed:', error.message);
    return {
      success: false,
      error: error.response?.data || error.message,
    };
  }
};

export default api;