'use client'

import { useState, useEffect } from 'react'
import clsx from "clsx"
import { supabase } from '@/lib/api'
import { useRouter } from 'next/navigation'
import { useAppointments } from '../../hooks/useAppointments'

import { 
  Calendar,
  Star, 
  Clock, 
  Archive, 
  LayoutDashboard,
  Users,
  Scissors,
  TrendingUp,
  Mic,
  Settings,
  X,
  User,
  LogOut
} from 'lucide-react'

import Image from 'next/image'

type PageType = 'dashboard' | 'today' | 'upcoming' | 'pending' | 'archive' | 'clients' | 'services' | 'statistics' | 'agent' | 'settings'


const adminNavigation = [
  { name: 'Dashboard', page: 'dashboard' as PageType, icon: LayoutDashboard },
  { name: 'Clienți', page: 'clients' as PageType, icon: Users },
  { name: 'Servicii', page: 'services' as PageType, icon: Scissors },
  { name: 'Statistici', page: 'statistics' as PageType, icon: TrendingUp },
  { name: 'Agent Vocal', page: 'agent' as PageType, icon: Mic },
  { name: 'Setări', page: 'settings' as PageType, icon: Settings },
]

interface AppointmentsSidebarProps {
  isMobile?: boolean
  onMobileToggle?: () => void
  currentPage?: PageType
  onPageChange?: (page: PageType) => void
}

