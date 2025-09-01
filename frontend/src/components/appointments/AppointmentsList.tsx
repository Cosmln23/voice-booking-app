'use client'

import { clsx } from "clsx"

import { useState, useEffect } from 'react'
import { Search, Filter, Bell, ChevronLeft, ChevronRight, Mic, Activity, Calendar, X, Menu, User, Phone, Mail, Clock as ClockIcon, Plus, Ban, LayoutDashboard } from 'lucide-react'

import Badge from '../ui/Badge'
import { useAppointments } from '../../hooks'
import type { Appointment, AppointmentStatus } from '../../types'

// Extended appointment interface with client details for compatibility
interface AppointmentWithDetails extends Omit<Appointment, 'duration'> {
  duration?: string
  clientName?: string
  clientPhone?: string
  clientEmail?: string
  clientNotes?: string
  lastVisit?: string
  preferences?: string[]
  preview?: string
}

interface AppointmentsListProps {
  selectedAppointment: string | null
  onSelectAppointment: (id: string) => void
  isMobile?: boolean
  onMobileToggle?: () => void
}

// Extended appointment interface with client details
interface AppointmentWithDetails extends Appointment {
  clientPhone?: string
  clientEmail?: string
  clientNotes?: string
  duration?: string
  price?: string
  lastVisit?: string
  preferences?: string[]
}

const convertedAppointments: AppointmentWithDetails[] = [
  {
    id: '5',
    clientName: 'Mihai Georgescu',
    service: 'Tuns + Spălat',
    time: '08:00',
    status: 'completed',
    type: 'voice',
    preview: 'Serviciu complet finalizat. Client mulțumit, programare următoare în 3 săptămâni.',
    clientPhone: '+40 744 555 123',
    clientEmail: 'mihai.georgescu@email.com',
    duration: '40 min',
    price: '55 RON',
    lastVisit: '11 Octombrie 2024',
    clientNotes: 'Client fidel, vine regulat la 3 săptămâni.',
    preferences: ['Tuns clasic', 'Spălat cu șampon anti-mătreață', 'Styling minimal']
  },
  {
    id: '1',
    clientName: 'Ion Popescu',
    service: 'Tuns + Barbă',
    time: '10:30',
    status: 'completed',
    type: 'voice',
    preview: 'Programare finalizată pentru tuns și aranjat barbă. Client obișnuit, preferințe cunoscute.',
    clientPhone: '+40 123 456 789',
    clientEmail: 'ion.popescu@email.com',
    duration: '45 min',
    price: '85 RON',
    lastVisit: '15 Aprilie 2024',
    clientNotes: 'Client obișnuit, preferă tunsoarea scurtă pe lateral și barbă aranjată clasic.',
    preferences: ['Tunsoare scurtă', 'Barbă îngrijită', 'Fără gel']
  },
  {
    id: '2',
    clientName: 'Maria Ionescu',
    service: 'Tuns + Vopsit',
    time: '11:15',
    status: 'in-progress',
    type: 'voice',
    preview: 'În desfășurare - tuns complet și vopsire cu nuanța preferată. Estimat 2 ore.',
    clientPhone: '+40 987 654 321',
    clientEmail: 'maria.ionescu@email.com',
    duration: '2 ore',
    price: '180 RON',
    lastVisit: '8 Martie 2024',
    clientNotes: 'Preferă culori naturale, are părul sensibil.',
    preferences: ['Culori naturale', 'Tratamente hidratante', 'Fără amoniac']
  },
  {
    id: '3',
    clientName: 'Alexandru Marin',
    service: 'Tuns simplu',
    time: '14:00',
    status: 'confirmed',
    type: 'manual',
    preview: 'Următorul client - programare confirmată. Client nou, fără istoric anterior.',
    clientPhone: '+40 755 123 456',
    clientEmail: 'alex.marin@email.com',
    duration: '30 min',
    price: '45 RON',
    lastVisit: null,
    clientNotes: 'Client nou, prima vizită.',
    preferences: []
  },
  {
    id: '4',
    clientName: 'Elena Vasile',
    service: 'Coafură ocazie',
    time: '16:30',
    status: 'confirmed',
    type: 'voice',
    preview: 'Coafură pentru eveniment special. Discutat modelul preferat și accesoriile necesare.',
    clientPhone: '+40 731 987 654',
    clientEmail: 'elena.vasile@email.com',
    duration: '90 min',
    price: '150 RON',
    lastVisit: '20 Septembrie 2024',
    clientNotes: 'Preferă coafuri elegante pentru evenimente. Are părul lung și des.',
    preferences: ['Coafuri elegante', 'Fixativ puternic', 'Accesorii florale']
  },
]

