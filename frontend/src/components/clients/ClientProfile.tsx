'use client'

import { useState } from 'react'
import {
  X,
  Phone,
  Mail,
  Calendar,
  MapPin,
  User,
  Heart,
  AlertTriangle,
  Clock,
  DollarSign,
  FileText,
  Shield,
  Star,
  Edit,
  Trash2,
  MessageSquare,
  PhoneCall
} from 'lucide-react'
import { cn } from '../../lib/utils'

interface Client {
  id: string
  name: string
  phone: string
  email: string
  lastVisit: string
  totalVisits: number
  status: 'VIP' | 'Standard' | 'New' | 'Inactive' | 'At Risk'
  ltv: string
  notes?: string
  preferences?: string
  noShows?: number
  gdprConsent: boolean
  nextAppointment?: string
}

interface Visit {
  id: string
  date: string
  service: string
  duration: string
  cost: string
  stylist: string
  notes?: string
  status: 'completed' | 'cancelled' | 'no-show'
}

interface ClientProfileProps {
  client: Client
  onClose: () => void
}

const mockVisits: Visit[] = [
  {
    id: '1',
    date: '2025-01-28',
    service: 'Tunsoare + Balayage',
    duration: '2h 30min',
    cost: '280 RON',
    stylist: 'Ana Popescu',
    notes: 'Client foarte mulțumit, dorește să repete peste 6 săptămâni',
    status: 'completed'
  },
  {
    id: '2',
    date: '2024-12-15',
    service: 'Coafură Eveniment',
    duration: '1h 45min',
    cost: '180 RON',
    stylist: 'Maria Ionescu',
    notes: 'Pentru nunta prietenei, foarte elegant',
    status: 'completed'
  },
  {
    id: '3',
    date: '2024-11-20',
    service: 'Tunsoare Simpla',
    duration: '45min',
    cost: '80 RON',
    stylist: 'Ana Popescu',
    status: 'completed'
  },
  {
    id: '4',
    date: '2024-10-28',
    service: 'Tratament Păr + Coafură',
    duration: '2h',
    cost: '220 RON',
    stylist: 'Ana Popescu',
    notes: 'Prima întâlnire, foarte entuziastă',
    status: 'completed'
  },
  {
    id: '5',
    date: '2024-09-15',
    service: 'Consultație',
    duration: '30min',
    cost: '0 RON',
    stylist: 'Ana Popescu',
    notes: 'A venit să se consulte pentru schimbarea stilului',
    status: 'no-show'
  }
]

