import axios, { AxiosInstance, AxiosResponse } from 'axios';
import { AuthResponse, APIResponse, Node, MetricsData, Alert } from '../types';

class ApiService {
  private api: AxiosInstance;
  private baseURL: string;

  constructor() {
    this.baseURL = process.env.REACT_APP_API_URL || 'http://localhost:5000';
    
    this.api = axios.create({
      baseURL: this.baseURL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor to add auth token
    this.api.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('magi_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor to handle errors
    this.api.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          localStorage.removeItem('magi_token');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  // Authentication
  async login(username: string, password: string): Promise<AuthResponse> {
    const response: AxiosResponse<AuthResponse> = await this.api.post('/api/auth/login', {
      username,
      password,
    });
    return response.data;
  }

  async logout(): Promise<APIResponse> {
    const response: AxiosResponse<APIResponse> = await this.api.post('/api/auth/logout');
    return response.data;
  }

  async verifyToken(): Promise<AuthResponse> {
    const response: AxiosResponse<AuthResponse> = await this.api.get('/api/auth/verify');
    return response.data;
  }

  // Nodes
  async getNodes(): Promise<APIResponse<Node[]>> {
    const response: AxiosResponse<APIResponse<Node[]>> = await this.api.get('/api/nodes');
    return response.data;
  }

  async getNode(nodeId: string): Promise<APIResponse<Node>> {
    const response: AxiosResponse<APIResponse<Node>> = await this.api.get(`/api/nodes/${nodeId}`);
    return response.data;
  }

  async getNodeStatus(nodeId: string): Promise<APIResponse> {
    const response: AxiosResponse<APIResponse> = await this.api.get(`/api/nodes/${nodeId}/status`);
    return response.data;
  }

  async restartNodeService(nodeId: string, serviceName: string): Promise<APIResponse> {
    const response: AxiosResponse<APIResponse> = await this.api.post(
      `/api/nodes/${nodeId}/services/${serviceName}/restart`
    );
    return response.data;
  }

  // Metrics
  async getNodeMetrics(nodeId: string, timeRange?: string): Promise<APIResponse<MetricsData[]>> {
    const params = timeRange ? { range: timeRange } : {};
    const response: AxiosResponse<APIResponse<MetricsData[]>> = await this.api.get(
      `/api/metrics/${nodeId}`,
      { params }
    );
    return response.data;
  }

  async getAllMetrics(timeRange?: string): Promise<APIResponse<Record<string, MetricsData[]>>> {
    const params = timeRange ? { range: timeRange } : {};
    const response: AxiosResponse<APIResponse<Record<string, MetricsData[]>>> = await this.api.get(
      '/api/metrics',
      { params }
    );
    return response.data;
  }

  // Alerts
  async getAlerts(): Promise<APIResponse<Alert[]>> {
    const response: AxiosResponse<APIResponse<Alert[]>> = await this.api.get('/api/alerts');
    return response.data;
  }

  async acknowledgeAlert(alertId: string): Promise<APIResponse> {
    const response: AxiosResponse<APIResponse> = await this.api.post(`/api/alerts/${alertId}/acknowledge`);
    return response.data;
  }

  async dismissAlert(alertId: string): Promise<APIResponse> {
    const response: AxiosResponse<APIResponse> = await this.api.delete(`/api/alerts/${alertId}`);
    return response.data;
  }

  // Terminal
  async createTerminalSession(nodeId: string): Promise<APIResponse<{ sessionId: string; url: string }>> {
    const response: AxiosResponse<APIResponse<{ sessionId: string; url: string }>> = await this.api.post(
      `/api/terminal/${nodeId}/create`
    );
    return response.data;
  }

  async getTerminalSessions(): Promise<APIResponse> {
    const response: AxiosResponse<APIResponse> = await this.api.get('/api/terminal/sessions');
    return response.data;
  }

  async closeTerminalSession(sessionId: string): Promise<APIResponse> {
    const response: AxiosResponse<APIResponse> = await this.api.delete(`/api/terminal/${sessionId}`);
    return response.data;
  }

  // Configuration
  async getConfig(): Promise<APIResponse> {
    const response: AxiosResponse<APIResponse> = await this.api.get('/api/config');
    return response.data;
  }

  async updateConfig(config: any): Promise<APIResponse> {
    const response: AxiosResponse<APIResponse> = await this.api.put('/api/config', config);
    return response.data;
  }

  // Health check
  async healthCheck(): Promise<APIResponse> {
    const response: AxiosResponse<APIResponse> = await this.api.get('/health');
    return response.data;
  }
}

export const apiService = new ApiService();
export default apiService;