const getStatusBadge = (status: string) => {
  switch (status) {
    case 'confirmed': return 'success'
    case 'pending': return 'warning'
    case 'in-progress': return 'info'
    case 'completed': return 'success'
    case 'cancelled': return 'error'
    default: return 'neutral'
  }
}

const getStatusText = (status: string) => {
  switch (status) {
    case 'confirmed': return 'Confirmat'
    case 'pending': return 'În așteptare'
    case 'in-progress': return 'În desfășurare'
    case 'completed': return 'Finalizat'
    case 'cancelled': return 'Anulat'
    default: return status
  }
}

export default function AppointmentsList({ selectedAppointment, onSelectAppointment, isMobile, onMobileToggle }: AppointmentsListProps) {
  const [showCalendar, setShowCalendar] = useState(false)
  const [showClientDetails, setShowClientDetails] = useState(false)
  const [selectedClient, setSelectedClient] = useState<AppointmentWithDetails | null>(null)
  const [showAddAppointment, setShowAddAppointment] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [statusFilter, setStatusFilter] = useState<AppointmentStatus | ''>('')

  // Use real API data
  const { 
    appointments, 
    total, 
    isLoading, 
    error, 
    fetchAppointments 
  } = useAppointments()

  // Fetch appointments on component mount and when filters change
  useEffect(() => {
    const today = new Date().toISOString().split('T')[0]
    fetchAppointments({
      date: today,
      status: statusFilter || undefined,
      limit: 50,
      offset: 0
    })
  }, [fetchAppointments, statusFilter])

  // Convert API appointments to component format for compatibility
  const convertedAppointments: AppointmentWithDetails[] = appointments.map(apt => ({
    id: apt.id,
    clientName: apt.client_name,
    service: apt.service,
    time: apt.time,
    status: apt.status,
    type: apt.type,
    preview: apt.notes || `${apt.service} pentru ${apt.client_name}`,
    clientPhone: apt.phone,
    clientEmail: '',
    clientNotes: apt.notes,
    duration: apt.duration,
    price: apt.price,
    date: apt.date,
    created_at: apt.created_at,
    updated_at: apt.updated_at,
    priority: apt.priority
  }))

  const handleShowClientDetails = (appointment: AppointmentWithDetails) => {
    setSelectedClient(appointment)
    setShowClientDetails(true)
  }

  // Function to identify next client (first upcoming confirmed appointment)
  const getNextClientId = (): string | null => {
    const upcomingAppointments = convertedAppointments.filter(
      apt => apt.status === 'confirmed' || apt.status === 'pending'
    )
    return upcomingAppointments.length > 0 ? upcomingAppointments[0].id : null
  }

  const nextClientId = getNextClientId()

  // Handle loading and error states
  if (isLoading && appointments.length === 0) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <Activity className="w-8 h-8 animate-spin mx-auto mb-2 text-primary" />
          <p className="text-secondary">Se încarcă programările...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <Ban className="w-8 h-8 mx-auto mb-2 text-destructive" />
          <p className="text-destructive mb-2">Eroare la încărcarea datelor</p>
          <button 
            onClick={() => fetchAppointments()}
            className="text-sm text-primary hover:underline"
          >
            Încearcă din nou
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className={clsx(
      "flex flex-col bg-card",
      isMobile ? "w-full h-full" : "flex-1 border-r border-border"
    )}>
      {/* Main Header */}
      <div className="px-4 py-2 border-b border-border bg-card">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            {isMobile && (
              <button 
                onClick={onMobileToggle}
                className="p-1.5 text-secondary hover:text-primary rounded-2xl hover:bg-card-hover transition-colors"
              >
                <Menu className="w-4 h-4" />
              </button>
            )}
            <LayoutDashboard className="w-4 h-4 text-primary" />
            <h1 className="text-3xl font-bold text-primary">Tablou de Bord</h1>
          </div>
          <div className="flex items-center gap-2">
            <p className="text-sm text-secondary">Astăzi, 12 Oct 2025</p>
            <button className="p-1.5 text-secondary hover:text-primary rounded-2xl hover:bg-card-hover transition-colors relative">
              <Bell className="h-4 w-4" />
              <div className="absolute -top-0.5 -right-0.5 w-2.5 h-2.5 bg-secondary rounded-full"></div>
            </button>
          </div>
        </div>
      </div>
      
      {/* Compact Status Bar */}
      <div className="px-4 py-2 border-b border-border bg-card">
        <div className="flex items-center justify-between text-sm">
          <div className="flex items-center gap-2">
            <Mic className="w-4 h-4 text-primary" />
            <span className="text-secondary">Agent Vocal</span>
            <div className="flex items-center gap-1">
              <div className="w-2 h-2 bg-secondary rounded-full animate-pulse"></div>
              <span className="text-primary font-medium">Activ</span>
            </div>
          </div>
          <div className="flex items-center gap-3 text-secondary">
            <span>Programări Azi 08:00–18:00</span>
            <span className="font-bold text-primary">14</span>
            <span className="text-primary">+2 față de ieri</span>
            <span>8 Finalizate</span>
            <span>6 Programate</span>
          </div>
        </div>
      </div>
      
      {/* Quick Actions */}
      <div className="px-4 py-2 border-b border-border bg-card">
        <div className="flex gap-2">
          <button 
            onClick={() => setShowAddAppointment(true)}
            className="flex items-center gap-2 px-3 py-1.5 bg-primary text-background rounded-2xl hover:bg-secondary transition-colors text-sm"
          >
            <Plus className="w-4 h-4" />
            Adaugă Programare
          </button>
          <button className="flex items-center gap-2 px-3 py-1.5 bg-secondary/10 text-secondary hover:text-primary hover:bg-secondary/20 rounded-2xl transition-colors text-sm">
            <Ban className="w-4 h-4" />
            Blochează Interval
          </button>
        </div>
      </div>
      
      {/* Search and Actions */}
      <div className="p-3 border-b border-border flex bg-card">
        <div className="relative flex-1">
          <input
            type="text"
            placeholder="Căutare programări..."
            className="w-full pl-9 pr-3 py-2 bg-card border border-border rounded-2xl text-base text-primary placeholder-secondary focus:outline-none focus:ring-1 focus:ring-secondary focus:border-secondary transition-colors"
          />
          <Search className="h-4 w-4 text-secondary absolute left-3 top-2.5" />
        </div>
        <button className="ml-2 p-2 text-secondary hover:text-primary rounded-2xl hover:bg-card-hover transition-colors">
          <Filter className="h-5 w-5" />
        </button>
      </div>
      
      {/* Agenda Header */}
      <div className="p-3 border-b border-border bg-card">
        <div className="flex items-center justify-between">
          <h3 className="text-base font-medium text-primary">Agenda Zilei</h3>
          <div className="flex items-center gap-2">
            <button className="p-1 text-secondary hover:text-primary rounded-2xl hover:bg-card-hover transition-colors">
              <ChevronLeft className="w-4 h-4" />
            </button>
            <button className="text-sm font-medium text-primary px-2 hover:bg-card-hover rounded-2xl transition-colors" onClick={() => setShowCalendar(!showCalendar)}>Astăzi</button>
            <button className="p-1 text-secondary hover:text-primary rounded-2xl hover:bg-card-hover transition-colors">
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
      
      {/* Appointments List */}
      <div className="flex-1 overflow-y-auto relative">
        {/* Timeline Line */}
        <div className="absolute left-6 top-0 bottom-0 w-px bg-border z-0"></div>
        {convertedAppointments.map((appointment) => {
          const isNextClient = appointment.id === nextClientId
          
          return (
            <div
              key={appointment.id}
              onClick={() => onSelectAppointment(appointment.id)}
              className={clsx(
                'border-b border-border px-4 py-3 cursor-pointer transition-colors relative',
                selectedAppointment === appointment.id
                  ? 'bg-secondary/10 border-l-2 border-l-secondary'
                  : isNextClient
                    ? 'bg-accent/10 border-l-4 border-l-accent hover:bg-accent/15'
                    : 'bg-card hover:bg-card-hover'
              )}
            >
            {/* Next Client Badge - Top Right Corner */}
            {isNextClient && (
              <div className="absolute top-2 right-4 text-primary text-xs font-medium">
                Următorul Client
              </div>
            )}
            
            {/* Timeline Dot */}
            <div className={clsx(
              "absolute left-[22px] top-4 w-3 h-3 rounded-full border-2 border-card z-10",
              isNextClient ? 'bg-accent border-accent animate-pulse' :
              appointment.status === 'completed' ? 'bg-secondary' :
              appointment.status === 'in-progress' ? 'bg-secondary' :
              'bg-secondary/50'
            )}></div>
            
            <div className="flex items-center mb-2 ml-6">
              <div className="flex items-center">
                <span className="text-sm text-secondary bg-secondary/10 px-2 py-1 rounded">{appointment.time}</span>
                <div className="w-3 h-px bg-border mx-2"></div>
                <span className="text-base font-medium text-primary">{appointment.clientName}</span>
              </div>
            </div>
            
            <div className="text-base font-medium text-primary mb-2 truncate ml-18">
              {appointment.service}
            </div>
            
            <div className="text-sm text-secondary truncate mb-2 ml-18">
              {appointment.preview}
            </div>
            
            <div className="flex items-center justify-between ml-6">
              <div className="flex items-center gap-2">
                <Badge variant={getStatusBadge(appointment.status)}>
                  {getStatusText(appointment.status)}
                </Badge>
                <Badge variant={appointment.type === 'voice' ? 'info' : 'neutral'}>
                  {appointment.type === 'voice' ? '🎤 Voce' : '⌨️ Manual'}
                </Badge>
              </div>
              <button 
                onClick={() => handleShowClientDetails(appointment)}
                className="text-sm text-secondary hover:text-primary bg-secondary/5 hover:bg-secondary/10 px-2 py-1 rounded-2xl transition-colors"
              >
                Detalii
              </button>
            </div>
          </div>
          )
        })}
      </div>
      
      {/* Calendar Modal */}
      {showCalendar && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50" onClick={() => setShowCalendar(false)}>
          <div className="bg-card border border-border rounded-2xl p-6 max-w-sm w-full mx-4" onClick={(e) => e.stopPropagation()}>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-medium text-primary">Selectează Data</h3>
              <button 
                onClick={() => setShowCalendar(false)}
                className="p-1 text-secondary hover:text-primary rounded-2xl hover:bg-card-hover transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            
            {/* Calendar Grid */}
            <div className="grid grid-cols-7 gap-1 mb-4">
              {['L', 'M', 'M', 'J', 'V', 'S', 'D'].map((day) => (
                <div key={day} className="text-center text-sm font-medium text-secondary p-2">
                  {day}
                </div>
              ))}
              
              {Array.from({ length: 35 }, (_, i) => {
                const dayNumber = i - 5 + 1; // Start from 1st day
                const isCurrentDay = dayNumber === 12;
                const isValidDay = dayNumber > 0 && dayNumber <= 31;
                
                return (
                  <button
                    key={i}
                    className={clsx(
                      "text-sm p-2 rounded-2xl transition-colors",
                      isCurrentDay 
                        ? "bg-primary text-background font-medium" 
                        : isValidDay 
                          ? "text-primary hover:bg-card-hover" 
                          : "text-secondary/50 cursor-not-allowed"
                    )}
                    disabled={!isValidDay}
                    onClick={() => {
                      if (isValidDay) {
                        setShowCalendar(false);
                      }
                    }}
                  >
                    {isValidDay ? dayNumber : ''}
                  </button>
                );
              })}
            </div>
            
            <div className="flex gap-2">
              <button 
                onClick={() => setShowCalendar(false)}
                className="flex-1 px-4 py-2 bg-secondary/10 text-secondary rounded-2xl hover:bg-secondary/20 transition-colors"
              >
                Anulează
              </button>
              <button 
                onClick={() => setShowCalendar(false)}
                className="flex-1 px-4 py-2 bg-primary text-background rounded-2xl hover:bg-secondary transition-colors"
              >
                Selectează
              </button>
            </div>
          </div>
        </div>
      )}
      
      {/* Client Details Modal */}
      {showClientDetails && selectedClient && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50" onClick={() => setShowClientDetails(false)}>
          <div className="bg-card border border-border rounded-2xl p-6 max-w-lg w-full mx-4 max-h-[80vh] overflow-y-auto" onClick={(e) => e.stopPropagation()}>
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-medium text-primary">Detalii Client</h3>
              <button 
                onClick={() => setShowClientDetails(false)}
                className="p-1 text-secondary hover:text-primary rounded-2xl hover:bg-card-hover transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            
            {/* Client Info */}
            <div className="space-y-6">
              {/* Basic Info */}
              <div className="flex items-center gap-4 p-4 bg-secondary/5 rounded-2xl">
                <div className="w-12 h-12 rounded-full bg-secondary/20 flex items-center justify-center">
                  <User className="w-6 h-6 text-primary" />
                </div>
                <div>
                  <h4 className="text-lg font-medium text-primary">{selectedClient.clientName}</h4>
                  <p className="text-sm text-secondary">
                    {selectedClient.lastVisit ? `Ultima vizită: ${selectedClient.lastVisit}` : 'Client nou'}
                  </p>
                </div>
              </div>
              
              {/* Contact Info */}
              <div className="grid grid-cols-1 gap-4">
                <div className="flex items-center gap-3 p-3 bg-card rounded-2xl border border-border">
                  <Phone className="w-4 h-4 text-secondary" />
                  <span className="text-primary">{selectedClient.clientPhone}</span>
                </div>
                <div className="flex items-center gap-3 p-3 bg-card rounded-2xl border border-border">
                  <Mail className="w-4 h-4 text-secondary" />
                  <span className="text-primary">{selectedClient.clientEmail}</span>
                </div>
              </div>
              
              {/* Appointment Info */}
              <div className="p-4 bg-secondary/5 rounded-2xl">
                <h5 className="text-base font-medium text-primary mb-3">Programarea Actuală</h5>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-secondary">Serviciu:</span>
                    <span className="text-primary font-medium">{selectedClient.service}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-secondary">Ora:</span>
                    <span className="text-primary">{selectedClient.time}</span>
                  </div>
                  {selectedClient.duration && (
                    <div className="flex justify-between">
                      <span className="text-secondary">Durată:</span>
                      <span className="text-primary">{selectedClient.duration}</span>
                    </div>
                  )}
                  {selectedClient.price && (
                    <div className="flex justify-between">
                      <span className="text-secondary">Preț:</span>
                      <span className="text-primary font-medium">{selectedClient.price}</span>
                    </div>
                  )}
                </div>
              </div>
              
              {/* Notes */}
              {selectedClient.clientNotes && (
                <div>
                  <h5 className="text-base font-medium text-primary mb-3">Observații</h5>
                  <p className="text-secondary bg-card border border-border rounded-2xl p-3 leading-relaxed">
                    {selectedClient.clientNotes}
                  </p>
                </div>
              )}
              
              {/* Preferences */}
              {selectedClient.preferences && selectedClient.preferences.length > 0 && (
                <div>
                  <h5 className="text-base font-medium text-primary mb-3">Preferințe</h5>
                  <div className="flex flex-wrap gap-2">
                    {selectedClient.preferences.map((preference, index) => (
                      <Badge key={index} variant="neutral">
                        {preference}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}
            </div>
            
            {/* Actions */}
            <div className="flex gap-3 mt-6 pt-4 border-t border-border">
              <button 
                onClick={() => setShowClientDetails(false)}
                className="flex-1 px-4 py-2 bg-secondary/10 text-secondary rounded-2xl hover:bg-secondary/20 transition-colors"
              >
                Închide
              </button>
              <button className="flex-1 px-4 py-2 bg-primary text-background rounded-2xl hover:bg-secondary transition-colors">
                Editează Client
              </button>
            </div>
          </div>
        </div>
      )}
      
      {/* Add Appointment Modal */}
      {showAddAppointment && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50" onClick={() => setShowAddAppointment(false)}>
          <div className="bg-card border border-border rounded-2xl p-6 max-w-md w-full mx-4 max-h-[80vh] overflow-y-auto" onClick={(e) => e.stopPropagation()}>
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-medium text-primary">Adaugă Programare</h3>
              <button 
                onClick={() => setShowAddAppointment(false)}
                className="p-1 text-secondary hover:text-primary rounded-2xl hover:bg-card-hover transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            
            {/* Form Fields */}
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-primary mb-2">Nume Client</label>
                <input
                  type="text"
                  placeholder="Nume complet client"
                  className="w-full px-3 py-2 bg-card border border-border rounded-2xl text-sm text-primary placeholder-secondary focus:outline-none focus:ring-1 focus:ring-secondary focus:border-secondary transition-colors"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-primary mb-2">Telefon</label>
                <input
                  type="tel"
                  placeholder="+40 123 456 789"
                  className="w-full px-3 py-2 bg-card border border-border rounded-2xl text-sm text-primary placeholder-secondary focus:outline-none focus:ring-1 focus:ring-secondary focus:border-secondary transition-colors"
                />
              </div>
              
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-sm font-medium text-primary mb-2">Data</label>
                  <input
                    type="date"
                    className="w-full px-3 py-2 bg-card border border-border rounded-2xl text-sm text-primary focus:outline-none focus:ring-1 focus:ring-secondary focus:border-secondary transition-colors"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-primary mb-2">Ora</label>
                  <input
                    type="time"
                    className="w-full px-3 py-2 bg-card border border-border rounded-2xl text-sm text-primary focus:outline-none focus:ring-1 focus:ring-secondary focus:border-secondary transition-colors"
                  />
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-primary mb-2">Serviciu</label>
                <select className="w-full px-3 py-2 bg-card border border-border rounded-2xl text-sm text-primary focus:outline-none focus:ring-1 focus:ring-secondary focus:border-secondary transition-colors">
                  <option value="">Selectează serviciul</option>
                  <option value="tuns">Tuns simplu</option>
                  <option value="tuns-barba">Tuns + Barbă</option>
                  <option value="tuns-vopsit">Tuns + Vopsit</option>
                  <option value="coafura">Coafură ocazie</option>
                  <option value="tratament">Tratamente păr</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-primary mb-2">Observații</label>
                <textarea
                  placeholder="Observații despre client, preferințe, alergii..."
                  rows={3}
                  className="w-full px-3 py-2 bg-card border border-border rounded-2xl text-sm text-primary placeholder-secondary focus:outline-none focus:ring-1 focus:ring-secondary focus:border-secondary transition-colors resize-none"
                ></textarea>
              </div>
            </div>
            
            {/* Actions */}
            <div className="flex gap-3 mt-6 pt-4 border-t border-border">
              <button 
                onClick={() => setShowAddAppointment(false)}
                className="flex-1 px-4 py-2 bg-secondary/10 text-secondary rounded-2xl hover:bg-secondary/20 transition-colors"
              >
                Anulează
              </button>
              <button 
                onClick={() => setShowAddAppointment(false)}
                className="flex-1 px-4 py-2 bg-primary text-background rounded-2xl hover:bg-secondary transition-colors"
              >
                Salvează Programare
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}