'use client'

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
  X
} from 'lucide-react'
import { cn } from '@/lib/utils'
import Image from 'next/image'

type PageType = 'dashboard' | 'today' | 'upcoming' | 'pending' | 'archive' | 'clients' | 'services' | 'statistics' | 'agent' | 'settings'

const navigation = [
  { name: 'Astăzi', page: 'today' as PageType, icon: Calendar, count: 4 },
  { name: 'Următoarele', page: 'upcoming' as PageType, icon: Star },
  { name: 'În așteptare', page: 'pending' as PageType, icon: Clock, count: 3 },
  { name: 'Arhivă', page: 'archive' as PageType, icon: Archive },
]

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
  return (
    <div className={cn(
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
              className={cn(
                'flex items-center w-full px-3 py-2 rounded-2xl group transition-colors',
                currentPage === item.page
                  ? 'bg-secondary/10 text-primary border border-border'
                  : 'text-secondary hover:text-primary hover:bg-card-hover'
              )}
            >
              <item.icon className="h-5 w-5 mr-3" />
              <span>{item.name}</span>
              {item.count && (
                <span className={cn(
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
                className={cn(
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
        <Image
          src="https://images.unsplash.com/photo-1544005313-94ddf0286df2?q=80&w=200&auto=format&fit=crop"
          alt="user"
          width={32}
          height={32}
          className="w-8 h-8 rounded-full object-cover"
        />
        <div className="ml-2">
          <div className="text-sm font-medium text-primary">Alexandra I.</div>
          <div className="text-xs text-secondary">salon.example@email.com</div>
        </div>
      </div>
    </div>
  )
}