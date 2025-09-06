'use client'

import { useState, useEffect } from 'react'
import { 
  X, 
  Calendar, 
  Plus,
  Settings,
  RefreshCw,
  CheckCircle,
  AlertCircle,
  Clock,
  User,
  Phone,
  ExternalLink
} from 'lucide-react'
import { useCalendar } from '../../hooks/useCalendar'
import { useAppointments } from '../../hooks/useAppointments'
import CalendarSetupModal from './CalendarSetupModal'

interface CalendarModalProps {
  isOpen: boolean
  onClose: () => void
  selectedDate?: string
}

export default function CalendarModal({ isOpen, onClose, selectedDate = new Date().toISOString().split('T')[0] }: CalendarModalProps) {
  const [showSetup, setShowSetup] = useState(false)
  const [selectedDay, setSelectedDay] = useState(selectedDate)
  const { calendarInfo, fetchCalendarInfo, loading: calendarLoading } = useCalendar()
  const { appointments, fetchAppointments } = useAppointments()

  useEffect(() => {
    if (isOpen) {
      fetchCalendarInfo()
      fetchAppointments()
    }
  }, [isOpen, fetchCalendarInfo, fetchAppointments])

  // Filter appointments for selected day
  const dayAppointments = appointments.filter(apt => apt.date === selectedDay)

  // Generate calendar days for current month
  const generateCalendarDays = () => {
    const today = new Date()
    const year = today.getFullYear()
    const month = today.getMonth()
    
    const firstDay = new Date(year, month, 1)
    const lastDay = new Date(year, month + 1, 0)
    const startDate = new Date(firstDay)
    startDate.setDate(startDate.getDate() - firstDay.getDay())
    
    const days = []
    const current = new Date(startDate)
    
    for (let i = 0; i < 42; i++) {
      const dayString = current.toISOString().split('T')[0]
      const dayAppointments = appointments.filter(apt => apt.date === dayString)
      
      days.push({
        date: dayString,
        day: current.getDate(),
        isCurrentMonth: current.getMonth() === month,
        isToday: dayString === new Date().toISOString().split('T')[0],
        isSelected: dayString === selectedDay,
        appointmentCount: dayAppointments.length,
        hasAppointments: dayAppointments.length > 0
      })
      
      current.setDate(current.getDate() + 1)
    }
    
    return days
  }

  const calendarDays = generateCalendarDays()
  const currentMonth = new Date().toLocaleDateString('ro-RO', { month: 'long', year: 'numeric' })

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'confirmed': return 'text-blue-600 bg-blue-50'
      case 'in-progress': return 'text-amber-600 bg-amber-50' 
      case 'completed': return 'text-green-600 bg-green-50'
      case 'pending': return 'text-orange-600 bg-orange-50'
      case 'cancelled': return 'text-red-600 bg-red-50'
      default: return 'text-gray-600 bg-gray-50'
    }
  }

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'confirmed': return 'Confirmat'
      case 'in-progress': return 'În progres'
      case 'completed': return 'Finalizat'
      case 'pending': return 'În așteptare'
      case 'cancelled': return 'Anulat'
      default: return status
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
      <div className="bg-card rounded-3xl shadow-xl w-full max-w-6xl max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-border">
          <div className="flex items-center gap-3">
            <Calendar className="w-8 h-8 text-secondary" />
            <div>
              <h2 className="text-2xl font-bold text-primary">Agenda Zilei</h2>
              <p className="text-secondary">{currentMonth}</p>
            </div>
          </div>
          
          <div className="flex items-center gap-3">
            {/* Calendar Status */}
            {calendarInfo ? (
              <div className="flex items-center gap-2 px-3 py-1 bg-green-50 text-green-700 rounded-lg border border-green-200">
                <CheckCircle className="w-4 h-4" />
                <span className="text-sm font-medium">
                  Calendar Sincronizat
                </span>
                <button 
                  onClick={() => setShowSetup(true)}
                  className="ml-2 p-1 hover:bg-green-100 rounded"
                >
                  <Settings className="w-4 h-4" />
                </button>
              </div>
            ) : (
              <button
                onClick={() => setShowSetup(true)}
                className="flex items-center gap-2 px-4 py-2 bg-blue-50 text-blue-700 rounded-lg border border-blue-200 hover:bg-blue-100 transition-colors"
              >
                <Plus className="w-4 h-4" />
                <span className="font-medium">Configurează Calendar</span>
              </button>
            )}
            
            <button
              onClick={onClose}
              className="p-2 hover:bg-card-hover rounded-lg transition-colors"
            >
              <X className="w-6 h-6 text-secondary" />
            </button>
          </div>
        </div>

        <div className="flex h-[calc(90vh-120px)]">
          {/* Calendar View */}
          <div className="flex-1 p-6">
            {/* Calendar Header */}
            <div className="grid grid-cols-7 gap-1 mb-4">
              {['Du', 'Lu', 'Ma', 'Mi', 'Jo', 'Vi', 'Sâ'].map(day => (
                <div key={day} className="p-2 text-center text-sm font-medium text-secondary">
                  {day}
                </div>
              ))}
            </div>

            {/* Calendar Grid */}
            <div className="grid grid-cols-7 gap-1">
              {calendarDays.map((day, index) => (
                <button
                  key={index}
                  onClick={() => setSelectedDay(day.date)}
                  className={`
                    relative p-3 rounded-lg text-sm transition-all duration-200
                    ${!day.isCurrentMonth 
                      ? 'text-gray-400 hover:bg-gray-50' 
                      : day.isSelected
                        ? 'bg-blue-500 text-white shadow-md'
                        : day.isToday
                          ? 'bg-blue-50 text-blue-700 border border-blue-200'
                          : 'text-primary hover:bg-card-hover'
                    }
                    ${day.hasAppointments && !day.isSelected ? 'font-semibold' : ''}
                  `}
                >
                  <span>{day.day}</span>
                  {day.hasAppointments && (
                    <div className={`
                      absolute top-1 right-1 w-2 h-2 rounded-full
                      ${day.isSelected ? 'bg-white' : 'bg-blue-500'}
                    `} />
                  )}
                  {day.appointmentCount > 0 && (
                    <div className={`
                      absolute -bottom-1 left-1/2 transform -translate-x-1/2
                      text-xs px-1 rounded-full min-w-[16px] h-4 flex items-center justify-center
                      ${day.isSelected 
                        ? 'bg-white text-blue-500' 
                        : 'bg-blue-500 text-white'
                      }
                    `}>
                      {day.appointmentCount}
                    </div>
                  )}
                </button>
              ))}
            </div>

            {/* Google Calendar Integration Status */}
            {calendarInfo && (
              <div className="mt-6 p-4 bg-background rounded-lg border border-border">
                <div className="flex items-center gap-3 mb-3">
                  <ExternalLink className="w-5 h-5 text-secondary" />
                  <h3 className="font-medium text-primary">Sincronizare Google Calendar</h3>
                </div>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-secondary">Calendar:</span>
                    <p className="font-medium text-primary">{calendarInfo.calendar_name}</p>
                  </div>
                  <div>
                    <span className="text-secondary">Ultima sincronizare:</span>
                    <p className="font-medium text-primary">
                      {calendarInfo.last_sync 
                        ? new Date(calendarInfo.last_sync).toLocaleString('ro-RO')
                        : 'Niciodată'
                      }
                    </p>
                  </div>
                  <div>
                    <span className="text-secondary">Creare automată:</span>
                    <p className="font-medium text-primary">
                      {calendarInfo.auto_create_events ? 'Activată' : 'Dezactivată'}
                    </p>
                  </div>
                  <div>
                    <span className="text-secondary">Fus orar:</span>
                    <p className="font-medium text-primary">{calendarInfo.timezone}</p>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Day Details */}
          <div className="w-80 border-l border-border p-6">
            <div className="mb-6">
              <h3 className="text-lg font-semibold text-primary mb-2">
                {new Date(selectedDay).toLocaleDateString('ro-RO', { 
                  weekday: 'long', 
                  day: 'numeric', 
                  month: 'long' 
                })}
              </h3>
              {dayAppointments.length > 0 ? (
                <p className="text-secondary">
                  {dayAppointments.length} {dayAppointments.length === 1 ? 'programare' : 'programări'}
                </p>
              ) : (
                <p className="text-secondary">Nu există programări</p>
              )}
            </div>

            {/* Appointments List */}
            <div className="space-y-3 max-h-[400px] overflow-y-auto">
              {dayAppointments.map((appointment) => (
                <div key={appointment.id} className="bg-background rounded-lg p-4 border border-border">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-2">
                      <Clock className="w-4 h-4 text-secondary" />
                      <span className="font-medium text-primary">{appointment.time}</span>
                    </div>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(appointment.status)}`}>
                      {getStatusLabel(appointment.status)}
                    </span>
                  </div>
                  
                  <div className="space-y-2 text-sm">
                    <div className="flex items-center gap-2">
                      <User className="w-4 h-4 text-secondary" />
                      <span className="text-primary">{appointment.client_name}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Phone className="w-4 h-4 text-secondary" />
                      <span className="text-secondary">{appointment.phone}</span>
                    </div>
                    <div className="text-primary font-medium">
                      {appointment.service}
                    </div>
                    <div className="text-secondary text-xs">
                      Durată: {appointment.duration}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Setup Modal */}
      {showSetup && (
        <CalendarSetupModal 
          isOpen={showSetup}
          onClose={() => setShowSetup(false)}
          onSuccess={() => {
            setShowSetup(false)
            fetchCalendarInfo()
          }}
          existingCalendar={calendarInfo}
        />
      )}
    </div>
  )
}