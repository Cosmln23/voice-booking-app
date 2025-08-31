/**
 * TypeScript interfaces for Voice Booking App
 * Matches backend Pydantic models
 */

// ============================================================================
// COMMON TYPES
// ============================================================================

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  message?: string;
  total?: number;
}

export interface PaginationParams {
  limit?: number;
  offset?: number;
}

// ============================================================================
// APPOINTMENT TYPES
// ============================================================================

export type AppointmentStatus = 
  | 'confirmed' 
  | 'pending' 
  | 'in-progress' 
  | 'completed' 
  | 'cancelled' 
  | 'no-show';

export type AppointmentType = 'voice' | 'manual';

export type AppointmentPriority = 'urgent' | 'high' | 'normal';

export interface Appointment {
  id: string;
  client_name: string;
  phone: string;
  service: string;
  date: string; // ISO date string
  time: string; // HH:MM format
  duration: string; // e.g., "45min"
  status: AppointmentStatus;
  type: AppointmentType;
  priority: AppointmentPriority;
  notes?: string;
  price?: string; // e.g., "120 RON"
  created_at: string; // ISO datetime
  updated_at: string; // ISO datetime
}

export interface AppointmentCreate {
  client_name: string;
  phone: string;
  service: string;
  date: string;
  time: string;
  duration: string;
  status?: AppointmentStatus;
  type?: AppointmentType;
  priority?: AppointmentPriority;
  notes?: string;
}

export interface AppointmentUpdate {
  client_name?: string;
  phone?: string;
  service?: string;
  date?: string;
  time?: string;
  duration?: string;
  status?: AppointmentStatus;
  priority?: AppointmentPriority;
  notes?: string;
}

export interface AppointmentFilters extends PaginationParams {
  date?: string;
  status?: AppointmentStatus;
}

// ============================================================================
// CLIENT TYPES
// ============================================================================

export type ClientStatus = 'active' | 'inactive';

export interface Client {
  id: string;
  name: string;
  phone: string;
  email?: string;
  notes?: string;
  status: ClientStatus;
  avatar?: string;
  total_appointments: number;
  last_appointment?: string; // ISO datetime
  created_at: string;
  updated_at: string;
}

export interface ClientCreate {
  name: string;
  phone: string;
  email?: string;
  notes?: string;
  status?: ClientStatus;
}

export interface ClientUpdate {
  name?: string;
  phone?: string;
  email?: string;
  notes?: string;
  status?: ClientStatus;
}

export interface ClientFilters extends PaginationParams {
  search?: string;
  status?: ClientStatus;
}

export interface ClientStats {
  total_clients: number;
  new_this_month: number;
  active_clients: number;
  inactive_clients: number;
}

// ============================================================================
// SERVICE TYPES
// ============================================================================

export type ServiceCategory = 'individual' | 'package';
export type ServiceStatus = 'active' | 'inactive';

export interface Service {
  id: string;
  name: string;
  price: number;
  currency: string;
  duration: string; // e.g., "45min"
  category: ServiceCategory;
  description?: string;
  status: ServiceStatus;
  popularity_score: number;
  created_at: string;
  updated_at: string;
}

export interface ServiceCreate {
  name: string;
  price: number;
  currency?: string;
  duration: string;
  category?: ServiceCategory;
  description?: string;
  status?: ServiceStatus;
}

export interface ServiceUpdate {
  name?: string;
  price?: number;
  currency?: string;
  duration?: string;
  category?: ServiceCategory;
  description?: string;
  status?: ServiceStatus;
}

export interface ServiceFilters extends PaginationParams {
  category?: ServiceCategory;
  status?: ServiceStatus;
}

export interface ServiceStats {
  total_services: number;
  active_services: number;
  most_popular?: string;
  average_price: number;
}

// ============================================================================
// STATISTICS TYPES
// ============================================================================

export type StatsPeriod = 'today' | 'week' | 'month' | 'year';
export type TrendDirection = 'up' | 'down' | 'stable';
export type ChartType = 'line' | 'bar' | 'pie' | 'donut';

export interface TrendData {
  direction: TrendDirection;
  percentage: number;
  previous_value?: number;
}

export interface ChartDataPoint {
  label: string;
  value: number;
  date?: string;
  color?: string;
}

export interface ChartData {
  type: ChartType;
  title: string;
  data: ChartDataPoint[];
  metadata?: Record<string, any>;
}

export interface KPIMetric {
  name: string;
  value: number;
  unit: string;
  trend?: TrendData;
  target?: number;
  description?: string;
}

export interface ServicePopularity {
  service_name: string;
  appointment_count: number;
  revenue: number;
  percentage_of_total: number;
}

export interface RevenueBreakdown {
  individual_services: number;
  package_deals: number;
  total: number;
  currency: string;
}

