'use client'

import { useState, useCallback } from 'react'
import { supabase } from '@/lib/api'

interface CalendarSettings {
  enabled: boolean
  calendar_id?: string
  calendar_name?: string
  timezone: string
  auto_create_events: boolean
  created_at?: string
  last_sync?: string
}

interface CalendarInfo {
  success: boolean
  calendar_info?: CalendarSettings
  message?: string
}

interface CalendarSetupRequest {
  calendar_name: string
  google_calendar_id: string
  google_calendar_credentials_json: string
  timezone?: string
  auto_create_events?: boolean
}

interface CalendarTestResult {
  success: boolean
  message: string
  test_results?: {
    calendar_id: string
    calendar_name: string
    test_event_created: boolean
    test_event_deleted: boolean
  }
}

export const useCalendar = () => {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [calendarInfo, setCalendarInfo] = useState<CalendarSettings | null>(null)

  const getAuthHeaders = async () => {
    const { data: { session } } = await supabase.auth.getSession()
    
    if (!session?.access_token) {
      throw new Error('No authentication token available')
    }

    return {
      'Authorization': `Bearer ${session.access_token}`,
      'Content-Type': 'application/json'
    }
  }

  const fetchCalendarInfo = useCallback(async () => {
    setLoading(true)
    setError(null)

    try {
      const headers = await getAuthHeaders()
      
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/calendar/info`, {
        method: 'GET',
        headers
      })

      const data: CalendarInfo = await response.json()

      if (!response.ok) {
        throw new Error(data.message || 'Failed to fetch calendar info')
      }

      if (data.success && data.calendar_info) {
        setCalendarInfo(data.calendar_info)
      } else {
        setCalendarInfo(null)
      }

      return data
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Failed to fetch calendar info'
      setError(errorMsg)
      console.error('Calendar info error:', err)
      return { success: false, message: errorMsg }
    } finally {
      setLoading(false)
    }
  }, [])

  const setupCalendar = async (setupRequest: CalendarSetupRequest) => {
    setLoading(true)
    setError(null)

    try {
      const headers = await getAuthHeaders()
      
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/calendar/setup`, {
        method: 'POST',
        headers,
        body: JSON.stringify(setupRequest)
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.detail || 'Failed to setup calendar')
      }

      if (data.success) {
        // Refresh calendar info after successful setup
        await fetchCalendarInfo()
      }

      return data
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Failed to setup calendar'
      setError(errorMsg)
      console.error('Calendar setup error:', err)
      throw err
    } finally {
      setLoading(false)
    }
  }

  const validateCalendar = async () => {
    setLoading(true)
    setError(null)

    try {
      const headers = await getAuthHeaders()
      
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/calendar/validate`, {
        method: 'GET',
        headers
      })

      const data = await response.json()

      return data
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Failed to validate calendar'
      setError(errorMsg)
      console.error('Calendar validation error:', err)
      return { success: false, message: errorMsg }
    } finally {
      setLoading(false)
    }
  }

  const testCalendar = async (): Promise<CalendarTestResult> => {
    setLoading(true)
    setError(null)

    try {
      const headers = await getAuthHeaders()
      
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/calendar/test`, {
        method: 'POST',
        headers
      })

      const data: CalendarTestResult = await response.json()

      if (!response.ok) {
        throw new Error(data.message || 'Calendar test failed')
      }

      return data
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Failed to test calendar'
      setError(errorMsg)
      console.error('Calendar test error:', err)
      return { success: false, message: errorMsg }
    } finally {
      setLoading(false)
    }
  }

  const enableCalendar = async () => {
    setLoading(true)
    setError(null)

    try {
      const headers = await getAuthHeaders()
      
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/calendar/enable`, {
        method: 'PUT',
        headers
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.detail || 'Failed to enable calendar')
      }

      if (data.success) {
        // Refresh calendar info after enabling
        await fetchCalendarInfo()
      }

      return data
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Failed to enable calendar'
      setError(errorMsg)
      console.error('Calendar enable error:', err)
      throw err
    } finally {
      setLoading(false)
    }
  }

  const disableCalendar = async () => {
    setLoading(true)
    setError(null)

    try {
      const headers = await getAuthHeaders()
      
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/calendar/disable`, {
        method: 'PUT',
        headers
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.detail || 'Failed to disable calendar')
      }

      if (data.success) {
        // Refresh calendar info after disabling
        await fetchCalendarInfo()
      }

      return data
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Failed to disable calendar'
      setError(errorMsg)
      console.error('Calendar disable error:', err)
      throw err
    } finally {
      setLoading(false)
    }
  }

  const getSetupGuide = async () => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/calendar/setup-guide`)
      const data = await response.json()
      return data
    } catch (err) {
      console.error('Failed to fetch setup guide:', err)
      return null
    }
  }

  return {
    loading,
    error,
    calendarInfo,
    fetchCalendarInfo,
    setupCalendar,
    validateCalendar,
    testCalendar,
    enableCalendar,
    disableCalendar,
    getSetupGuide
  }
}