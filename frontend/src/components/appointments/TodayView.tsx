'use client'

import clsx from "clsx"
import { useEffect } from 'react'
import { useAppointments } from '../../hooks/useAppointments'
import { AppointmentStatus } from '../../types/appointment'

import {
  Calendar,
  Clock,
  User,
  Phone,
  Eye,
  Menu
} from 'lucide-react'


interface TodayViewProps {
  isMobile?: boolean
  onMobileToggle?: () => void
}

export default function TodayView({ isMobile, onMobileToggle }: TodayViewProps) {
  const { appointments, isLoading, error, fetchAppointments } = useAppointments()
  
  // Fetch appointments on mount
  useEffect(() => {
    fetchAppointments()
  }, [fetchAppointments])
  
  // Filter appointments for today
  const today = new Date().toISOString().split('T')[0]
  const todayAppointments = appointments.filter(apt => apt.date === today).map(apt => ({
    id: apt.id,
    time: apt.time,
    client: apt.client_name,
    phone: apt.phone,
    service: apt.service,
    status: apt.status,
    duration: apt.duration
  }))

  const getStatusBadge = (status: string) => {
    const styles = {
      'confirmed': 'bg-secondary/20 text-primary border-border',
      'in-progress': 'bg-secondary/20 text-primary border-border',
      'completed': 'bg-secondary/20 text-secondary border-border'
    }
    
    const labels = {
      'confirmed': 'Confirmat',
      'in-progress': 'În progres',
      'completed': 'Finalizat'
    }
    
    return (
      <span className={clsx(
        'inline-flex items-center px-2 py-1 rounded-2xl text-xs font-medium border',
        styles[status as keyof typeof styles] || 'bg-secondary/20 text-secondary border-border'
      )}>
        {labels[status as keyof typeof labels] || status}
      </span>
    )
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
            <Calendar className="w-8 h-8 text-secondary" />
            <div>
              <h1 className="text-3xl font-bold text-primary">Astăzi</h1>
              <p className="text-base text-secondary">
                Programări pentru {new Date().toLocaleDateString('ro-RO', { weekday: 'long', day: 'numeric', month: 'long' })}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2 px-3 py-1 bg-background rounded-2xl border border-border">
            <div className="w-2 h-2 bg-secondary rounded-full animate-pulse"></div>
            <span className="text-sm text-primary">Live</span>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-6">
        {isLoading ? (
          <div className="text-center py-12">
            <div className="w-8 h-8 border-2 border-secondary border-t-primary rounded-full animate-spin mx-auto mb-4"></div>
            <p className="text-secondary">Se încarcă programările...</p>
          </div>
        ) : error ? (
          <div className="text-center py-12">
            <Calendar className="w-12 h-12 text-secondary mx-auto mb-4" />
            <h3 className="text-lg font-medium text-primary mb-2">Eroare la încărcarea datelor</h3>
            <p className="text-secondary">{error}</p>
          </div>
        ) : (
        <div className="space-y-4">
          {todayAppointments.map((appointment) => (
            <div key={appointment.id} className="bg-background rounded-2xl p-4 border border-border hover:bg-card-hover transition-colors">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className="text-center">
                    <div className="text-lg font-bold text-primary">{appointment.time}</div>
                    <div className="text-xs text-secondary">{appointment.duration}</div>
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
                  {getStatusBadge(appointment.status)}
                  <button className="p-2 text-secondary hover:text-primary rounded-2xl hover:bg-card-hover transition-colors">
                    <Eye className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>

          {todayAppointments.length === 0 && (
            <div className="text-center py-12">
              <Calendar className="w-12 h-12 text-secondary mx-auto mb-4" />
              <h3 className="text-lg font-medium text-primary mb-2">Nu există programări pentru astăzi</h3>
              <p className="text-secondary">Ziua liberă!</p>
            </div>
          )}
        </div>
        )}
      </div>
    </div>
  )
}