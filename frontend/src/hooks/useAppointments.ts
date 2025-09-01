/**
 * React Hook for Appointments Management
 * Handles CRUD operations and state management
 */

import { useState, useCallback } from 'react';
import { api } from '@/lib/api';
import type { 
  Appointment, 
  AppointmentCreate, 
  AppointmentUpdate, 
  AppointmentFilters,
  UseAppointmentsReturn 
} from '@/types';

export const useAppointments = (): UseAppointmentsReturn => {
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [total, setTotal] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | undefined>();

  const fetchAppointments = useCallback(async (filters?: AppointmentFilters) => {
    setIsLoading(true);
    setError(undefined);

    try {
      const params = {
        date: filters?.date,
        status: filters?.status,
        limit: filters?.limit || 50,
        offset: filters?.offset || 0,
      };

      const response = await api.appointments.getAppointments(params);

      if (response.success && response.data) {
        setAppointments(Array.isArray(response.data) ? response.data : []);
        setTotal(response.total || 0);
      } else {
        throw new Error(response.message || 'Failed to fetch appointments');
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error occurred';
      setError(errorMessage);
      console.error('Failed to fetch appointments:', err);
      
      // Fallback to empty array on error
      setAppointments([]);
      setTotal(0);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const createAppointment = useCallback(async (data: AppointmentCreate): Promise<Appointment> => {
    setIsLoading(true);
    setError(undefined);

    try {
      const response = await api.appointments.createAppointment(data);

      if (response.success && response.data) {
        const newAppointment = response.data as Appointment;
        
        // Add to current list
        setAppointments(prev => [newAppointment, ...prev]);
        setTotal(prev => prev + 1);
        
        return newAppointment;
      } else {
        throw new Error(response.message || 'Failed to create appointment');
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error occurred';
      setError(errorMessage);
      console.error('Failed to create appointment:', err);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const updateAppointment = useCallback(async (id: string, data: AppointmentUpdate): Promise<Appointment> => {
    setIsLoading(true);
    setError(undefined);

    try {
      const response = await api.appointments.updateAppointment(id, data);

      if (response.success && response.data) {
        const updatedAppointment = response.data as Appointment;
        
        // Update in current list
        setAppointments(prev => 
          prev.map(appointment => 
            appointment.id === id ? updatedAppointment : appointment
          )
        );
        
        return updatedAppointment;
      } else {
        throw new Error(response.message || 'Failed to update appointment');
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error occurred';
      setError(errorMessage);
      console.error('Failed to update appointment:', err);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const deleteAppointment = useCallback(async (id: string): Promise<void> => {
    setIsLoading(true);
    setError(undefined);

    try {
      const response = await api.appointments.deleteAppointment(id);

      if (response.success) {
        // Remove from current list
        setAppointments(prev => prev.filter(appointment => appointment.id !== id));
        setTotal(prev => Math.max(0, prev - 1));
      } else {
        throw new Error(response.message || 'Failed to delete appointment');
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error occurred';
      setError(errorMessage);
      console.error('Failed to delete appointment:', err);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  return {
    appointments,
    total,
    isLoading,
    error,
    fetchAppointments,
    createAppointment,
    updateAppointment,
    deleteAppointment,
  };
};