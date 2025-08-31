'use client'

import {
  Clock,
  User,
  Phone,
  Calendar,
  CheckCircle,
  XCircle,
  Menu
} from 'lucide-react'
import { cn } from '@/lib/utils'

interface PendingViewProps {
  isMobile?: boolean
  onMobileToggle?: () => void
}

export default function PendingView({ isMobile, onMobileToggle }: PendingViewProps) {
  const pendingAppointments = [
    {
      id: '1',
      date: '2025-02-02',
      time: '15:00',
      client: 'Marius Constantinescu',
      phone: '+40 730 ***123',
      service: 'Tunsoare Clasică',
      requestedAt: '2025-01-31 14:20',
      priority: 'normal'
    },
    {
      id: '2',
      date: '2025-02-03',
      time: '11:30',
      client: 'Andreea Popescu',
      phone: '+40 731 ***456',
      service: 'Tratament + Coafură',
      requestedAt: '2025-01-31 10:15',
      priority: 'high'
    },
    {
      id: '3',
      date: '2025-02-01',
      time: '16:45',
      client: 'Gabriel Mihai',
      phone: '+40 732 ***789',
      service: 'Barbă + Mustață',
      requestedAt: '2025-01-30 18:30',
      priority: 'urgent'
    }
  ]

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr)
    return date.toLocaleDateString('ro-RO', { 
      weekday: 'short', 
      day: 'numeric', 
      month: 'short' 
    })
  }

  const formatDateTime = (dateStr: string) => {
    const date = new Date(dateStr)
    return date.toLocaleDateString('ro-RO', { 
      day: '2-digit', 
      month: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const getPriorityBadge = (priority: string) => {
    const styles = {
      urgent: 'bg-secondary/20 text-primary border-border',
      high: 'bg-secondary/20 text-primary border-border',
      normal: 'bg-secondary/20 text-secondary border-border'
    }
    
    const labels = {
      urgent: 'Urgent',
      high: 'Prioritate',
      normal: 'Normal'
    }
    
    return (
      <span className={cn(
        'inline-flex items-center px-2 py-1 rounded-2xl text-xs font-medium border',
        styles[priority as keyof typeof styles] || 'bg-secondary/20 text-secondary border-border'
      )}>
        {labels[priority as keyof typeof labels] || priority}
      </span>
    )
  }

  const sortedAppointments = [...pendingAppointments].sort((a, b) => {
    const priorityOrder = { urgent: 3, high: 2, normal: 1 }
    return priorityOrder[b.priority as keyof typeof priorityOrder] - priorityOrder[a.priority as keyof typeof priorityOrder]
  })

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
            <Clock className="w-8 h-8 text-secondary" />
            <div>
              <h1 className="text-3xl font-bold text-primary">În Așteptare</h1>
              <p className="text-base text-secondary">
                Programări ce necesită confirmare ({pendingAppointments.length})
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2 px-3 py-1 bg-background rounded-2xl border border-border">
            <div className="w-2 h-2 bg-secondary rounded-full animate-pulse"></div>
            <span className="text-sm text-secondary">Necesită atenție</span>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-6">
        <div className="space-y-4">
          {sortedAppointments.map((appointment) => (
            <div key={appointment.id} className="bg-background rounded-2xl p-4 border border-border hover:bg-card-hover transition-colors">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-4">
                  <div className="text-center">
                    <div className="text-sm text-secondary">{formatDate(appointment.date)}</div>
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
                
                <div className="flex items-center gap-2">
                  {getPriorityBadge(appointment.priority)}
                </div>
              </div>

              <div className="flex items-center justify-between pt-3 border-t border-border">
                <div className="text-xs text-secondary">
                  Cerere: {formatDateTime(appointment.requestedAt)}
                </div>
                <div className="flex items-center gap-2">
                  <button className="flex items-center px-3 py-1 bg-background text-secondary border border-border rounded-2xl hover:text-primary hover:border-secondary transition-colors">
                    <CheckCircle className="w-4 h-4 mr-1" />
                    Confirmă
                  </button>
                  <button className="flex items-center px-3 py-1 bg-background text-secondary border border-border rounded-2xl hover:text-primary hover:border-secondary transition-colors">
                    <XCircle className="w-4 h-4 mr-1" />
                    Respinge
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>

        {pendingAppointments.length === 0 && (
          <div className="text-center py-12">
            <Clock className="w-12 h-12 text-secondary mx-auto mb-4" />
            <h3 className="text-lg font-medium text-primary mb-2">Nu există programări în așteptare</h3>
            <p className="text-secondary">Toate programările au fost procesate.</p>
          </div>
        )}
      </div>
    </div>
  )
}