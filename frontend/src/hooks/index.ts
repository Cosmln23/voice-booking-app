/**
 * Central export for all custom hooks
 */

export { useAppointments } from './useAppointments';
export { useClients } from './useClients';
export { useServices } from './useServices';
export { useStatistics } from './useStatistics';
export { useAgent } from './useAgent';

// Re-export types for convenience
export type {
  UseAppointmentsReturn,
  UseClientsReturn,
  UseServicesReturn,
  UseStatisticsReturn,
  UseAgentReturn,
} from '@/types';