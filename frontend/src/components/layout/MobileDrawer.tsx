'use client'

import { 
  LayoutDashboard, 
  Calendar, 
  Users, 
  Scissors, 
  TrendingUp, 
  Mic,
  X 
} from 'lucide-react'
import { cn } from '@/lib/utils'

interface MobileDrawerProps {
  isOpen: boolean
  onClose: () => void
}

const navigation = [
  { name: 'Dashboard', href: '#', icon: LayoutDashboard, current: true },
  { name: 'Calendar', href: '#', icon: Calendar, current: false },
  { name: 'Clienți', href: '#', icon: Users, current: false },
  { name: 'Servicii & Prețuri', href: '#', icon: Scissors, current: false },
  { name: 'Statistici', href: '#', icon: TrendingUp, current: false },
  { name: 'Setări Agent Vocal', href: '#', icon: Mic, current: false },
]

export default function MobileDrawer({ isOpen, onClose }: MobileDrawerProps) {
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
            <a
              key={item.name}
              href={item.href}
              className={cn(
                'flex items-center gap-3 px-3 py-2 rounded-2xl text-sm border transition-colors',
                item.current
                  ? 'bg-card-hover border-border'
                  : 'text-secondary hover:text-primary hover:bg-card-hover border-transparent hover:border-border'
              )}
              onClick={onClose}
            >
              <item.icon className={cn(
                'w-4.5 h-4.5',
                item.current ? 'text-primary' : ''
              )} />
              {item.name}
            </a>
          ))}
        </nav>
      </div>
    </div>
  )
}