export default function AppointmentsSidebar({ isMobile, onMobileToggle, currentPage = 'dashboard', onPageChange }: AppointmentsSidebarProps) {
  const [isLoggedIn, setIsLoggedIn] = useState(false)
  const [userInfo, setUserInfo] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const router = useRouter()
  const { appointments, fetchAppointments } = useAppointments()
  
  // Fetch appointments when user is logged in
  useEffect(() => {
    if (isLoggedIn) {
      fetchAppointments()
    }
  }, [isLoggedIn, fetchAppointments])
  
  // Calculate dynamic counts from API data
  const today = new Date().toISOString().split('T')[0]
  const todayCount = appointments.filter(apt => apt.date === today).length
  const upcomingCount = appointments.filter(apt => apt.date > today).length
  const pendingCount = appointments.filter(apt => apt.status === 'pending').length
  
  const navigation = [
    { name: 'Astăzi', page: 'today' as PageType, icon: Calendar, count: todayCount > 0 ? todayCount : undefined },
    { name: 'Următoarele', page: 'upcoming' as PageType, icon: Star, count: upcomingCount > 0 ? upcomingCount : undefined },
    { name: 'În așteptare', page: 'pending' as PageType, icon: Clock, count: pendingCount > 0 ? pendingCount : undefined },
    { name: 'Arhivă', page: 'archive' as PageType, icon: Archive },
  ]

  useEffect(() => {
    const getSession = async () => {
      try {
        const { data: { session } } = await supabase.auth.getSession()
        
        if (session?.user) {
          setIsLoggedIn(true)
          setUserInfo(session.user)
        } else {
          setIsLoggedIn(false)
          setUserInfo(null)
        }
      } catch (error) {
        console.error('Session error:', error)
      } finally {
        setLoading(false)
      }
    }

    getSession()

    const { data: { subscription } } = supabase.auth.onAuthStateChange((event, session) => {
      if (session?.user) {
        setIsLoggedIn(true)
        setUserInfo(session.user)
      } else {
        setIsLoggedIn(false)
        setUserInfo(null)
      }
      setLoading(false)
    })

    return () => subscription.unsubscribe()
  }, [])

  const handleLogin = () => {
    router.push('/login')
  }

  const handleLogout = async () => {
    try {
      await supabase.auth.signOut()
      setIsLoggedIn(false)
      setUserInfo(null)
      router.push('/login')
    } catch (error) {
      console.error('Logout error:', error)
    }
  }
  return (
    <div className={clsx(
      "bg-card border-border flex flex-col",
      isMobile ? "w-full h-full" : "w-64 border-r"
    )}>
        {/* App Logo */}
        <div className="p-4 border-b border-border">
          <div className="flex items-center whitespace-nowrap">
            <div className="w-8 h-8 rounded-2xl bg-secondary flex items-center justify-center text-primary font-bold">
              VB
            </div>
            <span className="ml-2 font-medium text-primary">Voice Booking</span>
            {isMobile && (
              <button 
                onClick={onMobileToggle}
                className="ml-auto p-2 text-secondary hover:text-primary rounded-2xl hover:bg-card-hover transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            )}
          </div>
        </div>
      
      {/* Main Navigation */}
      <nav className="flex-1 overflow-y-auto p-2">
        <div className="space-y-1">
          {navigation.map((item) => (
            <button
              key={item.name}
              onClick={() => onPageChange?.(item.page)}
              className={clsx(
                'flex items-center w-full px-3 py-2 rounded-2xl group transition-colors',
                currentPage === item.page
                  ? 'bg-secondary/10 text-primary border border-border'
                  : 'text-secondary hover:text-primary hover:bg-card-hover'
              )}
            >
              <item.icon className="h-5 w-5 mr-3" />
              <span>{item.name}</span>
              {item.count && (
                <span className={clsx(
                  'ml-auto rounded-full px-2 py-0.5 text-xs',
                  currentPage === item.page
                    ? 'bg-secondary/20 text-primary'
                    : 'bg-background text-secondary'
                )}>
                  {item.count}
                </span>
              )}
            </button>
          ))}
        </div>
        
        {/* Admin Section */}
        <div className="mt-6 pt-4 border-t border-border">
          <h3 className="px-3 text-xs font-semibold text-secondary uppercase tracking-wider">
            Administrare
          </h3>
          <div className="mt-2 space-y-1">
            {adminNavigation.map((item) => (
              <button
                key={item.name}
                onClick={() => onPageChange?.(item.page)}
                className={clsx(
                  "flex items-center w-full px-3 py-2 text-sm rounded-2xl transition-colors",
                  currentPage === item.page
                    ? 'bg-secondary/10 text-primary border border-border'
                    : 'text-secondary hover:text-primary hover:bg-card-hover'
                )}
              >
                <item.icon className="h-4 w-4 mr-3" />
                <span>{item.name}</span>
              </button>
            ))}
          </div>
        </div>
      </nav>
      
      {/* User Profile */}
      <div className="p-3 border-t border-border flex items-center whitespace-nowrap">
        {loading ? (
          <div className="flex items-center w-full">
            <div className="w-8 h-8 rounded-full bg-secondary/20 animate-pulse"></div>
            <div className="ml-2">
              <div className="h-3 bg-secondary/20 rounded w-16 animate-pulse"></div>
              <div className="h-2 bg-secondary/10 rounded w-20 mt-1 animate-pulse"></div>
            </div>
          </div>
        ) : !isLoggedIn ? (
          <div 
            className="flex items-center cursor-pointer hover:bg-card-hover rounded-md p-1 -m-1 transition-colors w-full"
            onClick={handleLogin}
          >
            <div className="w-8 h-8 rounded-full bg-secondary/20 flex items-center justify-center">
              <User className="w-4 h-4 text-secondary" />
            </div>
            <div className="ml-2">
              <div className="text-sm text-secondary">Log In / Sign Up</div>
              <div className="text-xs text-secondary/70">Intră în cont</div>
            </div>
          </div>
        ) : (
          <div className="flex items-center justify-between w-full">
            <div className="flex items-center flex-1 min-w-0">
              <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white text-sm font-medium">
                {userInfo?.email?.charAt(0)?.toUpperCase() || 'A'}
              </div>
              <div className="ml-2 min-w-0 flex-1">
                <div className="text-sm font-medium text-primary truncate">
                  {userInfo?.user_metadata?.name || userInfo?.email?.split('@')[0] || 'Admin'}
                </div>
                <div className="text-xs text-secondary truncate">
                  {userInfo?.email || 'admin@example.com'}
                </div>
              </div>
            </div>
            <button
              onClick={handleLogout}
              className="ml-2 p-1 hover:bg-destructive/10 rounded-md text-destructive hover:text-destructive transition-colors flex-shrink-0"
              title="Logout"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        )}
      </div>
    </div>
  )
}