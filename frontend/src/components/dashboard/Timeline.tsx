'use client'

import { Calendar as TimelineIcon, ChevronLeft, ChevronRight, MoreHorizontal, Plus } from 'lucide-react'
import Badge from '@/components/ui/Badge'
import { cn } from '@/lib/utils'

interface Appointment {
  id: string
  time: string
  clientName: string
  service: string
  status: 'confirmed' | 'pending' | 'in-progress' | 'cancelled'
  type: 'voice' | 'manual'
  isNext?: boolean
  isCurrent?: boolean
}

interface TimelineProps {
  appointments?: Appointment[]
}

const mockAppointments: Appointment[] = [
  {
    id: '1',
    time: '08:30',
    clientName: 'Ion P.',
    service: 'Tuns simplu',
    status: 'confirmed',
    type: 'voice'
  },
  {
    id: '2',
    time: '10:00',
    clientName: 'Maria L.',
    service: 'Tuns + Vopsit',
    status: 'pending',
    type: 'manual'
  },
  {
    id: '3',
    time: '11:30',
    clientName: 'Mihai V.',
    service: 'Tuns + Barbă',
    status: 'confirmed',
    type: 'voice',
    isNext: true
  },
  {
    id: '4',
    time: '13:30',
    clientName: 'Andrei C.',
    service: 'Tuns',
    status: 'confirmed',
    type: 'manual'
  },
  {
    id: '5',
    time: '14:30',
    clientName: 'Clientul Actual',
    service: 'Tuns + Spălat',
    status: 'in-progress',
    type: 'voice',
    isCurrent: true
  },
  {
    id: '6',
    time: '15:30',
    clientName: 'Anulat',
    service: 'Tuns + Barbă',
    status: 'cancelled',
    type: 'manual'
  }
]

const timeSlots = ['08:00', '09:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00', '18:00']

const StatusDot = ({ status, className }: { status: string, className?: string }) => {
  const colors = {
    confirmed: 'bg-accent',
    pending: 'bg-yellow-400', 
    'in-progress': 'bg-accent',
    cancelled: 'bg-red-400',
    break: 'bg-blue-400',
    free: 'bg-gray-500'
  }
  
  return (
    <div className={cn(
      'absolute -left-[18px] top-3 w-2 h-2 rounded-full ring-2 ring-background',
      colors[status as keyof typeof colors],
      className
    )} />
  )
}

const AppointmentCard = ({ appointment }: { appointment: Appointment }) => {
  const getBadgeVariant = (status: string) => {
    switch (status) {
      case 'confirmed': return 'success'
      case 'pending': return 'warning'
      case 'in-progress': return 'success'
      case 'cancelled': return 'error'
      default: return 'neutral'
    }
  }

  const getBadgeText = (status: string) => {
    switch (status) {
      case 'confirmed': return 'Confirmat'
      case 'pending': return 'În așteptare'
      case 'in-progress': return 'În desfășurare'
      case 'cancelled': return 'Anulat'
      default: return status
    }
  }

  const cardClasses = cn(
    'flex items-center justify-between rounded-md border border-border p-3 transition',
    appointment.isNext || appointment.isCurrent 
      ? 'border-accent/40 bg-accent/5 ring-2 ring-accent/20' 
      : 'bg-background hover:border-border-hover'
  )

  return (
    <div className="relative">
      <StatusDot status={appointment.status} />
      <div className={cardClasses}>
        <div className="flex items-center gap-3">
          <span className={cn(
            'text-xs w-14 md:w-16',
            appointment.isNext || appointment.isCurrent ? 'text-accent' : 'text-secondary'
          )}>
            {appointment.time}
          </span>
          <div className="flex flex-col">
            <div className={cn(
              'text-sm font-medium',
              appointment.isCurrent ? 'text-primary' : appointment.isNext ? 'text-primary' : 'text-primary'
            )}>
              {appointment.clientName}
            </div>
            <div className={cn(
              'text-xs',
              appointment.isNext || appointment.isCurrent ? 'text-secondary' : 'text-secondary'
            )}>
              {appointment.service}
            </div>
            <div className="mt-1 flex items-center gap-2">
              <Badge variant={getBadgeVariant(appointment.status)}>
                {getBadgeText(appointment.status)}
              </Badge>
              <Badge variant={appointment.type === 'voice' ? 'info' : 'neutral'}>
                {appointment.type === 'voice' ? '🎤 Voce' : '⌨️ Manual'}
              </Badge>
              {appointment.isNext && (
                <Badge variant="info">Următorul</Badge>
              )}
            </div>
          </div>
        </div>
        <button className="p-2 rounded-md border border-border hover:border-border-hover hover:bg-card-hover text-secondary hover:text-primary transition-colors">
          <MoreHorizontal className="w-4.5 h-4.5" />
        </button>
      </div>
    </div>
  )
}