export default function ClientProfile({ client, onClose }: ClientProfileProps) {
  const [activeTab, setActiveTab] = useState<'overview' | 'history' | 'notes'>('overview')

  const getStatusBadge = (status: Client['status']) => {
    const styles = {
      VIP: 'bg-secondary/20 text-secondary border-border',
      Standard: 'bg-green-500/20 text-green-400 border-green-500/30',
      New: 'bg-secondary/20 text-primary border-border',
      Inactive: 'bg-gray-500/20 text-gray-400 border-gray-500/30',
      'At Risk': 'bg-secondary/20 text-secondary border-border'
    }
    
    return (
      <span className={cn(
        'inline-flex items-center px-3 py-1 rounded-2xl text-sm font-medium border',
        styles[status]
      )}>
        {status === 'VIP' && <Star className="w-4 h-4 mr-2" />}
        {status === 'At Risk' && <AlertTriangle className="w-4 h-4 mr-2" />}
        {status}
      </span>
    )
  }

  const getVisitStatusBadge = (status: Visit['status']) => {
    const styles = {
      completed: 'bg-green-500/20 text-green-400',
      cancelled: 'bg-gray-500/20 text-gray-400',
      'no-show': 'bg-secondary/20 text-secondary'
    }
    
    const labels = {
      completed: 'Finalizat',
      cancelled: 'Anulat',
      'no-show': 'Absent'
    }
    
    return (
      <span className={cn(
        'inline-flex items-center px-2 py-1 rounded-2xl text-xs font-medium',
        styles[status]
      )}>
        {labels[status]}
      </span>
    )
  }

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr)
    return date.toLocaleDateString('ro-RO', { 
      day: '2-digit', 
      month: 'short', 
      year: 'numeric',
      weekday: 'short'
    })
  }

  const completedVisits = mockVisits.filter(v => v.status === 'completed')
  const totalRevenue = completedVisits.reduce((sum, visit) => {
    return sum + parseInt(visit.cost.replace(/[^\d]/g, ''))
  }, 0)

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-card rounded-2xl border border-border w-full max-w-4xl max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="p-6 border-b border-border">
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-4">
              <div className="w-16 h-16 rounded-full bg-accent/20 flex items-center justify-center text-accent font-bold text-xl">
                {client.name.split(' ').map(n => n[0]).join('').toUpperCase()}
              </div>
              <div>
                <h2 className="text-2xl font-bold text-primary mb-2">{client.name}</h2>
                <div className="flex items-center gap-3">
                  {getStatusBadge(client.status)}
                  <span className="text-sm text-secondary">Client din {new Date(mockVisits[mockVisits.length - 1]?.date || client.lastVisit).toLocaleDateString('ro-RO', { month: 'long', year: 'numeric' })}</span>
                </div>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <button className="p-2 text-secondary hover:text-primary rounded-2xl hover:bg-card-hover transition-colors">
                <MessageSquare className="w-5 h-5" />
              </button>
              <button className="p-2 text-secondary hover:text-primary rounded-2xl hover:bg-card-hover transition-colors">
                <PhoneCall className="w-5 h-5" />
              </button>
              <button className="p-2 text-secondary hover:text-primary rounded-2xl hover:bg-card-hover transition-colors">
                <Edit className="w-5 h-5" />
              </button>
              <button 
                onClick={onClose}
                className="p-2 text-secondary hover:text-primary rounded-2xl hover:bg-card-hover transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="px-6 border-b border-border">
          <div className="flex gap-8">
            {[
              { key: 'overview', label: 'Prezentare Generală', icon: User },
              { key: 'history', label: 'Istoric Vizite', icon: Calendar },
              { key: 'notes', label: 'Note & Preferințe', icon: FileText }
            ].map((tab) => (
              <button
                key={tab.key}
                onClick={() => setActiveTab(tab.key as any)}
                className={cn(
                  'flex items-center gap-2 py-3 border-b-2 transition-colors',
                  activeTab === tab.key
                    ? 'border-accent text-accent'
                    : 'border-transparent text-secondary hover:text-primary'
                )}
              >
                <tab.icon className="w-4 h-4" />
                {tab.label}
              </button>
            ))}
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {activeTab === 'overview' && (
            <div className="space-y-6">
              {/* Contact Info */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="bg-background rounded-2xl p-4 border border-border">
                  <h3 className="font-semibold text-primary mb-4 flex items-center gap-2">
                    <User className="w-4 h-4" />
                    Informații Contact
                  </h3>
                  <div className="space-y-3">
                    <div className="flex items-center gap-3">
                      <Phone className="w-4 h-4 text-secondary" />
                      <span className="text-primary">{client.phone}</span>
                    </div>
                    <div className="flex items-center gap-3">
                      <Mail className="w-4 h-4 text-secondary" />
                      <span className="text-primary">{client.email}</span>
                    </div>
                    <div className="flex items-center gap-3">
                      <Shield className="w-4 h-4 text-secondary" />
                      <span className={cn('text-sm', client.gdprConsent ? 'text-primary' : 'text-secondary')}>
                        GDPR: {client.gdprConsent ? 'Consimțământ activ' : 'Lipsă consimțământ'}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="bg-background rounded-2xl p-4 border border-border">
                  <h3 className="font-semibold text-primary mb-4 flex items-center gap-2">
                    <DollarSign className="w-4 h-4" />
                    Statistici Financiare
                  </h3>
                  <div className="space-y-3">
                    <div className="flex justify-between items-center">
                      <span className="text-secondary">Valoare totală (LTV):</span>
                      <span className="font-semibold text-primary">{client.ltv}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-secondary">Valoare medie/vizită:</span>
                      <span className="font-semibold text-primary">{Math.round(totalRevenue / completedVisits.length)} RON</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-secondary">Total vizite:</span>
                      <span className="font-semibold text-primary">{client.totalVisits}</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Visit Stats */}
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
                <div className="bg-background rounded-2xl p-4 border border-border text-center">
                  <Calendar className="w-8 h-8 text-accent mx-auto mb-2" />
                  <div className="text-2xl font-bold text-primary">{completedVisits.length}</div>
                  <div className="text-sm text-secondary">Vizite Finalizate</div>
                </div>
                
                <div className="bg-background rounded-2xl p-4 border border-border text-center">
                  <Clock className="w-8 h-8 text-primary mx-auto mb-2" />
                  <div className="text-2xl font-bold text-primary">{formatDate(client.lastVisit)}</div>
                  <div className="text-sm text-secondary">Ultima Vizită</div>
                </div>

                <div className="bg-background rounded-2xl p-4 border border-border text-center">
                  <AlertTriangle className={cn("w-8 h-8 mx-auto mb-2", client.noShows && client.noShows > 0 ? 'text-secondary' : 'text-primary')} />
                  <div className="text-2xl font-bold text-primary">{client.noShows || 0}</div>
                  <div className="text-sm text-secondary">Absențe (No-Show)</div>
                </div>
              </div>

              {/* Next Appointment */}
              {client.nextAppointment && (
                <div className="bg-accent/10 rounded-2xl p-4 border border-accent/30">
                  <h3 className="font-semibold text-primary mb-2 flex items-center gap-2">
                    <Calendar className="w-4 h-4 text-accent" />
                    Următoarea Programare
                  </h3>
                  <div className="text-accent font-semibold">
                    {formatDate(client.nextAppointment)} la ora 14:00
                  </div>
                  <div className="text-sm text-secondary mt-1">
                    Serviciu: Tunsoare + Coafură • Stilist: Ana Popescu
                  </div>
                </div>
              )}
            </div>
          )}

          {activeTab === 'history' && (
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <h3 className="font-semibold text-primary">Istoric Complet Vizite</h3>
                <div className="text-sm text-secondary">
                  {mockVisits.length} vizite • {totalRevenue} RON total
                </div>
              </div>
              
              <div className="space-y-4">
                {mockVisits.map((visit, index) => (
                  <div key={visit.id} className="bg-background rounded-2xl p-4 border border-border">
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-full bg-accent/20 flex items-center justify-center text-accent font-semibold text-sm">
                          {mockVisits.length - index}
                        </div>
                        <div>
                          <div className="font-semibold text-primary">{visit.service}</div>
                          <div className="text-sm text-secondary">
                            {formatDate(visit.date)} • {visit.duration} • {visit.stylist}
                          </div>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="font-semibold text-primary mb-1">{visit.cost}</div>
                        {getVisitStatusBadge(visit.status)}
                      </div>
                    </div>
                    
                    {visit.notes && (
                      <div className="mt-3 p-3 bg-card rounded-2xl">
                        <div className="text-sm text-secondary mb-1">Note:</div>
                        <div className="text-sm text-primary">{visit.notes}</div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'notes' && (
            <div className="space-y-6">
              <div className="bg-background rounded-2xl p-4 border border-border">
                <h3 className="font-semibold text-primary mb-4 flex items-center gap-2">
                  <Heart className="w-4 h-4" />
                  Preferințe Client
                </h3>
                <div className="p-3 bg-card rounded-2xl">
                  <div className="text-primary">{client.preferences || 'Nu există preferințe notate.'}</div>
                </div>
              </div>

              <div className="bg-background rounded-2xl p-4 border border-border">
                <h3 className="font-semibold text-primary mb-4 flex items-center gap-2">
                  <FileText className="w-4 h-4" />
                  Note Generale
                </h3>
                <div className="p-3 bg-card rounded-2xl">
                  <div className="text-primary">{client.notes || 'Nu există note adăugate.'}</div>
                </div>
              </div>

              <div className="bg-background rounded-2xl p-4 border border-border">
                <h3 className="font-semibold text-primary mb-4">Acțiuni Administrative</h3>
                <div className="space-y-2">
                  <button className="w-full text-left p-3 text-secondary hover:text-primary hover:bg-card-hover rounded-2xl transition-colors">
                    📝 Editează informațiile clientului
                  </button>
                  <button className="w-full text-left p-3 text-secondary hover:text-primary hover:bg-card-hover rounded-2xl transition-colors">
                    📊 Exportă datele clientului (GDPR)
                  </button>
                  <button className="w-full text-left p-3 text-secondary hover:text-primary hover:bg-card-hover rounded-2xl transition-colors">
                    🔒 Actualizează consimțământul GDPR
                  </button>
                  <button className="w-full text-left p-3 text-secondary hover:bg-secondary/10 rounded-2xl transition-colors">
                    🗑️ Șterge clientul (GDPR)
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}