'use client'

import { 
  Reply, 
  Trash2, 
  Star, 
  Phone, 
  Clock, 
  MapPin,
  Edit3,
  Check,
  X,
  MessageSquare,
  Calendar
} from 'lucide-react'
import Badge from '@/components/ui/Badge'
import { cn } from '@/lib/utils'

interface AppointmentDetailsProps {
  appointmentId: string | null
}

// Mock data pentru appointment details
const appointmentDetails = {
  '1': {
    id: '1',
    clientName: 'Ion Popescu',
    clientPhone: '+40 123 456 789',
    clientEmail: 'ion.popescu@email.com',
    service: 'Tuns + Barbă',
    date: '13 Mai 2024',
    time: '10:30',
    duration: '45 minute',
    status: 'confirmed',
    type: 'voice',
    price: '85 RON',
    notes: 'Client obișnuit, preferă tunsoarea scurtă pe lateral și barbă aranjată clasic. Alergic la anumite produse - să se verifice înainte de aplicare.',
    history: [
      'Ultima programare: 15 Aprilie 2024 - Tuns simplu',
      'Frecvență: O dată la 3-4 săptămâni',
      'Preferințe: Tunsoare scurtă, barbă îngrijită'
    ],
    voiceTranscript: 'Bună ziua, aș dori să programez o întâlnire pentru tuns și barbă. Sunt Ion Popescu, client obișnuit. Când aveți loc marți dimineața?'
  },
  '2': {
    id: '2',
    clientName: 'Maria Ionescu',
    clientPhone: '+40 987 654 321',
    clientEmail: 'maria.ionescu@email.com',
    service: 'Tuns + Vopsit',
    date: '13 Mai 2024',
    time: '11:15',
    duration: '2 ore',
    status: 'in-progress',
    type: 'voice',
    price: '180 RON',
    notes: 'În desfășurare - tuns complet și vopsire cu nuanța preferată castaniu închis. Client solicită și tratament de hidratare.',
    history: [
      'Ultima programare: 8 Martie 2024 - Vopsit',
      'Frecvență: O dată la 2 luni',
      'Preferințe: Culori naturale, tratamente de îngrijire'
    ],
    voiceTranscript: 'Salut, sunt Maria. Vreau să-mi programez o ședință pentru vopsit părul. Aceeași nuanță ca data trecută, castaniu închis.'
  }
}

