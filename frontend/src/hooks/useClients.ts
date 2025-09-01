/**
 * React Hook for Clients Management
 * Handles CRUD operations and state management
 */

import { useState, useCallback } from 'react';
import { api } from '@/lib/api';
import type { 
  Client, 
  ClientCreate, 
  ClientUpdate, 
  ClientFilters,
  ClientStats,
  UseClientsReturn 
} from '@/types';

export const useClients = (): UseClientsReturn => {
  const [clients, setClients] = useState<Client[]>([]);
  const [total, setTotal] = useState(0);
  const [stats, setStats] = useState<ClientStats | undefined>();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | undefined>();

  const fetchClients = useCallback(async (filters?: ClientFilters) => {
    setIsLoading(true);
    setError(undefined);

    try {
      const params = {
        search: filters?.search,
        status: filters?.status,
        limit: filters?.limit || 50,
        offset: filters?.offset || 0,
      };

      const response = await api.clients.getClients(params);

      if (response.success && response.data) {
        setClients(Array.isArray(response.data) ? response.data : []);
        setTotal(response.total || 0);
      } else {
        throw new Error(response.message || 'Failed to fetch clients');
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error occurred';
      setError(errorMessage);
      console.error('Failed to fetch clients:', err);
      
      // Fallback to empty array on error
      setClients([]);
      setTotal(0);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const fetchStats = useCallback(async () => {
    try {
      const response = await api.clients.getClientStats();

      if (response.success && response.data) {
        setStats(response.data as ClientStats);
      } else {
        console.warn('Failed to fetch client stats:', response.message);
      }
    } catch (err) {
      console.error('Failed to fetch client stats:', err);
    }
  }, []);

  const createClient = useCallback(async (data: ClientCreate): Promise<Client> => {
    setIsLoading(true);
    setError(undefined);

    try {
      const response = await api.clients.createClient(data);

      if (response.success && response.data) {
        const newClient = response.data as Client;
        
        // Add to current list
        setClients(prev => [newClient, ...prev]);
        setTotal(prev => prev + 1);
        
        // Update stats if available
        if (stats) {
          setStats(prev => prev ? {
            ...prev,
            total_clients: prev.total_clients + 1,
            active_clients: data.status === 'active' ? prev.active_clients + 1 : prev.active_clients,
          } : undefined);
        }
        
        return newClient;
      } else {
        throw new Error(response.message || 'Failed to create client');
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error occurred';
      setError(errorMessage);
      console.error('Failed to create client:', err);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [stats]);

  const updateClient = useCallback(async (id: string, data: ClientUpdate): Promise<Client> => {
    setIsLoading(true);
    setError(undefined);

    try {
      const response = await api.clients.updateClient(id, data);

      if (response.success && response.data) {
        const updatedClient = response.data as Client;
        
        // Update in current list
        setClients(prev => 
          prev.map(client => 
            client.id === id ? updatedClient : client
          )
        );
        
        return updatedClient;
      } else {
        throw new Error(response.message || 'Failed to update client');
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error occurred';
      setError(errorMessage);
      console.error('Failed to update client:', err);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const deleteClient = useCallback(async (id: string): Promise<void> => {
    setIsLoading(true);
    setError(undefined);

    try {
      const response = await api.clients.deleteClient(id);

      if (response.success) {
        // Remove from current list
        const deletedClient = clients.find(client => client.id === id);
        setClients(prev => prev.filter(client => client.id !== id));
        setTotal(prev => Math.max(0, prev - 1));
        
        // Update stats if available
        if (stats && deletedClient) {
          setStats(prev => prev ? {
            ...prev,
            total_clients: Math.max(0, prev.total_clients - 1),
            active_clients: deletedClient.status === 'active' 
              ? Math.max(0, prev.active_clients - 1) 
              : prev.active_clients,
            inactive_clients: deletedClient.status === 'inactive'
              ? Math.max(0, prev.inactive_clients - 1)
              : prev.inactive_clients,
          } : undefined);
        }
      } else {
        throw new Error(response.message || 'Failed to delete client');
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error occurred';
      setError(errorMessage);
      console.error('Failed to delete client:', err);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [clients, stats]);

  return {
    clients,
    total,
    stats,
    isLoading,
    error,
    fetchClients,
    fetchStats,
    createClient,
    updateClient,
    deleteClient,
  };
};