const BreakSlot = ({ time, description }: { time: string, description: string }) => (
  <div className="relative">
    <StatusDot status="break" />
    <div className="flex items-center justify-between rounded-md border border-dashed border-border bg-background/20 p-3">
      <div className="flex items-center gap-3">
        <span className="text-xs text-secondary w-14 md:w-16">{time}</span>
        <div className="text-xs text-secondary">{description}</div>
      </div>
    </div>
  </div>
)

const FreeSlot = ({ time }: { time: string }) => (
  <div className="relative">
    <StatusDot status="free" />
    <div className="flex items-center justify-between rounded-md border border-dashed border-border bg-background/20 p-3">
      <div className="flex items-center gap-3">
        <span className="text-xs text-secondary w-14 md:w-16">{time}</span>
        <div className="text-xs text-secondary">Slot liber</div>
      </div>
      <button className="inline-flex items-center gap-1.5 px-2.5 h-8 rounded-md border border-accent/40 text-accent hover:bg-accent/10 transition-colors">
        <Plus className="w-4 h-4" />
        Adaugă
      </button>
    </div>
  </div>
)

export default function Timeline({ appointments = mockAppointments }: TimelineProps) {
  return (
    <div className="xl:col-span-8">
      <div className="rounded-lg bg-card border border-border overflow-hidden">
        <div className="flex items-center justify-between p-4 border-b border-border">
          <div className="flex items-center gap-2">
            <TimelineIcon className="w-4.5 h-4.5 text-accent" />
            <h2 className="text-base md:text-lg font-semibold tracking-tight text-primary">Agenda Zilei</h2>
          </div>
          <div className="flex items-center gap-2 text-xs">
            <button className="button-ghost">Astăzi</button>
            <button className="px-2.5 h-8 rounded-md border border-border hover:border-border-hover hover:bg-card-hover transition">
              <ChevronLeft className="w-4 h-4" />
            </button>
            <button className="px-2.5 h-8 rounded-md border border-border hover:border-border-hover hover:bg-card-hover transition">
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>

        <div className="p-4">
          <div className="grid grid-cols-12 gap-3 md:gap-4">
            {/* Hours rail */}
            <div className="hidden md:block md:col-span-2">
              <div className="space-y-6 text-xs text-secondary">
                {timeSlots.map(time => (
                  <div key={time}>{time}</div>
                ))}
              </div>
            </div>
            
            {/* Appointments */}
            <div className="col-span-12 md:col-span-10">
              <div className="relative">
                {/* Vertical guide */}
                <div className="absolute left-0 top-0 bottom-0 w-px bg-border"></div>
                <div className="space-y-3 pl-0 md:pl-4">
                  {appointments.map(appointment => (
                    <AppointmentCard key={appointment.id} appointment={appointment} />
                  ))}
                  
                  {/* Breaks */}
                  <BreakSlot time="11:00" description="Pauză scurtă (15 min)" />
                  <BreakSlot time="12:30" description="Pauză prânz (30 min)" />
                  
                  {/* Free slot */}
                  <FreeSlot time="16:30" />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}