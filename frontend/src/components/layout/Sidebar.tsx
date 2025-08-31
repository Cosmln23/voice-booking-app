'use client'

import { 
  LayoutDashboard, 
  Calendar, 
  Users, 
  Scissors, 
  TrendingUp, 
  Mic, 
  LogOut,
  ChevronLeft,
  ChevronRight
} from 'lucide-react'
import { cn } from '@/lib/utils'
import Image from 'next/image'

const navigation = [
  { name: 'Dashboard', href: '#', icon: LayoutDashboard, current: true },
  { name: 'Calendar', href: '#', icon: Calendar, current: false },
  { name: 'Clienți', href: '#', icon: Users, current: false },
  { name: 'Servicii & Prețuri', href: '#', icon: Scissors, current: false },
  { name: 'Statistici', href: '#', icon: TrendingUp, current: false },
  { name: 'Setări Agent Vocal', href: '#', icon: Mic, current: false },
]

interface SidebarProps {
  isOpen: boolean
  onToggle: () => void
}

export default function Sidebar({ isOpen, onToggle }: SidebarProps) {
  return (
    <aside className={cn(
      "hidden md:flex md:flex-col md:w-72 md:shrink-0 relative",
      "border-r border-border bg-card backdrop-blur-lg",
      "transition-transform duration-300 ease-in-out",
      isOpen ? "translate-x-0" : "-translate-x-full"
    )}>
      {/* Logo */}
      <div className="flex items-center gap-3 px-5 h-16 border-b border-border">
        <div className="grid place-items-center w-8 h-8 rounded-md bg-accent/10 text-accent border border-accent/30 tracking-tight text-sm font-semibold">
          VB
        </div>
        <div className="flex flex-col">
          <span className="text-sm font-semibold tracking-tight text-primary">Voice Booking</span>
          <span className="text-[11px] text-secondary">Admin Dashboard</span>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-1">
        {navigation.map((item) => (
          <a
            key={item.name}
            href={item.href}
            className={cn(
              'group flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium border transition-colors',
              item.current
                ? 'bg-card-hover border-border hover:border-border-hover'
                : 'text-secondary hover:text-primary hover:bg-card-hover border-transparent hover:border-border'
            )}
          >
            <item.icon className={cn(
              'w-4.5 h-4.5',
              item.current ? 'text-accent' : ''
            )} />
            <span>{item.name}</span>
          </a>
        ))}
      </nav>

      {/* Profile */}
      <div className="mt-auto p-4 border-t border-border">
        <div className="flex items-center gap-3">
          <Image
            src="https://images.unsplash.com/photo-1544005313-94ddf0286df2?q=80&w=200&auto=format&fit=crop"
            alt="user"
            width={36}
            height={36}
            className="w-9 h-9 rounded-md object-cover border border-border"
          />
          <div className="flex-1">
            <div className="text-sm font-medium text-primary">Alexandra I.</div>
            <div className="text-xs text-secondary">Owner</div>
          </div>
          <button 
            className="p-2 rounded-md hover:bg-card-hover border border-border hover:border-border-hover transition-colors text-secondary hover:text-primary" 
            title="Logout"
          >
            <LogOut className="w-4.5 h-4.5" />
          </button>
        </div>
      </div>

      {/* Toggle Button */}
      <button
        onClick={onToggle}
        className={cn(
          "absolute top-1/2 -translate-y-1/2 -right-3 z-50",
          "w-6 h-6 rounded-full bg-card border border-border",
          "flex items-center justify-center",
          "text-secondary hover:text-primary hover:bg-card-hover hover:border-border-hover",
          "transition-colors duration-200"
        )}
        aria-label="Toggle sidebar"
      >
        {isOpen ? (
          <ChevronLeft className="w-4 h-4" />
        ) : (
          <ChevronRight className="w-4 h-4" />
        )}
      </button>
    </aside>
  )
}