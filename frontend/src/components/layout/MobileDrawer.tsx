'use client'

import clsx from "clsx"

import { 
  LayoutDashboard, 
  Calendar, 
  Users, 
  Scissors, 
  TrendingUp, 
  Mic,
  X 
} from 'lucide-react'


type PageType = 'dashboard' | 'today' | 'upcoming' | 'pending' | 'archive' | 'clients' | 'services' | 'statistics' | 'agent' | 'settings'

interface MobileDrawerProps {
  isOpen: boolean
  onClose: () => void
  currentPage?: PageType
  onPageChange?: (page: PageType) => void
}

const navigation = [
  { name: 'Dashboard', key: 'dashboard', icon: LayoutDashboard },
  { name: 'Clienți', key: 'clients', icon: Users },
  { name: 'Servicii', key: 'services', icon: Scissors },
  { name: 'Statistici', key: 'statistics', icon: TrendingUp },
  { name: 'Agent Vocal', key: 'agent', icon: Mic },
  { name: 'Setări', key: 'settings', icon: Calendar },
]

export default function MobileDrawer({ isOpen, onClose, currentPage = 'dashboard', onPageChange }: MobileDrawerProps) {
  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-40">
      <div 
        className="absolute inset-0 bg-black/50" 
        onClick={onClose}
      />
      <div className="absolute left-0 top-0 bottom-0 w-72 bg-card border-r border-border p-4" data-drawer="mobile">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <div className="grid place-items-center w-8 h-8 rounded-2xl bg-secondary/10 text-primary border border-border tracking-tight text-sm font-semibold">
              VB
            </div>
            <div className="text-sm font-semibold tracking-tight text-primary">Voice Booking</div>
          </div>
          <button 
            onClick={onClose}
            className="p-2 rounded-2xl border border-border hover:border-border-hover hover:bg-card-hover text-secondary hover:text-primary transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
        
        <nav className="space-y-1">
          {navigation.map((item) => (
            <button
              key={item.name}
              className={clsx(
                'w-full flex items-center gap-3 px-3 py-2 rounded-2xl text-sm border transition-colors text-left',
                currentPage === item.key
                  ? 'bg-card-hover border-border text-primary'
                  : 'text-secondary hover:text-primary hover:bg-card-hover border-transparent hover:border-border'
              )}
              onClick={() => {
                if (onPageChange) {
                  onPageChange(item.key as PageType)
                }
                onClose() // Auto-close drawer after navigation
              }}
            >
              <item.icon className={clsx(
                'w-4.5 h-4.5',
                currentPage === item.key ? 'text-primary' : ''
              )} />
              {item.name}
            </button>
          ))}
        </nav>
      </div>
    </div>
  )
}