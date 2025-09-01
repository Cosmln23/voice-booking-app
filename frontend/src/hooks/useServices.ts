/**
 * React Hook for Services Management
 * Handles CRUD operations and state management
 */

import { useState, useCallback } from 'react';
import { api } from '../lib/api';
import type { 
  Service, 
  ServiceCreate, 
  ServiceUpdate, 
  ServiceFilters,
  ServiceStats,
  UseServicesReturn 
} from '../types';

export const useServices = (): UseServicesReturn => {
  const [services, setServices] = useState<Service[]>([]);
  const [total, setTotal] = useState(0);
  const [stats, setStats] = useState<ServiceStats | undefined>();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | undefined>();

  const fetchServices = useCallback(async (filters?: ServiceFilters) => {
    setIsLoading(true);
    setError(undefined);

    try {
      const params = {
        category: filters?.category,
        status: filters?.status,
        limit: filters?.limit || 50,
        offset: filters?.offset || 0,
      };

      const response = await api.services.getServices(params);

      if (response.success && response.data) {
        setServices(Array.isArray(response.data) ? response.data : []);
        setTotal(response.total || 0);
      } else {
        throw new Error(response.message || 'Failed to fetch services');
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error occurred';
      setError(errorMessage);
      console.error('Failed to fetch services:', err);
      
      // Fallback to empty array on error
      setServices([]);
      setTotal(0);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const fetchStats = useCallback(async () => {
    try {
      const response = await api.services.getServiceStats();

      if (response.success && response.data) {
        setStats(response.data as ServiceStats);
      } else {
        console.warn('Failed to fetch service stats:', response.message);
      }
    } catch (err) {
      console.error('Failed to fetch service stats:', err);
    }
  }, []);

  const createService = useCallback(async (data: ServiceCreate): Promise<Service> => {
    setIsLoading(true);
    setError(undefined);

    try {
      const response = await api.services.createService(data);

      if (response.success && response.data) {
        const newService = response.data as Service;
        
        // Add to current list
        setServices(prev => [newService, ...prev]);
        setTotal(prev => prev + 1);
        
        // Update stats if available
        if (stats) {
          setStats(prev => prev ? {
            ...prev,
            total_services: prev.total_services + 1,
            active_services: data.status === 'active' ? prev.active_services + 1 : prev.active_services,
          } : undefined);
        }
        
        return newService;
      } else {
        throw new Error(response.message || 'Failed to create service');
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error occurred';
      setError(errorMessage);
      console.error('Failed to create service:', err);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [stats]);

  const updateService = useCallback(async (id: string, data: ServiceUpdate): Promise<Service> => {
    setIsLoading(true);
    setError(undefined);

    try {
      const response = await api.services.updateService(id, data);

      if (response.success && response.data) {
        const updatedService = response.data as Service;
        
        // Update in current list
        setServices(prev => 
          prev.map(service => 
            service.id === id ? updatedService : service
          )
        );
        
        return updatedService;
      } else {
        throw new Error(response.message || 'Failed to update service');
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error occurred';
      setError(errorMessage);
      console.error('Failed to update service:', err);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const deleteService = useCallback(async (id: string): Promise<void> => {
    setIsLoading(true);
    setError(undefined);

    try {
      const response = await api.services.deleteService(id);

      if (response.success) {
        // Remove from current list
        const deletedService = services.find(service => service.id === id);
        setServices(prev => prev.filter(service => service.id !== id));
        setTotal(prev => Math.max(0, prev - 1));
        
        // Update stats if available
        if (stats && deletedService) {
          setStats(prev => prev ? {
            ...prev,
            total_services: Math.max(0, prev.total_services - 1),
            active_services: deletedService.status === 'active' 
              ? Math.max(0, prev.active_services - 1) 
              : prev.active_services,
          } : undefined);
        }
      } else {
        throw new Error(response.message || 'Failed to delete service');
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error occurred';
      setError(errorMessage);
      console.error('Failed to delete service:', err);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [services, stats]);

  return {
    services,
    total,
    stats,
    isLoading,
    error,
    fetchServices,
    fetchStats,
    createService,
    updateService,
    deleteService,
  };
};