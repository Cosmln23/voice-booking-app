/**
 * React Hook for Statistics Management
 * Handles dashboard stats and charts
 */

import { useState, useCallback, useEffect } from 'react';
import { api, supabase } from '../lib/api';
import type { 
  DashboardStats, 
  ChartData, 
  StatsPeriod,
  UseStatisticsReturn 
} from '../types/index';

export const useStatistics = (): UseStatisticsReturn => {
  const [statistics, setStatistics] = useState<DashboardStats | undefined>();
  const [charts, setCharts] = useState<ChartData[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | undefined>();
  const [hasSession, setHasSession] = useState(false);

  // Check for session on mount
  useEffect(() => {
    const checkSession = async () => {
      const { data: { session } } = await supabase.auth.getSession();
      setHasSession(!!session);
    };
    checkSession();

    // Listen for auth changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange((event, session) => {
      setHasSession(!!session);
    });

    return () => subscription.unsubscribe();
  }, []);

  const fetchStatistics = useCallback(async (period: StatsPeriod = 'today') => {
    // Don't fetch if no session
    if (!hasSession) {
      setStatistics(undefined);
      setError('No session available');
      return;
    }

    setIsLoading(true);
    setError(undefined);

    try {
      const response = await api.statistics.getStatistics(period);

      if (response.success && response.data) {
        setStatistics(response.data as DashboardStats);
      } else {
        throw new Error(response.message || 'Failed to fetch statistics');
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error occurred';
      setError(errorMessage);
      console.error('Failed to fetch statistics:', err);
      
      // Clear statistics on error
      setStatistics(undefined);
    } finally {
      setIsLoading(false);
    }
  }, [hasSession]);

  const fetchCharts = useCallback(async (period: StatsPeriod = 'week') => {
    // Don't fetch if no session
    if (!hasSession) {
      setCharts([]);
      setError('No session available');
      return;
    }

    setIsLoading(true);
    setError(undefined);

    try {
      const response = await api.statistics.getCharts(period);

      if (response.success && response.data) {
        setCharts(Array.isArray(response.data) ? response.data : []);
      } else {
        throw new Error(response.message || 'Failed to fetch charts');
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error occurred';
      setError(errorMessage);
      console.error('Failed to fetch charts:', err);
      
      // Clear charts on error
      setCharts([]);
    } finally {
      setIsLoading(false);
    }
  }, [hasSession]);

  return {
    statistics,
    charts,
    isLoading,
    error,
    fetchStatistics,
    fetchCharts,
  };
};