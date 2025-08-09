export interface Node {
  id: string;
  name: string;
  role: string;
  description: string;
  ip: string;
  hostname: string;
  services: Service[];
  metrics: MetricsConfig;
  ssh: SSHConfig;
  terminal: TerminalConfig;
  status?: NodeStatus;
  lastSeen?: string;
}

export interface Service {
  name: string;
  display_name: string;
  port: number | null;
  health_endpoint: string | null;
  critical: boolean;
  status?: ServiceStatus;
}

export interface MetricsConfig {
  port: number;
  endpoint: string;
}

export interface SSHConfig {
  port: number;
  username: string;
  key_path: string;
}

export interface TerminalConfig {
  enabled: boolean;
  port: number;
}

export interface NodeStatus {
  online: boolean;
  cpu_usage: number;
  memory_usage: number;
  disk_usage: number;
  network_rx: number;
  network_tx: number;
  uptime: number;
  load_average: number[];
  temperature?: number;
}

export interface ServiceStatus {
  running: boolean;
  response_time?: number;
  last_check: string;
  error_message?: string;
}

export interface GlobalSettings {
  refresh_interval: number;
  alert_thresholds: AlertThresholds;
  authentication: AuthenticationSettings;
  notifications: NotificationSettings;
}

export interface AlertThresholds {
  cpu_usage: number;
  memory_usage: number;
  disk_usage: number;
  response_timeout: number;
}

export interface AuthenticationSettings {
  enabled: boolean;
  session_timeout: number;
  max_login_attempts: number;
}

export interface NotificationSettings {
  sound_enabled: boolean;
  desktop_notifications: boolean;
  email_alerts: boolean;
}

export interface NodesConfig {
  nodes: Node[];
  global_settings: GlobalSettings;
}

export interface User {
  id: string;
  username: string;
  loginTime?: string;
}

export interface AuthResponse {
  success: boolean;
  message: string;
  token?: string;
  user?: User;
}

export interface MetricsData {
  timestamp: string;
  nodeId: string;
  cpu: number;
  memory: number;
  disk: number;
  network: {
    rx: number;
    tx: number;
  };
  uptime: number;
  load: number[];
}

export interface Alert {
  id: string;
  nodeId: string;
  type: 'warning' | 'error' | 'info';
  message: string;
  timestamp: string;
  acknowledged: boolean;
  service?: string;
}

export interface TerminalSession {
  id: string;
  nodeId: string;
  active: boolean;
  startTime: string;
  lastActivity: string;
}

export interface APIResponse<T = any> {
  success: boolean;
  message: string;
  data?: T;
  error?: string;
}
