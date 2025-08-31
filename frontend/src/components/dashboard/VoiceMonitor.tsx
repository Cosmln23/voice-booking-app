'use client'

import { Activity, FileText, CheckCircle, AlertCircle, XOctagon } from 'lucide-react'

interface VoiceActivity {
  id: string
  timestamp: string
  type: 'success' | 'warning' | 'error'
  intent?: string
  result: string
  client?: string
}

interface VoiceMonitorProps {
  activities?: VoiceActivity[]
}

const mockActivities: VoiceActivity[] = [
  {
    id: '1',
    timestamp: '14:30',
    type: 'success',
    intent: 'Tuns simplu',
    result: 'Programare reușită (Mihai V.)',
    client: 'Mihai V.'
  },
  {
    id: '2',
    timestamp: '14:25',
    type: 'warning',
    intent: 'Vopsit',
    result: 'Serviciu neconfigurat'
  },
  {
    id: '3',
    timestamp: '14:20',
    type: 'error',
    intent: undefined,
    result: 'Sincronizare Google Calendar eșuată'
  }
]

const ActivityItem = ({ activity }: { activity: VoiceActivity }) => {
  const getStatusColor = (type: string) => {
    switch (type) {
      case 'success': return 'bg-accent'
      case 'warning': return 'bg-yellow-400'  
      case 'error': return 'bg-red-400'
      default: return 'bg-gray-400'
    }
  }

  const getStatusIcon = (type: string) => {
    switch (type) {
      case 'success': return <CheckCircle className="w-3.5 h-3.5" />
      case 'warning': return <AlertCircle className="w-3.5 h-3.5" />
      case 'error': return <XOctagon className="w-3.5 h-3.5" />
      default: return null
    }
  }

  const getStatusText = (type: string) => {
    switch (type) {
      case 'success': return 'text-accent'
      case 'warning': return 'text-yellow-300'
      case 'error': return 'text-red-300'
      default: return 'text-secondary'
    }
  }

  return (
    <div className="p-4 flex items-start gap-3 border-b border-border last:border-b-0">
      <span className={`mt-1.5 w-2 h-2 rounded-full ${getStatusColor(activity.type)}`} />
      <div className="flex-1">
        <div className="flex items-center justify-between">
          <div className="text-sm">
            <span className="text-secondary">[{activity.timestamp}]</span>
            {activity.intent ? (
              <>
                <span className="ml-2 text-primary">Intenție:</span>
                <span className="text-secondary"> "{activity.intent}"</span>
              </>
            ) : (
              <>
                <span className="ml-2 text-primary">Eroare Sistem:</span>
                <span className="text-secondary"> {activity.result}</span>
              </>
            )}
          </div>
          {activity.intent && (
            <span className={`text-xs inline-flex items-center gap-1 ${getStatusText(activity.type)}`}>
              {getStatusIcon(activity.type)}
              {activity.result}
            </span>
          )}
        </div>
        {activity.type === 'warning' && (
          <div className="text-xs text-secondary mt-1">Rezultat: Conversație abandonată</div>
        )}
        <div className="mt-2">
          <button className="inline-flex items-center gap-1.5 text-xs text-accent hover:text-accent-hover transition-colors">
            <FileText className="w-3.5 h-3.5" />
            {activity.type === 'error' ? 'Vezi log-ul' : 'Vezi transcrierea'}
          </button>
        </div>
      </div>
    </div>
  )
}

export default function VoiceMonitor({ activities = mockActivities }: VoiceMonitorProps) {
  return (
    <div className="rounded-lg bg-card border border-border overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b border-border">
        <div className="flex items-center gap-2">
          <Activity className="w-4.5 h-4.5 text-accent" />
          <h3 className="text-base font-semibold tracking-tight text-primary">Agent Vocal — Activitate</h3>
        </div>
        <button className="button-ghost">Live</button>
      </div>
      <div className="divide-y divide-border">
        {activities.map(activity => (
          <ActivityItem key={activity.id} activity={activity} />
        ))}
      </div>
    </div>
  )
}