'use client'

import clsx from "clsx"

import { useState } from 'react'
import {
  Settings,
  Building2,
  Clock,
  Calendar,
  Users,
  Bell,
  Plug,
  CreditCard,
  Upload,
  Save,
  Edit,
  Trash2,
  Plus,
  CheckCircle,
  XCircle,
  AlertCircle,
  Globe,
  Phone,
  Mail,
  MapPin,
  Shield,
  Crown,
  Menu
} from 'lucide-react'
import ResponsiveTable, { ResponsiveTableRow, ResponsiveTableCell } from '../ui/ResponsiveTable'


interface BusinessHours {
  [key: string]: {
    isOpen: boolean
    openTime: string
    closeTime: string
    breaks: Array<{ start: string; end: string; name: string }>
  }
}

interface User {
  id: string
  name: string
  email: string
  role: 'Admin' | 'Staff'
  status: 'active' | 'inactive'
  lastLogin: string
}

interface SettingsPanelProps {
  isMobile?: boolean
  onMobileToggle?: () => void
}

export default function SettingsPanel({ isMobile, onMobileToggle }: SettingsPanelProps) {
  const [activeTab, setActiveTab] = useState<'business' | 'schedule' | 'integrations' | 'notifications' | 'users' | 'billing'>('business')
  
  // Business details
  const [businessDetails, setBusinessDetails] = useState({
    name: 'Voice Booking Salon',
    address: 'Strada Exemplu nr. 123, Sector 1, București',
    phone: '+40 721 123 456',
    email: 'contact@voicebooking.ro',
    website: 'www.voicebooking.ro',
    timezone: 'Europe/Bucharest'
  })

  // Business hours mock
  const [businessHours, setBusinessHours] = useState<BusinessHours>({
    monday: { isOpen: true, openTime: '09:00', closeTime: '18:00', breaks: [{ start: '13:00', end: '14:00', name: 'Pauza de masă' }] },
    tuesday: { isOpen: true, openTime: '09:00', closeTime: '18:00', breaks: [{ start: '13:00', end: '14:00', name: 'Pauza de masă' }] },
    wednesday: { isOpen: true, openTime: '09:00', closeTime: '18:00', breaks: [{ start: '13:00', end: '14:00', name: 'Pauza de masă' }] },
    thursday: { isOpen: true, openTime: '09:00', closeTime: '18:00', breaks: [{ start: '13:00', end: '14:00', name: 'Pauza de masă' }] },
    friday: { isOpen: true, openTime: '09:00', closeTime: '18:00', breaks: [{ start: '13:00', end: '14:00', name: 'Pauza de masă' }] },
    saturday: { isOpen: true, openTime: '10:00', closeTime: '16:00', breaks: [] },
    sunday: { isOpen: false, openTime: '10:00', closeTime: '16:00', breaks: [] }
  })

  // Integrations status
  const integrations = [
    { name: 'Google Calendar', status: 'connected', description: 'Sincronizare programări cu calendarul', lastSync: '2025-01-31 10:30' },
    { name: 'SMS Gateway', status: 'connected', description: 'Trimitere SMS-uri automate clienților', provider: 'Twilio' },
    { name: 'Email Service', status: 'connected', description: 'Trimitere email-uri și notificări', provider: 'SendGrid' },
    { name: 'Payment Gateway', status: 'disconnected', description: 'Procesare plăți online', provider: 'Stripe' },
    { name: 'Analytics', status: 'connected', description: 'Urmărire performanță și statistici', provider: 'Google Analytics' }
  ]

  // Users mock
  const [users, setUsers] = useState<User[]>([
    { id: '1', name: 'Alexandra Ionescu', email: 'alexandra@voicebooking.ro', role: 'Admin', status: 'active', lastLogin: '2025-01-31 09:15' },
    { id: '2', name: 'Maria Popescu', email: 'maria@voicebooking.ro', role: 'Staff', status: 'active', lastLogin: '2025-01-30 16:45' },
    { id: '3', name: 'Ana Radu', email: 'ana@voicebooking.ro', role: 'Staff', status: 'inactive', lastLogin: '2025-01-28 14:20' }
  ])

  // Notification settings
  const [notificationSettings, setNotificationSettings] = useState({
    emailReminders: true,
    smsReminders: true,
    emailReminderTime: '24', // hours before
    smsReminderTime: '2', // hours before
    emailTemplate: 'Bună ziua! Vă reamintim despre programarea dvs. de mâine la ora {time}. Pentru reprogramare, sunați la {phone}.',
    smsTemplate: 'Programare mâine la {time}. Pentru modificări: {phone}'
  })

  // Billing mock
  const billingInfo = {
    currentPlan: 'Professional',
    price: '199 RON/lună',
    billingCycle: 'Lunar',
    nextBilling: '2025-02-28',
    features: ['Până la 500 clienți', 'Agent vocal AI', 'Integrări complete', 'Rapoarte avansate', 'Suport prioritar'],
    paymentMethod: '**** **** **** 1234',
    billingHistory: [
      { date: '2025-01-01', amount: '199 RON', status: 'paid', invoice: 'VB-2025-001' },
      { date: '2024-12-01', amount: '199 RON', status: 'paid', invoice: 'VB-2024-012' },
      { date: '2024-11-01', amount: '199 RON', status: 'paid', invoice: 'VB-2024-011' }
    ]
  }

  const getDayName = (key: string) => {
    const days = {
      monday: 'Luni',
      tuesday: 'Marți', 
      wednesday: 'Miercuri',
      thursday: 'Joi',
      friday: 'Vineri',
      saturday: 'Sâmbătă',
      sunday: 'Duminică'
    }
    return days[key as keyof typeof days] || key
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'connected': return <CheckCircle className="w-4 h-4 text-primary" />
      case 'disconnected': return <XCircle className="w-4 h-4 text-secondary" />
      default: return <AlertCircle className="w-4 h-4 text-secondary" />
    }
  }

  const getRoleBadge = (role: User['role']) => {
    const styles = {
      Admin: 'bg-secondary/20 text-primary border-border',
      Staff: 'bg-secondary/20 text-secondary border-border'
    }
    
    return (
      <span className={clsx(
        'inline-flex items-center px-2 py-1 rounded-2xl text-xs font-medium border',
        styles[role]
      )}>
        {role === 'Admin' && <Shield className="w-3 h-3 mr-1" />}
        {role}
      </span>
    )
  }

  return (
    <div className="flex-1 flex flex-col bg-card h-full">
      {/* Header */}
      <div className="p-6 lg:p-6 md:p-3 sm:p-3 border-b border-border">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3 lg:gap-3 md:gap-3 sm:gap-3">
            {isMobile && (
              <button 
                onClick={onMobileToggle}
                className="p-2 text-secondary hover:text-primary rounded-2xl hover:bg-card-hover transition-colors"
              >
                <Menu className="w-5 h-5" />
              </button>
            )}
            <Settings className="w-8 h-8 lg:w-8 lg:h-8 md:w-6 md:h-6 sm:w-6 sm:h-6 text-secondary" />
            <div>
              <h1 className="text-3xl lg:text-3xl md:text-sm sm:text-sm font-bold lg:font-bold md:font-semibold sm:font-semibold text-primary">Setări</h1>
              <p className="text-base lg:text-base md:text-sm sm:text-sm text-secondary">
                Configurarea afacerii și aplicației
              </p>
            </div>
          </div>
          <button className="hidden lg:flex md:flex items-center px-4 py-2 lg:px-4 lg:py-2 md:px-3 md:py-2 sm:px-3 sm:py-2 bg-background text-secondary lg:text-secondary md:text-sm sm:text-sm border border-border rounded-2xl hover:text-primary hover:border-secondary transition-colors">
            <Save className="w-4 h-4 mr-2 lg:mr-2 md:mr-1 sm:mr-1" />
            <span className="lg:inline md:text-sm sm:text-sm">Salvează Toate</span>
          </button>
        </div>

        {/* Tabs */}
        <div className="flex gap-8 lg:gap-8 md:gap-3 sm:gap-3 overflow-x-auto">
          {[
            { key: 'business', label: 'Detalii Afacere', icon: Building2 },
            { key: 'schedule', label: 'Program Lucru', icon: Clock },
            { key: 'integrations', label: 'Integrări', icon: Plug },
            { key: 'notifications', label: 'Notificări', icon: Bell },
            { key: 'users', label: 'Utilizatori', icon: Users },
            { key: 'billing', label: 'Facturare', icon: CreditCard }
          ].map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key as any)}
              className={clsx(
                'flex items-center gap-2 lg:gap-2 md:gap-3 sm:gap-3 py-3 lg:py-3 md:py-2 sm:py-2 border-b-2 transition-colors whitespace-nowrap text-sm',
                activeTab === tab.key
                  ? 'border-secondary text-primary'
                  : 'border-transparent text-secondary hover:text-primary'
              )}
            >
              <tab.icon className="w-4 h-4" />
              <span className="lg:inline md:text-sm sm:text-sm">{tab.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-6 lg:p-6 md:p-3 sm:p-3">
        {activeTab === 'business' && (
          <div className="space-y-6">
            {/* Business Information */}
            <div className="bg-background rounded-2xl p-6 border border-border">
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-semibold text-primary flex items-center gap-2">
                  <Building2 className="w-5 h-5" />
                  Informații Afacere
                </h3>
                <button className="flex items-center gap-2 px-3 py-1 bg-background text-secondary border border-border rounded-2xl hover:text-primary transition-colors">
                  <Edit className="w-4 h-4" />
                  Editează
                </button>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-primary mb-2">Nume Salon</label>
                    <input
                      type="text"
                      value={businessDetails.name}
                      onChange={(e) => setBusinessDetails(prev => ({ ...prev, name: e.target.value }))}
                      className="w-full px-4 py-2 bg-background border border-border rounded-2xl text-primary focus:outline-none focus:border-secondary transition-colors"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-primary mb-2">Adresă</label>
                    <textarea
                      value={businessDetails.address}
                      onChange={(e) => setBusinessDetails(prev => ({ ...prev, address: e.target.value }))}
                      rows={3}
                      className="w-full px-4 py-2 bg-background border border-border rounded-2xl text-primary focus:outline-none focus:border-secondary transition-colors resize-none"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-primary mb-2">Telefon</label>
                    <div className="relative">
                      <Phone className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-secondary" />
                      <input
                        type="tel"
                        value={businessDetails.phone}
                        onChange={(e) => setBusinessDetails(prev => ({ ...prev, phone: e.target.value }))}
                        className="w-full pl-10 pr-4 py-2 bg-background border border-border rounded-2xl text-primary focus:outline-none focus:border-secondary transition-colors"
                      />
                    </div>
                  </div>
                </div>

                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-primary mb-2">Email</label>
                    <div className="relative">
                      <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-secondary" />
                      <input
                        type="email"
                        value={businessDetails.email}
                        onChange={(e) => setBusinessDetails(prev => ({ ...prev, email: e.target.value }))}
                        className="w-full pl-10 pr-4 py-2 bg-background border border-border rounded-2xl text-primary focus:outline-none focus:border-secondary transition-colors"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-primary mb-2">Website</label>
                    <div className="relative">
                      <Globe className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-secondary" />
                      <input
                        type="url"
                        value={businessDetails.website}
                        onChange={(e) => setBusinessDetails(prev => ({ ...prev, website: e.target.value }))}
                        className="w-full pl-10 pr-4 py-2 bg-background border border-border rounded-2xl text-primary focus:outline-none focus:border-secondary transition-colors"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-primary mb-2">Fus Orar</label>
                    <select
                      value={businessDetails.timezone}
                      onChange={(e) => setBusinessDetails(prev => ({ ...prev, timezone: e.target.value }))}
                      className="w-full px-4 py-2 bg-background border border-border rounded-2xl text-primary focus:outline-none focus:border-secondary transition-colors"
                    >
                      <option value="Europe/Bucharest">Europa/București (UTC+2)</option>
                      <option value="Europe/London">Europa/Londra (UTC+0)</option>
                      <option value="Europe/Paris">Europa/Paris (UTC+1)</option>
                    </select>
                    <p className="mt-1 text-xs text-secondary">
                      Crucial pentru corectitudinea programărilor și sincronizarea cu Google Calendar
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Logo Upload */}
            <div className="bg-background rounded-2xl p-6 border border-border">
              <h3 className="font-semibold text-primary mb-4 flex items-center gap-2">
                <Upload className="w-5 h-5" />
                Logo Salon
              </h3>
              <div className="flex items-center gap-6">
                <div className="w-24 h-24 bg-secondary/20 rounded-2xl flex items-center justify-center border border-border">
                  <Building2 className="w-8 h-8 text-secondary" />
                </div>
                <div className="space-y-2">
                  <button className="flex items-center px-4 py-2 bg-background text-secondary border border-border rounded-2xl hover:text-primary hover:border-secondary transition-colors">
                    <Upload className="w-4 h-4 mr-2" />
                    Încarcă Logo
                  </button>
                  <p className="text-xs text-secondary">
                    Format recomandat: PNG sau JPG, dimensiune minimă 200x200px
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'schedule' && (
          <div className="space-y-6">
            {/* Business Hours */}
            <div className="bg-background rounded-2xl p-6 border border-border">
              <h3 className="font-semibold text-primary mb-4 flex items-center gap-2">
                <Clock className="w-5 h-5" />
                Program de Lucru
              </h3>
              
              <div className="space-y-4">
                {Object.entries(businessHours).map(([day, hours]) => (
                  <div key={day} className="flex items-center gap-4 p-4 bg-card rounded-2xl">
                    <div className="w-24">
                      <span className="font-medium text-primary">{getDayName(day)}</span>
                    </div>
                    
                    <div className="flex items-center gap-2">
                      <input
                        type="checkbox"
                        checked={hours.isOpen}
                        onChange={(e) => setBusinessHours(prev => ({
                          ...prev,
                          [day]: { ...prev[day], isOpen: e.target.checked }
                        }))}
                        className="w-4 h-4"
                      />
                      <span className="text-sm text-secondary">Deschis</span>
                    </div>
                    
                    {hours.isOpen ? (
                      <div className="flex items-center gap-2">
                        <input
                          type="time"
                          value={hours.openTime}
                          onChange={(e) => setBusinessHours(prev => ({
                            ...prev,
                            [day]: { ...prev[day], openTime: e.target.value }
                          }))}
                          className="px-3 py-1 bg-background border border-border rounded-2xl text-primary focus:outline-none focus:border-secondary"
                        />
                        <span className="text-secondary">—</span>
                        <input
                          type="time"
                          value={hours.closeTime}
                          onChange={(e) => setBusinessHours(prev => ({
                            ...prev,
                            [day]: { ...prev[day], closeTime: e.target.value }
                          }))}
                          className="px-3 py-1 bg-background border border-border rounded-2xl text-primary focus:outline-none focus:border-secondary"
                        />
                      </div>
                    ) : (
                      <span className="text-secondary">Închis</span>
                    )}

                    {hours.breaks.length > 0 && (
                      <div className="flex items-center gap-2 text-sm text-secondary overflow-x-auto">
                        <span className="flex-shrink-0">Pauze:</span>
                        <div className="flex items-center gap-2 min-w-0">
                          {hours.breaks.map((br, i) => (
                            <span key={i} className="px-2 py-1 bg-background rounded text-xs flex-shrink-0">
                              {br.start}-{br.end} ({br.name})
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>

              <div className="mt-4 p-3 bg-secondary/10 rounded-2xl">
                <p className="text-sm text-secondary">
                  <strong className="text-primary">Notă:</strong> Programul de lucru afectează disponibilitatea pentru programări și comportamentul Agent-ului Vocal.
                </p>
              </div>
            </div>

            {/* Holidays */}
            <div className="bg-background rounded-2xl p-6 border border-border">
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-semibold text-primary flex items-center gap-2">
                  <Calendar className="w-5 h-5" />
                  Zile Libere și Sărbători
                </h3>
                <button className="flex items-center px-4 py-2 bg-background text-secondary border border-border rounded-2xl hover:text-primary hover:border-secondary transition-colors">
                  <Plus className="w-4 h-4 mr-2" />
                  Adaugă Zi Liberă
                </button>
              </div>

              <div className="space-y-2">
                {[
                  { date: '2025-01-01', name: 'Anul Nou', type: 'Sărbătoare' },
                  { date: '2025-01-06', name: 'Boboteaza', type: 'Sărbătoare' },
                  { date: '2025-02-15', name: 'Concediu personal', type: 'Zi liberă' }
                ].map((holiday, index) => (
                  <div key={index} className="flex items-center justify-between p-3 bg-card rounded-2xl">
                    <div>
                      <span className="font-medium text-primary">{holiday.name}</span>
                      <span className="ml-2 text-sm text-secondary">({holiday.date})</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="px-2 py-1 bg-secondary/20 text-secondary text-xs rounded-2xl">
                        {holiday.type}
                      </span>
                      <button className="p-1 text-secondary hover:text-primary transition-colors">
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'integrations' && (
          <div className="space-y-6">
            <div className="bg-background rounded-2xl p-6 border border-border">
              <h3 className="font-semibold text-primary mb-4 flex items-center gap-2">
                <Plug className="w-5 h-5" />
                Integrări și Conexiuni
              </h3>
              
              <div className="space-y-4">
                {integrations.map((integration, index) => (
                  <div key={index} className="flex items-center justify-between p-4 bg-card rounded-2xl">
                    <div className="flex items-center gap-4">
                      {getStatusIcon(integration.status)}
                      <div>
                        <div className="font-medium text-primary">{integration.name}</div>
                        <div className="text-sm text-secondary">{integration.description}</div>
                        {integration.provider && (
                          <div className="text-xs text-secondary mt-1">Provider: {integration.provider}</div>
                        )}
                        {integration.lastSync && (
                          <div className="text-xs text-secondary">Ultima sincronizare: {integration.lastSync}</div>
                        )}
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      {integration.status === 'connected' ? (
                        <button className="px-3 py-1 bg-background text-secondary border border-border rounded-2xl hover:text-primary transition-colors">
                          Configurează
                        </button>
                      ) : (
                        <button className="px-3 py-1 bg-background text-secondary border border-border rounded-2xl hover:text-primary hover:border-secondary transition-colors">
                          Conectează
                        </button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'notifications' && (
          <div className="space-y-6">
            {/* Notification Settings */}
            <div className="bg-background rounded-2xl p-6 border border-border">
              <h3 className="font-semibold text-primary mb-4 flex items-center gap-2">
                <Bell className="w-5 h-5" />
                Configurare Notificări
              </h3>
              
              <div className="space-y-6">
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <div className="font-medium text-primary">Reminder-uri Email</div>
                        <div className="text-sm text-secondary">Trimite email-uri automate clienților</div>
                      </div>
                      <button
                        onClick={() => setNotificationSettings(prev => ({ ...prev, emailReminders: !prev.emailReminders }))}
                        className="flex items-center gap-2 text-secondary hover:text-primary transition-colors"
                      >
                        {notificationSettings.emailReminders ? (
                          <CheckCircle className="w-5 h-5 text-primary" />
                        ) : (
                          <XCircle className="w-5 h-5" />
                        )}
                      </button>
                    </div>

                    <div className="flex items-center justify-between">
                      <div>
                        <div className="font-medium text-primary">Reminder-uri SMS</div>
                        <div className="text-sm text-secondary">Trimite SMS-uri automate clienților</div>
                      </div>
                      <button
                        onClick={() => setNotificationSettings(prev => ({ ...prev, smsReminders: !prev.smsReminders }))}
                        className="flex items-center gap-2 text-secondary hover:text-primary transition-colors"
                      >
                        {notificationSettings.smsReminders ? (
                          <CheckCircle className="w-5 h-5 text-primary" />
                        ) : (
                          <XCircle className="w-5 h-5" />
                        )}
                      </button>
                    </div>
                  </div>

                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-primary mb-2">
                        Timp Email Reminder (ore înainte)
                      </label>
                      <select
                        value={notificationSettings.emailReminderTime}
                        onChange={(e) => setNotificationSettings(prev => ({ ...prev, emailReminderTime: e.target.value }))}
                        className="w-full px-4 py-2 bg-background border border-border rounded-2xl text-primary focus:outline-none focus:border-secondary"
                      >
                        <option value="2">2 ore înainte</option>
                        <option value="4">4 ore înainte</option>
                        <option value="24">24 ore înainte</option>
                        <option value="48">48 ore înainte</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-primary mb-2">
                        Timp SMS Reminder (ore înainte)
                      </label>
                      <select
                        value={notificationSettings.smsReminderTime}
                        onChange={(e) => setNotificationSettings(prev => ({ ...prev, smsReminderTime: e.target.value }))}
                        className="w-full px-4 py-2 bg-background border border-border rounded-2xl text-primary focus:outline-none focus:border-secondary"
                      >
                        <option value="1">1 oră înainte</option>
                        <option value="2">2 ore înainte</option>
                        <option value="4">4 ore înainte</option>
                      </select>
                    </div>
                  </div>
                </div>

                {/* Email Template */}
                <div>
                  <label className="block text-sm font-medium text-primary mb-2">
                    Template Email Reminder
                  </label>
                  <textarea
                    value={notificationSettings.emailTemplate}
                    onChange={(e) => setNotificationSettings(prev => ({ ...prev, emailTemplate: e.target.value }))}
                    rows={4}
                    className="w-full px-4 py-2 bg-background border border-border rounded-2xl text-primary focus:outline-none focus:border-secondary resize-none"
                  />
                  <p className="mt-1 text-xs text-secondary">
                    Variabile disponibile: {'{time}'}, {'{phone}'}, {'{client_name}'}, {'{service}'}
                  </p>
                </div>

                {/* SMS Template */}
                <div>
                  <label className="block text-sm font-medium text-primary mb-2">
                    Template SMS Reminder
                  </label>
                  <textarea
                    value={notificationSettings.smsTemplate}
                    onChange={(e) => setNotificationSettings(prev => ({ ...prev, smsTemplate: e.target.value }))}
                    rows={2}
                    className="w-full px-4 py-2 bg-background border border-border rounded-2xl text-primary focus:outline-none focus:border-secondary resize-none"
                  />
                  <div className="mt-1 flex justify-between items-center">
                    <p className="text-xs text-secondary">
                      Variabile: {'{time}'}, {'{phone}'}, {'{client_name}'}
                    </p>
                    <span className="text-xs text-secondary">
                      {notificationSettings.smsTemplate.length}/160 caractere
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'users' && (
          <div className="space-y-6">
            {/* Add User */}
            <div className="bg-background rounded-2xl p-6 border border-border">
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-semibold text-primary flex items-center gap-2">
                  <Users className="w-5 h-5" />
                  Management Utilizatori
                </h3>
                <button className="flex items-center px-4 py-2 bg-background text-secondary border border-border rounded-2xl hover:text-primary hover:border-secondary transition-colors">
                  <Plus className="w-4 h-4 mr-2" />
                  Invită Utilizator
                </button>
              </div>

              {/* Users Table */}
              <ResponsiveTable
                columns={[
                  { key: 'user', label: 'Utilizator', minWidth: '200px' },
                  { key: 'email', label: 'Email', minWidth: '200px' },
                  { key: 'role', label: 'Rol', minWidth: '120px' },
                  { key: 'lastLogin', label: 'Ultima Conectare', minWidth: '150px' },
                  { key: 'actions', label: 'Acțiuni', minWidth: '120px', className: 'text-center' }
                ]}
                mobileMinWidth="800px"
              >
                {users.map((user) => (
                  <ResponsiveTableRow
                    key={user.id}
                    columns={[
                      { key: 'user', label: 'Utilizator', minWidth: '200px' },
                      { key: 'email', label: 'Email', minWidth: '200px' },
                      { key: 'role', label: 'Rol', minWidth: '120px' },
                      { key: 'lastLogin', label: 'Ultima Conectare', minWidth: '150px' },
                      { key: 'actions', label: 'Acțiuni', minWidth: '120px', className: 'text-center' }
                    ]}
                  >
                    <ResponsiveTableCell column={{ key: 'user', label: 'Utilizator', minWidth: '200px' }}>
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-full bg-secondary/20 flex items-center justify-center text-primary font-semibold text-sm">
                          {user.name.split(' ').map(n => n[0]).join('').toUpperCase()}
                        </div>
                        <div>
                          <div className="font-medium text-primary">{user.name}</div>
                          <div className={clsx(
                            "text-xs",
                            user.status === 'active' ? 'text-primary' : 'text-secondary'
                          )}>
                            {user.status === 'active' ? 'Activ' : 'Inactiv'}
                          </div>
                        </div>
                      </div>
                    </ResponsiveTableCell>

                    <ResponsiveTableCell column={{ key: 'email', label: 'Email', minWidth: '200px' }}>
                      <span className="text-primary">{user.email}</span>
                    </ResponsiveTableCell>

                    <ResponsiveTableCell column={{ key: 'role', label: 'Rol', minWidth: '120px' }}>
                      {getRoleBadge(user.role)}
                    </ResponsiveTableCell>

                    <ResponsiveTableCell column={{ key: 'lastLogin', label: 'Ultima Conectare', minWidth: '150px' }}>
                      <div className="text-sm text-primary">{user.lastLogin}</div>
                    </ResponsiveTableCell>

                    <ResponsiveTableCell column={{ key: 'actions', label: 'Acțiuni', minWidth: '120px', className: 'text-center' }}>
                      <div className="flex items-center justify-center gap-1">
                        <button className="p-1 text-secondary hover:text-primary rounded transition-colors">
                          <Edit className="w-4 h-4" />
                        </button>
                        {user.role !== 'Admin' && (
                          <button className="p-1 text-secondary hover:text-primary rounded transition-colors">
                            <Trash2 className="w-4 h-4" />
                          </button>
                        )}
                      </div>
                    </ResponsiveTableCell>
                  </ResponsiveTableRow>
                ))}
              </ResponsiveTable>
            </div>
          </div>
        )}

        {activeTab === 'billing' && (
          <div className="space-y-6">
            {/* Current Plan */}
            <div className="bg-background rounded-2xl p-6 border border-border">
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-semibold text-primary flex items-center gap-2">
                  <Crown className="w-5 h-5" />
                  Plan Actual
                </h3>
                <div className="flex items-center gap-2">
                  <span className="px-3 py-1 bg-secondary/20 text-primary text-sm rounded-2xl border border-border">
                    {billingInfo.currentPlan}
                  </span>
                </div>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="lg:col-span-2">
                  <div className="mb-4">
                    <div className="text-3xl font-bold text-primary mb-1">{billingInfo.price}</div>
                    <div className="text-secondary">Facturare {billingInfo.billingCycle.toLowerCase()}</div>
                    <div className="text-sm text-secondary mt-1">
                      Următoarea factură: {billingInfo.nextBilling}
                    </div>
                  </div>

                  <div className="space-y-2">
                    <h4 className="font-medium text-primary">Funcționalități incluse:</h4>
                    {billingInfo.features.map((feature, index) => (
                      <div key={index} className="flex items-center gap-2">
                        <CheckCircle className="w-4 h-4 text-primary" />
                        <span className="text-sm text-primary">{feature}</span>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="space-y-4">
                  <div className="p-4 bg-card rounded-2xl border border-border">
                    <div className="text-sm text-secondary mb-1">Metodă de plată</div>
                    <div className="font-medium text-primary">{billingInfo.paymentMethod}</div>
                  </div>
                  <button className="w-full px-4 py-2 bg-background text-secondary border border-border rounded-2xl hover:text-primary hover:border-secondary transition-colors">
                    Actualizează Metoda de Plată
                  </button>
                  <button className="w-full px-4 py-2 bg-background text-secondary border border-border rounded-2xl hover:text-primary hover:border-secondary transition-colors">
                    Schimbă Planul
                  </button>
                </div>
              </div>
            </div>

            {/* Billing History */}
            <div className="bg-background rounded-2xl p-6 border border-border">
              <h3 className="font-semibold text-primary mb-4 flex items-center gap-2">
                <CreditCard className="w-5 h-5" />
                Istoric Facturare
              </h3>

              <ResponsiveTable
                columns={[
                  { key: 'date', label: 'Data', minWidth: '120px' },
                  { key: 'amount', label: 'Sumă', minWidth: '120px' },
                  { key: 'status', label: 'Status', minWidth: '120px' },
                  { key: 'invoice', label: 'Factură', minWidth: '150px' }
                ]}
                mobileMinWidth="600px"
              >
                {billingInfo.billingHistory.map((bill, index) => (
                  <ResponsiveTableRow
                    key={index}
                    columns={[
                      { key: 'date', label: 'Data', minWidth: '120px' },
                      { key: 'amount', label: 'Sumă', minWidth: '120px' },
                      { key: 'status', label: 'Status', minWidth: '120px' },
                      { key: 'invoice', label: 'Factură', minWidth: '150px' }
                    ]}
                  >
                    <ResponsiveTableCell column={{ key: 'date', label: 'Data', minWidth: '120px' }}>
                      <span className="text-primary">{bill.date}</span>
                    </ResponsiveTableCell>

                    <ResponsiveTableCell column={{ key: 'amount', label: 'Sumă', minWidth: '120px' }}>
                      <span className="font-semibold text-primary">{bill.amount}</span>
                    </ResponsiveTableCell>

                    <ResponsiveTableCell column={{ key: 'status', label: 'Status', minWidth: '120px' }}>
                      <span className={clsx(
                        "inline-flex items-center px-2 py-1 rounded-2xl text-xs font-medium border",
                        bill.status === 'paid' 
                          ? 'bg-secondary/20 text-primary border-border'
                          : 'bg-secondary/20 text-secondary border-border'
                      )}>
                        {bill.status === 'paid' ? 'Plătit' : 'Nepilătit'}
                      </span>
                    </ResponsiveTableCell>

                    <ResponsiveTableCell column={{ key: 'invoice', label: 'Factură', minWidth: '150px' }}>
                      <button className="text-secondary hover:text-primary underline text-sm transition-colors">
                        {bill.invoice}
                      </button>
                    </ResponsiveTableCell>
                  </ResponsiveTableRow>
                ))}
              </ResponsiveTable>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}