export default function AppointmentDetails({ appointmentId }: AppointmentDetailsProps) {
  if (!appointmentId) {
    return (
      <div className="flex-[40] flex items-center justify-center bg-card">
        <div className="text-center">
          <Calendar className="h-12 w-12 text-secondary mx-auto mb-4" />
          <h3 className="text-lg font-medium text-primary mb-2">Selectează o programare</h3>
          <p className="text-secondary">Alege o programare din lista din stânga pentru a vedea detaliile complete.</p>
        </div>
      </div>
    )
  }

  const appointment = appointmentDetails[appointmentId as keyof typeof appointmentDetails]
  
  if (!appointment) {
    return (
      <div className="flex-[40] flex items-center justify-center bg-card">
        <div className="text-center">
          <div className="text-lg font-medium text-primary">Programare nu a fost găsită</div>
        </div>
      </div>
    )
  }

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

  return (
    <div className="flex-[40] flex flex-col bg-card">
      {/* Header */}
      <div className="p-4 border-b border-border bg-card">
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-xl font-medium text-primary">{appointment.service}</h2>
          <div className="flex space-x-2">
            <button className="p-2 text-secondary hover:text-primary rounded-md hover:bg-card-hover transition-colors" title="Răspunde">
              <Reply className="h-5 w-5" />
            </button>
            <button className="p-2 text-secondary hover:text-primary rounded-md hover:bg-card-hover transition-colors" title="Șterge">
              <Trash2 className="h-5 w-5" />
            </button>
            <button className="p-2 text-secondary hover:text-primary rounded-md hover:bg-card-hover transition-colors" title="Favoriți">
              <Star className="h-5 w-5" />
            </button>
          </div>
        </div>
        
        <div className="flex items-center">
          <div className="w-10 h-10 rounded-full bg-secondary/20 flex items-center justify-center text-primary font-medium">
            {appointment.clientName.split(' ').map(n => n[0]).join('')}
          </div>
          <div className="ml-3">
            <div className="flex items-center gap-3">
              <span className="font-medium text-primary">{appointment.clientName}</span>
              <span className="text-secondary">{appointment.clientEmail}</span>
            </div>
            <div className="flex items-center text-sm text-secondary gap-4">
              <span className="flex items-center gap-1">
                <Clock className="w-4 h-4" />
                {appointment.date} la {appointment.time}
              </span>
              <span className="flex items-center gap-1">
                <Phone className="w-4 h-4" />
                {appointment.clientPhone}
              </span>
            </div>
          </div>
          <div className="ml-auto flex gap-2">
            <Badge variant={getStatusBadge(appointment.status)}>
              {getStatusText(appointment.status)}
            </Badge>
            <Badge variant={appointment.type === 'voice' ? 'info' : 'neutral'}>
              {appointment.type === 'voice' ? '🎤 Voce' : '⌨️ Manual'}
            </Badge>
          </div>
        </div>
      </div>
      
      {/* Content */}
      <div className="flex-1 p-6 overflow-y-auto">
        {/* Service Details */}
        <div className="mb-6">
          <h3 className="text-lg font-medium text-primary mb-3">Detalii Serviciu</h3>
          <div className="bg-card rounded-lg p-4 space-y-3">
            <div className="flex justify-between">
              <span className="text-secondary">Serviciu:</span>
              <span className="text-primary font-medium">{appointment.service}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-secondary">Durată:</span>
              <span className="text-primary">{appointment.duration}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-secondary">Preț:</span>
              <span className="text-primary font-medium">{appointment.price}</span>
            </div>
          </div>
        </div>

        {/* Notes */}
        <div className="mb-6">
          <h3 className="text-lg font-medium text-primary mb-3">Observații</h3>
          <div className="bg-card rounded-lg p-4">
            <p className="text-secondary leading-relaxed">{appointment.notes}</p>
          </div>
        </div>

        {/* Voice Transcript */}
        {appointment.type === 'voice' && (
          <div className="mb-6">
            <h3 className="text-lg font-medium text-primary mb-3 flex items-center gap-2">
              <MessageSquare className="w-5 h-5" />
              Transcriere Conversație Vocală
            </h3>
            <div className="bg-secondary/10 border border-border rounded-lg p-4">
              <p className="text-primary italic leading-relaxed">"{appointment.voiceTranscript}"</p>
            </div>
          </div>
        )}

        {/* Client History */}
        <div className="mb-6">
          <h3 className="text-lg font-medium text-primary mb-3">Istoric Client</h3>
          <div className="bg-card rounded-lg p-4">
            <ul className="space-y-2">
              {appointment.history.map((item, index) => (
                <li key={index} className="text-secondary flex items-start gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-secondary mt-2 flex-shrink-0"></span>
                  {item}
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
      
      {/* Actions Footer */}
      <div className="p-4 border-t border-border bg-card">
        <div className="flex items-center justify-between">
          <div className="flex space-x-2">
            {appointment.status === 'pending' && (
              <>
                <button className="inline-flex items-center gap-2 px-4 py-2 bg-primary text-background font-medium rounded-md hover:bg-secondary transition-colors">
                  <Check className="w-4 h-4" />
                  Confirmă
                </button>
                <button className="inline-flex items-center gap-2 px-4 py-2 bg-secondary text-primary font-medium rounded-md hover:bg-secondary/80 transition-colors">
                  <X className="w-4 h-4" />
                  Refuză
                </button>
              </>
            )}
            {appointment.status === 'confirmed' && (
              <button className="inline-flex items-center gap-2 px-4 py-2 bg-primary text-background font-medium rounded-md hover:bg-secondary transition-colors">
                <Clock className="w-4 h-4" />
                Începe Serviciul
              </button>
            )}
            {appointment.status === 'in-progress' && (
              <button className="inline-flex items-center gap-2 px-4 py-2 bg-primary text-background font-medium rounded-md hover:bg-secondary transition-colors">
                <Check className="w-4 h-4" />
                Finalizează
              </button>
            )}
          </div>
          
          <button className="inline-flex items-center gap-2 px-4 py-2 border border-border text-secondary hover:text-primary hover:bg-card-hover rounded-md transition-colors">
            <Edit3 className="w-4 h-4" />
            Editează
          </button>
        </div>
      </div>
    </div>
  )
}