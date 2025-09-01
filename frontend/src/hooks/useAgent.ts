/**
 * React Hook for Voice Agent Management
 * Handles agent status, configuration, and operations
 */

import { useState, useCallback } from 'react';
import { api } from '../lib/api';
import type { 
  AgentStatusInfo, 
  AgentConfiguration,
  UseAgentReturn 
} from '../types';

export const useAgent = (): UseAgentReturn => {
  const [status, setStatus] = useState<AgentStatusInfo | undefined>();
  const [config, setConfig] = useState<AgentConfiguration | undefined>();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | undefined>();

  const fetchStatus = useCallback(async () => {
    setIsLoading(true);
    setError(undefined);

    try {
      const response = await api.agent.getStatus();

      if (response.success && response.data) {
        setStatus(response.data as AgentStatusInfo);
      } else {
        throw new Error(response.message || 'Failed to fetch agent status');
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error occurred';
      setError(errorMessage);
      console.error('Failed to fetch agent status:', err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const fetchConfig = useCallback(async () => {
    try {
      const response = await api.agent.getConfig();

      if (response.success && response.data) {
        setConfig(response.data as AgentConfiguration);
      } else {
        console.warn('Failed to fetch agent config:', response.message);
      }
    } catch (err) {
      console.error('Failed to fetch agent config:', err);
    }
  }, []);

  const startAgent = useCallback(async () => {
    setIsLoading(true);
    setError(undefined);

    try {
      const response = await api.agent.start();

      if (response.success) {
        // Update status to active
        setStatus(prev => prev ? {
          ...prev,
          status: 'active',
          last_activity: new Date().toISOString(),
        } : undefined);
      } else {
        throw new Error(response.message || 'Failed to start agent');
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error occurred';
      setError(errorMessage);
      console.error('Failed to start agent:', err);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const stopAgent = useCallback(async () => {
    setIsLoading(true);
    setError(undefined);

    try {
      const response = await api.agent.stop();

      if (response.success) {
        // Update status to inactive
        setStatus(prev => prev ? {
          ...prev,
          status: 'inactive',
          last_activity: new Date().toISOString(),
        } : undefined);
      } else {
        throw new Error(response.message || 'Failed to stop agent');
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error occurred';
      setError(errorMessage);
      console.error('Failed to stop agent:', err);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const updateConfig = useCallback(async (data: AgentConfiguration) => {
    setIsLoading(true);
    setError(undefined);

    try {
      const response = await api.agent.updateConfig(data);

      if (response.success && response.data) {
        setConfig(response.data as AgentConfiguration);
      } else {
        throw new Error(response.message || 'Failed to update agent config');
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error occurred';
      setError(errorMessage);
      console.error('Failed to update agent config:', err);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const simulateCall = useCallback(async () => {
    setIsLoading(true);
    setError(undefined);

    try {
      const response = await api.agent.simulateCall();

      if (response.success) {
        // Refresh status to get updated logs
        await fetchStatus();
      } else {
        throw new Error(response.message || 'Failed to simulate call');
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error occurred';
      setError(errorMessage);
      console.error('Failed to simulate call:', err);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [fetchStatus]);

  return {
    status,
    config,
    isLoading,
    error,
    fetchStatus,
    fetchConfig,
    startAgent,
    stopAgent,
    updateConfig,
    simulateCall,
  };
};