'use client'

import clsx from "clsx"

import { useState } from 'react'
import {
  Mic,
  Settings,
  Phone,
  Calendar,
  Brain,
  Activity,
  Clock,
  DollarSign,
  Eye,
  Play,
  FileText,
  ToggleLeft,
  ToggleRight,
  CheckCircle,
  XCircle,
  AlertCircle,
  Download,
  Edit,
  Volume2,
  MessageSquare,
  Filter,
  Search,
  Menu
} from 'lucide-react'
import HorizontalScroller from '../ui/HorizontalScroller'


interface CallLog {
  id: string
  date: string
  time: string
  phoneNumber: string
  detectedIntent: string
  result: 'completed' | 'transferred' | 'abandoned'
  duration: string
  hasTranscript: boolean
  hasRecording: boolean
}

interface AgentControlCenterProps {
  isMobile?: boolean
  onMobileToggle?: () => void
}

export default function AgentControlCenter({ isMobile, onMobileToggle }: AgentControlCenterProps) {
  const [activeTab, setActiveTab] = useState<'overview' | 'config' | 'dictionary' | 'logs'>('overview')
  const [voiceGender, setVoiceGender] = useState<'male' | 'female'>('female')
  const [voiceTone, setVoiceTone] = useState<'professional' | 'friendly' | 'casual'>('friendly')
  const [redirectMode, setRedirectMode] = useState<'after_hours' | 'always' | 'when_busy'>('after_hours')
  const [greetingMessage, setGreetingMessage] = useState('Bună ziua! Vă sun de la salonul Voice Booking. Cu ce vă pot ajuta astăzi?')
  const [transferNumber, setTransferNumber] = useState('+40 721 123 456')
  
  // Integration status mock
  const integrationStatus = {
    openai: { status: 'online', lastSync: '2025-01-31 10:30' },
    googleCalendar: { status: 'online', lastSync: '2025-01-31 10:28' },
    telephony: { status: 'online', lastSync: '2025-01-31 10:32' }
  }

  // Performance metrics mock
  const performanceMetrics = {
    totalCalls: 247,
    successRate: 78,
    timeSaved: 15.5, // hours
    tokenCosts: 45.30, // RON
    avgCallDuration: '3:45',
    completedBookings: 192
  }

  // Dictionary/synonyms mock
  const [dictionary, setDictionary] = useState([
    { clientTerm: 'fade', officialService: 'Tuns Clasic', frequency: 23 },
    { clientTerm: 'barbă', officialService: 'Aranjare Barbă', frequency: 45 },
    { clientTerm: 'tuns scurt', officialService: 'Tunsoare Clasică', frequency: 67 },
    { clientTerm: 'spălat + tuns', officialService: 'Tunsoare + Styling', frequency: 34 },
    { clientTerm: 'îngrijire barbă', officialService: 'Barbă Completă', frequency: 28 }
  ])

  // Call logs mock
  const callLogs: CallLog[] = [
    {
      id: '1',
      date: '2025-01-31',
      time: '10:25',
      phoneNumber: '+40 721 ***456',
      detectedIntent: 'Programare tuns pentru mâine',
      result: 'completed',
      duration: '4:23',
      hasTranscript: true,
      hasRecording: true
    },
    {
      id: '2', 
      date: '2025-01-31',
      time: '09:45',
      phoneNumber: '+40 722 ***789',
      detectedIntent: 'Întrebare despre prețuri',
      result: 'completed',
      duration: '2:15',
      hasTranscript: true,
      hasRecording: true
    },
    {
      id: '3',
      date: '2025-01-30',
      time: '18:30',
      phoneNumber: '+40 723 ***234',
      detectedIntent: 'Programare urgentă',
      result: 'transferred',
      duration: '1:45',
      hasTranscript: true,
      hasRecording: false
    },
    {
      id: '4',
      date: '2025-01-30',
      time: '16:20',
      phoneNumber: '+40 724 ***567',
      detectedIntent: 'Anulare programare',
      result: 'completed',
      duration: '3:10',
      hasTranscript: true,
      hasRecording: true
    },
    {
      id: '5',
      date: '2025-01-30',
      time: '14:15',
      phoneNumber: '+40 725 ***890',
      detectedIntent: 'Programare pentru weeked',
      result: 'abandoned',
      duration: '0:45',
      hasTranscript: false,
      hasRecording: false
    }
  ]

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'online': return <CheckCircle className="w-4 h-4 text-primary" />
      case 'offline': return <XCircle className="w-4 h-4 text-secondary" />
      default: return <AlertCircle className="w-4 h-4 text-secondary" />
    }
  }

  const getResultBadge = (result: CallLog['result']) => {
    const styles = {
      completed: 'bg-secondary/20 text-primary border-border',
      transferred: 'bg-secondary/20 text-secondary border-border',
      abandoned: 'bg-secondary/20 text-secondary border-border'
    }
    
    const labels = {
      completed: 'Finalizat',
      transferred: 'Transferat', 
      abandoned: 'Abandonat'
    }
    
    return (
      <span className={clsx(
        'inline-flex items-center px-2 py-1 rounded-2xl text-xs font-medium border',
        styles[result]
      )}>
        {labels[result]}
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
            <Mic className="w-8 h-8 text-secondary" />
            <div>
              <h1 className="text-3xl font-bold text-primary">Agent Vocal</h1>
              <p className="text-base text-secondary">
                Centru control AI
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <div className="flex items-center gap-2 px-3 py-1 bg-background rounded-2xl border border-border">
              <Activity className="w-4 h-4 text-secondary animate-pulse" />
              <span className="text-sm text-primary">Activ</span>
            </div>
            <button className="flex items-center px-4 py-2 bg-background text-secondary border border-border rounded-2xl hover:text-primary hover:border-secondary transition-colors">
              <Download className="w-4 h-4 mr-2" />
              Export Raport
            </button>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex gap-8">
          {[
            { key: 'overview', label: 'Prezentare Generală', icon: Activity },
            { key: 'config', label: 'Configurare', icon: Settings },
            { key: 'dictionary', label: 'Dicționar AI', icon: Brain },
            { key: 'logs', label: 'Jurnal Apeluri', icon: FileText }
          ].map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key as any)}
              className={clsx(
                'flex items-center gap-2 py-3 border-b-2 transition-colors',
                activeTab === tab.key
                  ? 'border-secondary text-primary'
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
            {/* Integration Status */}
            <div className="bg-background rounded-2xl p-4 border border-border">
              <h3 className="font-semibold text-primary mb-4 flex items-center gap-2">
                <Settings className="w-5 h-5" />
                Status Integrări
              </h3>
              <div className="hidden lg:grid lg:grid-cols-3 lg:gap-4">
                <div className="flex items-center justify-between p-3 bg-card rounded-2xl">
                  <div className="flex items-center gap-3">
                    <Brain className="w-5 h-5 text-secondary" />
                    <div>
                      <div className="font-medium text-primary">OpenAI</div>
                      <div className="text-xs text-secondary">Ultimul sync: {integrationStatus.openai.lastSync}</div>
                    </div>
                  </div>
                  {getStatusIcon(integrationStatus.openai.status)}
                </div>

                <div className="flex items-center justify-between p-3 bg-card rounded-2xl">
                  <div className="flex items-center gap-3">
                    <Calendar className="w-5 h-5 text-secondary" />
                    <div>
                      <div className="font-medium text-primary">Google Calendar</div>
                      <div className="text-xs text-secondary">Ultimul sync: {integrationStatus.googleCalendar.lastSync}</div>
                    </div>
                  </div>
                  {getStatusIcon(integrationStatus.googleCalendar.status)}
                </div>

                <div className="flex items-center justify-between p-3 bg-card rounded-2xl">
                  <div className="flex items-center gap-3">
                    <Phone className="w-5 h-5 text-secondary" />
                    <div>
                      <div className="font-medium text-primary">Telefonie</div>
                      <div className="text-xs text-secondary">Ultimul sync: {integrationStatus.telephony.lastSync}</div>
                    </div>
                  </div>
                  {getStatusIcon(integrationStatus.telephony.status)}
                </div>
              </div>
              
              <HorizontalScroller>
                <div className="flex items-center justify-between p-3 bg-card rounded-2xl min-w-[240px] snap-start shrink-0">
                  <div className="flex items-center gap-3">
                    <Brain className="w-5 h-5 text-secondary" />
                    <div>
                      <div className="font-medium text-primary">OpenAI</div>
                      <div className="text-xs text-secondary">Ultimul sync: {integrationStatus.openai.lastSync}</div>
                    </div>
                  </div>
                  {getStatusIcon(integrationStatus.openai.status)}
                </div>

                <div className="flex items-center justify-between p-3 bg-card rounded-2xl min-w-[240px] snap-start shrink-0">
                  <div className="flex items-center gap-3">
                    <Calendar className="w-5 h-5 text-secondary" />
                    <div>
                      <div className="font-medium text-primary">Google Calendar</div>
                      <div className="text-xs text-secondary">Ultimul sync: {integrationStatus.googleCalendar.lastSync}</div>
                    </div>
                  </div>
                  {getStatusIcon(integrationStatus.googleCalendar.status)}
                </div>

                <div className="flex items-center justify-between p-3 bg-card rounded-2xl min-w-[240px] snap-start shrink-0">
                  <div className="flex items-center gap-3">
                    <Phone className="w-5 h-5 text-secondary" />
                    <div>
                      <div className="font-medium text-primary">Telefonie</div>
                      <div className="text-xs text-secondary">Ultimul sync: {integrationStatus.telephony.lastSync}</div>
                    </div>
                  </div>
                  {getStatusIcon(integrationStatus.telephony.status)}
                </div>
              </HorizontalScroller>
            </div>

            {/* Performance Metrics */}
            <div className="hidden lg:grid lg:grid-cols-3 lg:gap-4">
              <div className="bg-background rounded-2xl p-4 border border-border">
                <div className="flex items-center gap-3 mb-2">
                  <Phone className="w-5 h-5 text-secondary" />
                  <span className="text-sm text-secondary">Total Apeluri</span>
                </div>
                <div className="text-2xl font-bold text-primary">{performanceMetrics.totalCalls}</div>
                <div className="text-xs text-secondary">Această lună</div>
              </div>

              <div className="bg-background rounded-2xl p-4 border border-border">
                <div className="flex items-center gap-3 mb-2">
                  <CheckCircle className="w-5 h-5 text-secondary" />
                  <span className="text-sm text-secondary">Rata de Succes</span>
                </div>
                <div className="text-2xl font-bold text-primary">{performanceMetrics.successRate}%</div>
                <div className="text-xs text-secondary">{performanceMetrics.completedBookings} programări finalizate</div>
              </div>

              <div className="bg-background rounded-2xl p-4 border border-border">
                <div className="flex items-center gap-3 mb-2">
                  <Clock className="w-5 h-5 text-secondary" />
                  <span className="text-sm text-secondary">Timp Economisit</span>
                </div>
                <div className="text-2xl font-bold text-primary">{performanceMetrics.timeSaved}h</div>
                <div className="text-xs text-secondary">Durată medie: {performanceMetrics.avgCallDuration}</div>
              </div>
            </div>

            <HorizontalScroller>
              <div className="bg-background rounded-2xl p-3 border border-border min-w-[240px] snap-start shrink-0">
                <div className="flex items-center gap-3 mb-2">
                  <Phone className="w-5 h-5 text-secondary" />
                  <span className="text-xs text-secondary">Total Apeluri</span>
                </div>
                <div className="text-lg font-bold text-primary">{performanceMetrics.totalCalls}</div>
                <div className="text-xs text-secondary">Această lună</div>
              </div>

              <div className="bg-background rounded-2xl p-3 border border-border min-w-[240px] snap-start shrink-0">
                <div className="flex items-center gap-3 mb-2">
                  <CheckCircle className="w-5 h-5 text-secondary" />
                  <span className="text-xs text-secondary">Rata de Succes</span>
                </div>
                <div className="text-lg font-bold text-primary">{performanceMetrics.successRate}%</div>
                <div className="text-xs text-secondary">{performanceMetrics.completedBookings} programări finalizate</div>
              </div>

              <div className="bg-background rounded-2xl p-3 border border-border min-w-[240px] snap-start shrink-0">
                <div className="flex items-center gap-3 mb-2">
                  <Clock className="w-5 h-5 text-secondary" />
                  <span className="text-xs text-secondary">Timp Economisit</span>
                </div>
                <div className="text-lg font-bold text-primary">{performanceMetrics.timeSaved}h</div>
                <div className="text-xs text-secondary">Durată medie: {performanceMetrics.avgCallDuration}</div>
              </div>
            </HorizontalScroller>

            {/* Costs and Efficiency */}
            <div className="bg-background rounded-2xl p-4 border border-border">
              <h3 className="font-semibold text-primary mb-4 flex items-center gap-2">
                <DollarSign className="w-5 h-5" />
                Costuri și Eficiență
              </h3>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                <div className="p-3 bg-card rounded-2xl">
                  <div className="flex justify-between items-center">
                    <span className="text-secondary">Costuri Tokens (Luna curentă):</span>
                    <span className="font-semibold text-primary">{performanceMetrics.tokenCosts} RON</span>
                  </div>
                  <div className="text-xs text-secondary mt-1">
                    Cost mediu per apel: {(performanceMetrics.tokenCosts / performanceMetrics.totalCalls).toFixed(2)} RON
                  </div>
                </div>
                <div className="p-3 bg-card rounded-2xl">
                  <div className="flex justify-between items-center">
                    <span className="text-secondary">Economie estimată:</span>
                    <span className="font-semibold text-primary">{Math.round(performanceMetrics.timeSaved * 25)} RON</span>
                  </div>
                  <div className="text-xs text-secondary mt-1">
                    Bazat pe {performanceMetrics.timeSaved}h × 25 RON/oră salariu operator
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'config' && (
          <div className="space-y-6">
            {/* Voice Configuration */}
            <div className="bg-background rounded-2xl p-4 border border-border">
              <h3 className="font-semibold text-primary mb-4 flex items-center gap-2">
                <Volume2 className="w-5 h-5" />
                Configurare Voce
              </h3>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-primary mb-2">
                    Gen Voce
                  </label>
                  <div className="flex gap-2">
                    <button
                      onClick={() => setVoiceGender('female')}
                      className={clsx(
                        'px-4 py-2 rounded-2xl border transition-colors',
                        voiceGender === 'female'
                          ? 'bg-secondary/20 text-primary border-border'
                          : 'bg-background text-secondary border-border hover:text-primary'
                      )}
                    >
                      Feminin
                    </button>
                    <button
                      onClick={() => setVoiceGender('male')}
                      className={clsx(
                        'px-4 py-2 rounded-2xl border transition-colors',
                        voiceGender === 'male'
                          ? 'bg-secondary/20 text-primary border-border'
                          : 'bg-background text-secondary border-border hover:text-primary'
                      )}
                    >
                      Masculin
                    </button>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-primary mb-2">
                    Ton Voce
                  </label>
                  <select
                    value={voiceTone}
                    onChange={(e) => setVoiceTone(e.target.value as any)}
                    className="w-full px-4 py-2 bg-background border border-border rounded-2xl text-primary focus:outline-none focus:border-secondary transition-colors"
                  >
                    <option value="professional">Profesional</option>
                    <option value="friendly">Prietenos</option>
                    <option value="casual">Casual</option>
                  </select>
                </div>
              </div>
            </div>

            {/* Greeting Message */}
            <div className="bg-background rounded-2xl p-4 border border-border">
              <h3 className="font-semibold text-primary mb-4 flex items-center gap-2">
                <MessageSquare className="w-5 h-5" />
                Mesaj de Întâmpinare
              </h3>
              <textarea
                value={greetingMessage}
                onChange={(e) => setGreetingMessage(e.target.value)}
                rows={4}
                className="w-full px-4 py-2 bg-background border border-border rounded-2xl text-primary placeholder-secondary focus:outline-none focus:border-secondary transition-colors resize-none"
                placeholder="Introduceti mesajul de întâmpinare..."
              />
              <div className="mt-2 flex justify-between items-center">
                <span className="text-xs text-secondary">{greetingMessage.length}/500 caractere</span>
                <button className="flex items-center gap-1 px-3 py-1 text-xs bg-background text-secondary border border-border rounded-2xl hover:text-primary transition-colors">
                  <Play className="w-3 h-3" />
                  Testează Vocea
                </button>
              </div>
            </div>

            {/* Call Handling */}
            <div className="bg-background rounded-2xl p-4 border border-border">
              <h3 className="font-semibold text-primary mb-4 flex items-center gap-2">
                <Phone className="w-5 h-5" />
                Configurare Preluare Apeluri
              </h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-primary mb-2">
                    Când preia AI-ul apelurile?
                  </label>
                  <div className="space-y-2">
                    {[
                      { value: 'after_hours', label: 'Doar după program' },
                      { value: 'always', label: 'Întotdeauna' },
                      { value: 'when_busy', label: 'Doar când sunt ocupat' }
                    ].map((option) => (
                      <div key={option.value} className="flex items-center gap-3">
                        <input
                          type="radio"
                          id={option.value}
                          name="redirect_mode"
                          value={option.value}
                          checked={redirectMode === option.value}
                          onChange={(e) => setRedirectMode(e.target.value as any)}
                          className="w-4 h-4"
                        />
                        <label htmlFor={option.value} className="text-primary cursor-pointer">
                          {option.label}
                        </label>
                      </div>
                    ))}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-primary mb-2">
                    Număr Transfer (Fallback)
                  </label>
                  <input
                    type="tel"
                    value={transferNumber}
                    onChange={(e) => setTransferNumber(e.target.value)}
                    className="w-full px-4 py-2 bg-background border border-border rounded-2xl text-primary placeholder-secondary focus:outline-none focus:border-secondary transition-colors"
                    placeholder="+40 721 123 456"
                  />
                  <p className="mt-1 text-xs text-secondary">
                    Numărul la care AI-ul transferă apelul dacă nu reușește să finalizeze programarea
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'dictionary' && (
          <div className="space-y-6">
            {/* Dictionary Header */}
            <div className="bg-background rounded-2xl p-4 border border-border">
              <h3 className="font-semibold text-primary mb-2 flex items-center gap-2">
                <Brain className="w-5 h-5" />
                Dicționar și Sinonime AI
              </h3>
              <p className="text-sm text-secondary mb-4">
                Mapează termenii folosiți de clienți pe serviciile oficiale pentru a îmbunătăți înțelegerea AI-ului.
              </p>
              <button className="flex items-center px-4 py-2 bg-background text-secondary border border-border rounded-2xl hover:text-primary hover:border-secondary transition-colors">
                <Edit className="w-4 h-4 mr-2" />
                Adaugă Mapare Nouă
              </button>
            </div>

            {/* Dictionary Table */}
            <div className="bg-background rounded-2xl border border-border overflow-hidden">
              <div className="grid grid-cols-12 gap-4 p-4 border-b border-border text-xs font-semibold text-secondary uppercase tracking-wider">
                <div className="col-span-4">Termen Client</div>
                <div className="col-span-4">Serviciu Oficial</div>
                <div className="col-span-2">Frecvență</div>
                <div className="col-span-2 text-center">Acțiuni</div>
              </div>
              
              <div className="divide-y divide-border">
                {dictionary.map((item, index) => (
                  <div key={index} className="grid grid-cols-12 gap-4 p-4 hover:bg-card-hover transition-colors">
                    <div className="col-span-4">
                      <span className="font-medium text-primary">&quot;{item.clientTerm}&quot;</span>
                    </div>
                    <div className="col-span-4">
                      <span className="text-primary">{item.officialService}</span>
                    </div>
                    <div className="col-span-2">
                      <div className="flex items-center gap-2">
                        <div className="flex-1 bg-card rounded-full h-2">
                          <div 
                            className="bg-secondary/30 h-2 rounded-full"
                            style={{ width: `${(item.frequency / 70) * 100}%` }}
                          ></div>
                        </div>
                        <span className="text-xs text-secondary">{item.frequency}</span>
                      </div>
                    </div>
                    <div className="col-span-2 text-center">
                      <div className="flex items-center justify-center gap-1">
                        <button className="p-1 text-secondary hover:text-primary rounded transition-colors">
                          <Edit className="w-4 h-4" />
                        </button>
                        <button className="p-1 text-secondary hover:text-primary rounded transition-colors">
                          <XCircle className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'logs' && (
          <div className="space-y-6">
            {/* Search and Filters */}
            <div className="flex flex-col lg:flex-row gap-4">
              <div className="flex-1 relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-secondary" />
                <input
                  type="text"
                  placeholder="Căutare după număr telefon sau intenție..."
                  className="w-full pl-10 pr-4 py-2 bg-background border border-border rounded-2xl text-primary placeholder-secondary focus:outline-none focus:border-secondary transition-colors"
                />
              </div>
              <div className="flex gap-2">
                <button className="flex items-center px-4 py-2 bg-background text-secondary border border-border rounded-2xl hover:text-primary hover:border-secondary transition-colors">
                  <Filter className="w-4 h-4 mr-2" />
                  Filtrare
                </button>
                <button className="flex items-center px-4 py-2 bg-background text-secondary border border-border rounded-2xl hover:text-primary hover:border-secondary transition-colors">
                  <Download className="w-4 h-4 mr-2" />
                  Export CSV
                </button>
              </div>
            </div>

            {/* Call Logs Table */}
            <div className="bg-background rounded-2xl border border-border overflow-hidden">
              <div className="grid grid-cols-12 gap-4 p-4 border-b border-border text-xs font-semibold text-secondary uppercase tracking-wider">
                <div className="col-span-2">Data/Ora</div>
                <div className="col-span-2">Număr Apelant</div>
                <div className="col-span-3">Intenție Detectată</div>
                <div className="col-span-2">Rezultat</div>
                <div className="col-span-1">Durată</div>
                <div className="col-span-2 text-center">Acțiuni</div>
              </div>
              
              <div className="divide-y divide-border">
                {callLogs.map((call) => (
                  <div key={call.id} className="grid grid-cols-12 gap-4 p-4 hover:bg-card-hover transition-colors">
                    <div className="col-span-2">
                      <div className="text-sm text-primary">{call.date}</div>
                      <div className="text-xs text-secondary">{call.time}</div>
                    </div>
                    <div className="col-span-2">
                      <span className="text-primary font-mono">{call.phoneNumber}</span>
                    </div>
                    <div className="col-span-3">
                      <span className="text-primary">{call.detectedIntent}</span>
                    </div>
                    <div className="col-span-2">
                      {getResultBadge(call.result)}
                    </div>
                    <div className="col-span-1">
                      <span className="text-secondary font-mono">{call.duration}</span>
                    </div>
                    <div className="col-span-2 text-center">
                      <div className="flex items-center justify-center gap-1">
                        {call.hasTranscript && (
                          <button className="p-1 text-secondary hover:text-primary rounded transition-colors" title="Vezi transcriere">
                            <FileText className="w-4 h-4" />
                          </button>
                        )}
                        {call.hasRecording && (
                          <button className="p-1 text-secondary hover:text-primary rounded transition-colors" title="Ascultă înregistrarea">
                            <Play className="w-4 h-4" />
                          </button>
                        )}
                        <button className="p-1 text-secondary hover:text-primary rounded transition-colors" title="Vezi detalii">
                          <Eye className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Call Summary */}
            <div className="bg-background rounded-2xl p-4 border border-border">
              <h3 className="font-semibold text-primary mb-3">Rezumat Apeluri</h3>
              <div className="hidden lg:grid lg:grid-cols-3 lg:gap-4">
                <div className="text-center">
                  <div className="text-2xl font-bold text-primary">
                    {callLogs.filter(c => c.result === 'completed').length}
                  </div>
                  <div className="text-sm text-secondary">Finalizate</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-primary">
                    {callLogs.filter(c => c.result === 'transferred').length}
                  </div>
                  <div className="text-sm text-secondary">Transferate</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-primary">
                    {callLogs.filter(c => c.result === 'abandoned').length}
                  </div>
                  <div className="text-sm text-secondary">Abandonate</div>
                </div>
              </div>

              <HorizontalScroller>
                <div className="text-center min-w-[120px] snap-start shrink-0">
                  <div className="text-lg font-bold text-primary">
                    {callLogs.filter(c => c.result === 'completed').length}
                  </div>
                  <div className="text-xs text-secondary">Finalizate</div>
                </div>
                <div className="text-center min-w-[120px] snap-start shrink-0">
                  <div className="text-lg font-bold text-primary">
                    {callLogs.filter(c => c.result === 'transferred').length}
                  </div>
                  <div className="text-xs text-secondary">Transferate</div>
                </div>
                <div className="text-center min-w-[120px] snap-start shrink-0">
                  <div className="text-lg font-bold text-primary">
                    {callLogs.filter(c => c.result === 'abandoned').length}
                  </div>
                  <div className="text-xs text-secondary">Abandonate</div>
                </div>
              </HorizontalScroller>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}