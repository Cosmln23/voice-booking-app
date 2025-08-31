'use client'

import { useState, useEffect } from 'react'

export function useSidebar() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(true)

  useEffect(() => {
    // Load sidebar state from localStorage
    try {
      const savedState = localStorage.getItem('sidebar-open')
      if (savedState !== null) {
        setIsSidebarOpen(JSON.parse(savedState))
      }
    } catch (error) {
      console.warn('Failed to load sidebar state from localStorage:', error)
    }
  }, [])

  const toggleSidebar = () => {
    const newState = !isSidebarOpen
    setIsSidebarOpen(newState)
    
    // Save to localStorage
    try {
      localStorage.setItem('sidebar-open', JSON.stringify(newState))
    } catch (error) {
      console.warn('Failed to save sidebar state to localStorage:', error)
    }
  }

  return { isSidebarOpen, toggleSidebar }
}