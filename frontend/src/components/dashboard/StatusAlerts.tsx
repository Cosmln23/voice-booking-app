'use client'

import { ShieldAlert, Check, X } from 'lucide-react'

interface ServiceStatus {
  name: string
  status: 'online' | 'offline' | 'warning'
  lastUpdate?: string
}

interface StatusAlertsProps {
  services?: ServiceStatus[]
}

const mockServices: ServiceStatus[] = [
  { name: 'OpenAI API', status: 'online' },
  { name: 'Google Calendar', status: 'offline' },
  { name: 'Ultima anulare', status: 'warning', lastUpdate: 'acum 12 min' }
]

const StatusItem = ({ service }: { service: ServiceStatus }) => {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'online': return 'bg-accent'
      case 'offline': return 'bg-red-400'
      case 'warning': return 'bg-yellow-400'
      default: return 'bg-gray-400'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'online': return <Check className="w-3.5 h-3.5" />
      case 'offline': return <X className="w-3.5 h-3.5" />
      default: return null
    }
  }

  const getStatusText = (status: string) => {
    switch (status) {
      case 'online': return { text: 'Online', color: 'text-accent' }
      case 'offline': return { text: 'Offline', color: 'text-red-300' }
      case 'warning': return { text: service.lastUpdate || 'Warning', color: 'text-yellow-300' }
      default: return { text: 'Unknown', color: 'text-secondary' }
    }
  }

  const statusInfo = getStatusText(service.status)

  return (
    <div className="flex items-center justify-between rounded-md border border-border bg-background/40 p-3">
      <div className="flex items-center gap-2">
        <span className={`w-2.5 h-2.5 rounded-full ${getStatusColor(service.status)}`} />
        <div className="text-sm text-primary">{service.name}</div>
      </div>
      <div className={`text-xs inline-flex items-center gap-1 ${statusInfo.color}`}>
        {getStatusIcon(service.status)}
        {statusInfo.text}
      </div>
    </div>
  )
}

export default function StatusAlerts({ services = mockServices }: StatusAlertsProps) {
  return (
    <div className="rounded-lg bg-card border border-border overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b border-border">
        <div className="flex items-center gap-2">
          <ShieldAlert className="w-4.5 h-4.5 text-accent" />
          <h3 className="text-base font-semibold tracking-tight text-primary">Alerte & Sincronizare</h3>
        </div>
      </div>
      <div className="p-4 space-y-3">
        {services.map((service, index) => (
          <StatusItem key={index} service={service} />
        ))}
      </div>
    </div>
  )
}