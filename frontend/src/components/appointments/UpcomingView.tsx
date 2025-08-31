'use client'

import {
  Star,
  Calendar,
  User,
  Phone,
  Eye,
  Menu
} from 'lucide-react'
import { cn } from '@/lib/utils'

interface UpcomingViewProps {
  isMobile?: boolean
  onMobileToggle?: () => void
}

export default function UpcomingView({ isMobile, onMobileToggle }: UpcomingViewProps) {
  const upcomingAppointments = [
    {
      id: '1',
      date: '2025-02-01',
      time: '10:00',
      client: 'Bogdan Mihai',
      phone: '+40 725 ***345',
      service: 'Tunsoare + Styling',
      status: 'confirmed',
      daysUntil: 1
    },
    {
      id: '2',
      date: '2025-02-01',
      time: '14:30',
      client: 'Cristina Popescu',
      phone: '+40 726 ***678',
      service: 'Tratament Păr',
      status: 'confirmed',
      daysUntil: 1
    },
    {
      id: '3',
      date: '2025-02-03',
      time: '09:15',
      client: 'Daniel Ionescu',
      phone: '+40 727 ***901',
      service: 'Barbă Completă',
      status: 'confirmed',
      daysUntil: 3
    },
    {
      id: '4',
      date: '2025-02-05',
      time: '11:00',
      client: 'Elena Radu',
      phone: '+40 728 ***234',
      service: 'Pachet Premium',
      status: 'confirmed',
      daysUntil: 5
    },
    {
      id: '5',
      date: '2025-02-07',
      time: '16:00',
      client: 'Florin Georgescu',
      phone: '+40 729 ***567',
      service: 'Tunsoare Clasică',
      status: 'confirmed',
      daysUntil: 7
    }
  ]

  const groupedAppointments = upcomingAppointments.reduce((groups, appointment) => {
    const key = appointment.date
    if (!groups[key]) {
      groups[key] = []
    }
    groups[key].push(appointment)
    return groups
  }, {} as Record<string, typeof upcomingAppointments>)

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr)
    return date.toLocaleDateString('ro-RO', { 
      weekday: 'long', 
      day: 'numeric', 
      month: 'long' 
    })
  }

  const getDaysText = (days: number) => {
    if (days === 1) return 'Mâine'
    if (days === 7) return 'Săptămâna viitoare'
    return `În ${days} zile`
  }

  return (
    <div className="flex-1 flex flex-col bg-card h-full">
      {/* Header */}
      <div className="p-6 border-b border-border">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            {isMobile && (
              <button 
                onClick={onMobileToggle}
                className="p-2 text-secondary hover:text-primary rounded-2xl hover:bg-card-hover transition-colors"
              >
                <Menu className="w-5 h-5" />
              </button>
            )}
            <Star className="w-8 h-8 text-secondary" />
            <div>
              <h1 className="text-3xl font-bold text-primary">Următoarele</h1>
              <p className="text-base text-secondary">
                Programări viitoare ({upcomingAppointments.length})
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-6">
        <div className="space-y-6">
          {Object.entries(groupedAppointments).map(([date, appointments]) => (
            <div key={date}>
              <div className="sticky top-0 bg-card z-10 pb-2">
                <h2 className="font-semibold text-primary text-lg">{formatDate(date)}</h2>
                <p className="text-sm text-secondary">{getDaysText(appointments[0].daysUntil)}</p>
              </div>
              
              <div className="space-y-3">
                {appointments.map((appointment) => (
                  <div key={appointment.id} className="bg-background rounded-2xl p-4 border border-border hover:bg-card-hover transition-colors">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-4">
                        <div className="text-center">
                          <div className="text-lg font-bold text-primary">{appointment.time}</div>
                        </div>
                        
                        <div className="w-px h-12 bg-border"></div>
                        
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <User className="w-4 h-4 text-secondary" />
                            <span className="font-medium text-primary">{appointment.client}</span>
                          </div>
                          <div className="flex items-center gap-2 mb-1">
                            <Phone className="w-4 h-4 text-secondary" />
                            <span className="text-sm text-secondary">{appointment.phone}</span>
                          </div>
                          <div className="text-sm text-primary">{appointment.service}</div>
                        </div>
                      </div>
                      
                      <div className="flex items-center gap-3">
                        <span className="inline-flex items-center px-2 py-1 rounded-2xl text-xs font-medium border bg-secondary/20 text-primary border-border">
                          Confirmat
                        </span>
                        <button className="p-2 text-secondary hover:text-primary rounded-2xl hover:bg-card-hover transition-colors">
                          <Eye className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>

        {upcomingAppointments.length === 0 && (
          <div className="text-center py-12">
            <Star className="w-12 h-12 text-secondary mx-auto mb-4" />
            <h3 className="text-lg font-medium text-primary mb-2">Nu există programări viitoare</h3>
            <p className="text-secondary">Toate programările sunt pentru astăzi sau în trecut.</p>
          </div>
        )}
      </div>
    </div>
  )
}