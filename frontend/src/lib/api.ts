/**
 * API Client for Voice Booking App
 * Handles all HTTP requests to the FastAPI backend
 */

import { createClient } from '@supabase/supabase-js';

// Base configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Supabase configuration
const SUPABASE_URL = process.env.NEXT_PUBLIC_SUPABASE_URL || '';
const SUPABASE_ANON_KEY = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || '';

// Create Supabase client
export const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

// Request timeout in milliseconds
const REQUEST_TIMEOUT = 10000;

// Clean auth headers - no forced authentication
async function withAuthHeaders(headers: Record<string, string> = {}): Promise<Record<string, string>> {
  const { data: { session } } = await supabase.auth.getSession();
  return session?.access_token
    ? { ...headers, Authorization: `Bearer ${session.access_token}` }
    : headers;
}

// API Response wrapper
interface ApiResponse<T> {
  success: boolean;
  data?: T;
  message?: string;
  total?: number;
}

// HTTP Client class
class ApiClient {
  private baseURL: string;
  private timeout: number;

  constructor(baseURL: string = API_BASE_URL, timeout: number = REQUEST_TIMEOUT) {
    this.baseURL = baseURL;
    this.timeout = timeout;
  }

  // Generic request method with timeout and auth
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeout);

    try {
      // Get headers with auth token (only if session exists)
      const authHeaders = await withAuthHeaders({
        'Content-Type': 'application/json',
        ...options.headers as Record<string, string>,
      });

      const response = await fetch(`${this.baseURL}${endpoint}`, {
        ...options,
        signal: controller.signal,
        headers: authHeaders,
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        // Handle 401 specifically for auth redirects
        if (response.status === 401) {
          // Clear session and redirect to login
          await supabase.auth.signOut();
          if (typeof window !== 'undefined') {
            window.location.href = '/login';
          }
          throw new Error('Authentication required');
        }
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      clearTimeout(timeoutId);
      
      if (error instanceof Error) {
        if (error.name === 'AbortError') {
          throw new Error('Request timeout');
        }
        throw error;
      }
      throw new Error('Unknown error occurred');
    }
  }

  // GET request
  async get<T>(endpoint: string, params?: Record<string, string>): Promise<ApiResponse<T>> {
    const url = new URL(`${this.baseURL}${endpoint}`);
    
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          url.searchParams.append(key, value);
        }
      });
    }

    return this.request<T>(url.pathname + url.search);
  }

  // POST request
  async post<T>(endpoint: string, data?: any): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  // PUT request
  async put<T>(endpoint: string, data?: any): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, {
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  // DELETE request
  async delete<T>(endpoint: string): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, {
      method: 'DELETE',
    });
  }
}

// Create and export API client instance
export const apiClient = new ApiClient();

// Appointments API
export const appointmentsApi = {
  getAppointments: (params?: {
    date?: string;
    status?: string;
    limit?: number;
    offset?: number;
  }) => apiClient.get('/api/appointments', params as Record<string, string>),

  createAppointment: (data: any) => apiClient.post('/api/appointments', data),

  updateAppointment: (id: string, data: any) => 
    apiClient.put(`/api/appointments/${id}`, data),

  deleteAppointment: (id: string) => 
    apiClient.delete(`/api/appointments/${id}`),
};

// Clients API
export const clientsApi = {
  getClients: (params?: {
    search?: string;
    status?: string;
    limit?: number;
    offset?: number;
  }) => apiClient.get('/api/clients', params as Record<string, string>),

  getClientStats: () => apiClient.get('/api/clients/stats'),

  createClient: (data: any) => apiClient.post('/api/clients', data),

  updateClient: (id: string, data: any) => 
    apiClient.put(`/api/clients/${id}`, data),

  deleteClient: (id: string) => 
    apiClient.delete(`/api/clients/${id}`),
};

// Services API
export const servicesApi = {
  getServices: (params?: {
    category?: string;
    status?: string;
    limit?: number;
    offset?: number;
  }) => apiClient.get('/api/services', params as Record<string, string>),

  getServiceStats: () => apiClient.get('/api/services/stats'),

  createService: (data: any) => apiClient.post('/api/services', data),

  updateService: (id: string, data: any) => 
    apiClient.put(`/api/services/${id}`, data),

  deleteService: (id: string) => 
    apiClient.delete(`/api/services/${id}`),
};

// Statistics API
export const statisticsApi = {
  getStatistics: (period?: string) => 
    apiClient.get('/api/stats', period ? { period } : undefined),

  getCharts: (period?: string) => 
    apiClient.get('/api/stats/charts', period ? { period } : undefined),
};

// Agent API
export const agentApi = {
  getStatus: () => apiClient.get('/api/agent/status'),
  
  start: () => apiClient.post('/api/agent/start'),
  
  stop: () => apiClient.post('/api/agent/stop'),
  
  getLogs: (params?: {
    limit?: number;
    log_type?: string;
  }) => apiClient.get('/api/agent/logs', params as Record<string, string>),

  getConfig: () => apiClient.get('/api/agent/config'),

  updateConfig: (data: any) => apiClient.put('/api/agent/config', data),

  simulateCall: () => apiClient.post('/api/agent/simulate-call'),
};

// Settings API
export const settingsApi = {
  getSettings: () => apiClient.get('/api/settings'),

  updateSettings: (data: any) => apiClient.put('/api/settings', data),

  getWorkingHours: () => apiClient.get('/api/settings/working-hours'),

  updateWorkingHours: (data: any) => 
    apiClient.put('/api/settings/working-hours', data),

  getNotifications: () => apiClient.get('/api/settings/notifications'),

  updateNotifications: (data: any) => 
    apiClient.put('/api/settings/notifications', data),

  getAgentSettings: () => apiClient.get('/api/settings/agent'),

  updateAgentSettings: (data: any) => 
    apiClient.put('/api/settings/agent', data),
};

// Calendar API
export const calendarApi = {
  getInfo: () => apiClient.get('/api/calendar/info'),

  setup: (data: any) => apiClient.post('/api/calendar/setup', data),

  validate: () => apiClient.get('/api/calendar/validate'),

  test: () => apiClient.post('/api/calendar/test'),

  enable: () => apiClient.put('/api/calendar/enable'),

  disable: () => apiClient.put('/api/calendar/disable'),

  getSetupGuide: () => apiClient.get('/api/calendar/setup-guide'),
};

// Export all APIs
export const api = {
  appointments: appointmentsApi,
  clients: clientsApi,
  services: servicesApi,
  statistics: statisticsApi,
  agent: agentApi,
  settings: settingsApi,
  calendar: calendarApi,
};

export default api;