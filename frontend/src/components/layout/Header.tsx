'use client'

import { Menu, Calendar, Bell, Plus } from 'lucide-react'

interface HeaderProps {
  onMobileMenuClick: () => void
}

export default function Header({ onMobileMenuClick }: HeaderProps) {
  const currentDate = new Date().toLocaleDateString('ro-RO', {
    weekday: 'long',
    day: 'numeric',
    month: 'short',
    year: 'numeric'
  })

  return (
    <>
      {/* Mobile Topbar */}
      <div className="md:hidden flex items-center justify-between px-4 h-14 border-b border-border bg-background/80 backdrop-blur">
        <button 
          onClick={onMobileMenuClick}
          className="p-2 rounded-md border border-border hover:border-border-hover hover:bg-card-hover text-secondary hover:text-primary"
        >
          <Menu className="w-5 h-5" />
        </button>
        <div className="text-sm font-semibold tracking-tight text-primary">Tablou de Bord</div>
        <div></div>
      </div>

      {/* Main Header */}
      <header className="sticky top-0 z-30 bg-background/75 backdrop-blur border-b border-border">
        <div className="flex items-center justify-between px-6 h-16">
          <div className="flex items-center gap-3">
            <h1 className="text-lg md:text-xl font-semibold tracking-tight text-primary">Tablou de Bord</h1>
            <span className="hidden md:inline-flex items-center gap-2 text-xs text-secondary border border-border rounded-md px-2 py-1">
              <Calendar className="w-3.5 h-3.5" />
              {currentDate}
            </span>
          </div>
          
          <div className="flex items-center gap-3">
            <button className="relative p-2 rounded-md border border-border hover:border-border-hover hover:bg-card-hover text-secondary hover:text-primary transition-colors" title="Notificări">
              <Bell className="w-5 h-5" />
              <span className="absolute -top-0.5 -right-0.5 w-2.5 h-2.5 bg-accent rounded-full ring-2 ring-background"></span>
            </button>
            
            <button className="button-primary">
              <Plus className="w-4.5 h-4.5" />
              Adaugă Programare Manuală
            </button>
          </div>
        </div>
      </header>
    </>
  )
}