export interface AppointmentDistribution {
  completed: number;
  cancelled: number;
  no_show: number;
  pending: number;
  confirmed: number;
  in_progress: number;
}

export interface PeriodStats {
  period: StatsPeriod;
  start_date: string;
  end_date: string;
  total_appointments: number;
  total_revenue: number;
  completion_rate: number;
  cancellation_rate: number;
  no_show_rate: number;
  average_appointment_value: number;
  new_clients: number;
  returning_clients: number;
  trends: Record<string, TrendData>;
}

export interface DashboardStats {
  current_period: PeriodStats;
  kpi_metrics: KPIMetric[];
  service_popularity: ServicePopularity[];
  revenue_breakdown: RevenueBreakdown;
  appointment_distribution: AppointmentDistribution;
  charts: ChartData[];
  last_updated: string;
}

// ============================================================================
// AGENT TYPES
// ============================================================================

export type AgentStatus = 'active' | 'inactive' | 'processing';
export type ActivityLogType = 
  | 'incoming_call' 
  | 'booking_success' 
  | 'booking_failed' 
  | 'system_status';

export interface ActivityLog {
  timestamp: string;
  type: ActivityLogType;
  message: string;
  client_info?: string;
  details?: Record<string, any>;
}

export interface AgentConfiguration {
  enabled: boolean;
  model: string;
  language: string;
  voice: string;
  auto_booking: boolean;
  confirmation_required: boolean;
}

export interface AgentStatusInfo {
  status: AgentStatus;
  last_activity?: string;
  total_calls: number;
  success_rate: number;
  activity_log: ActivityLog[];
}

// ============================================================================
// SETTINGS TYPES
// ============================================================================

export interface WorkingHours {
  day_of_week: number; // 0=Monday, 6=Sunday
  start_time: string; // HH:MM
  end_time: string; // HH:MM
  is_closed: boolean;
}

export interface NotificationSettings {
  email_notifications: boolean;
  sms_notifications: boolean;
  appointment_reminders: boolean;
  new_booking_alerts: boolean;
  system_updates: boolean;
}

export interface BusinessSettings {
  name: string;
  address: string;
  phone: string;
  email: string;
  working_hours: WorkingHours[];
  notifications: NotificationSettings;
  agent_config: AgentConfiguration;
  timezone: string;
}

// ============================================================================
// UI TYPES
// ============================================================================

export interface LoadingState {
  isLoading: boolean;
  error?: string;
}

export interface PaginationState {
  page: number;
  limit: number;
  total: number;
  hasMore: boolean;
}

export type PageType = 
  | 'dashboard' 
  | 'today' 
  | 'upcoming' 
  | 'pending' 
  | 'archive'
  | 'clients' 
  | 'services' 
  | 'statistics' 
  | 'agent' 
  | 'settings';

// ============================================================================
// HOOK RETURN TYPES
// ============================================================================

export interface UseAppointmentsReturn extends LoadingState {
  appointments: Appointment[];
  total: number;
  fetchAppointments: (filters?: AppointmentFilters) => Promise<void>;
  createAppointment: (data: AppointmentCreate) => Promise<Appointment>;
  updateAppointment: (id: string, data: AppointmentUpdate) => Promise<Appointment>;
  deleteAppointment: (id: string) => Promise<void>;
}

export interface UseClientsReturn extends LoadingState {
  clients: Client[];
  total: number;
  stats?: ClientStats;
  fetchClients: (filters?: ClientFilters) => Promise<void>;
  fetchStats: () => Promise<void>;
  createClient: (data: ClientCreate) => Promise<Client>;
  updateClient: (id: string, data: ClientUpdate) => Promise<Client>;
  deleteClient: (id: string) => Promise<void>;
}

export interface UseServicesReturn extends LoadingState {
  services: Service[];
  total: number;
  stats?: ServiceStats;
  fetchServices: (filters?: ServiceFilters) => Promise<void>;
  fetchStats: () => Promise<void>;
  createService: (data: ServiceCreate) => Promise<Service>;
  updateService: (id: string, data: ServiceUpdate) => Promise<Service>;
  deleteService: (id: string) => Promise<void>;
}

export interface UseStatisticsReturn extends LoadingState {
  statistics?: DashboardStats;
  charts: ChartData[];
  fetchStatistics: (period?: StatsPeriod) => Promise<void>;
  fetchCharts: (period?: StatsPeriod) => Promise<void>;
}

export interface UseAgentReturn extends LoadingState {
  status?: AgentStatusInfo;
  config?: AgentConfiguration;
  fetchStatus: () => Promise<void>;
  fetchConfig: () => Promise<void>;
  startAgent: () => Promise<void>;
  stopAgent: () => Promise<void>;
  updateConfig: (data: AgentConfiguration) => Promise<void>;
  simulateCall: () => Promise<void>;
}