'use client'

import { useState, useRef } from 'react'
import { 
  X, 
  Upload,
  Settings,
  CheckCircle,
  AlertCircle,
  Loader,
  ExternalLink,
  Play,
  RotateCcw,
  Power,
  PowerOff
} from 'lucide-react'
import { useCalendar } from '../../hooks/useCalendar'

interface CalendarSetupModalProps {
  isOpen: boolean
  onClose: () => void
  onSuccess?: () => void
  existingCalendar?: any
}

export default function CalendarSetupModal({ isOpen, onClose, onSuccess, existingCalendar }: CalendarSetupModalProps) {
  const [step, setStep] = useState(existingCalendar ? 'manage' : 'setup')
  const [formData, setFormData] = useState({
    calendar_name: existingCalendar?.calendar_name || '',
    google_calendar_id: existingCalendar?.calendar_id || '',
    timezone: existingCalendar?.timezone || 'Europe/Bucharest',
    auto_create_events: existingCalendar?.auto_create_events ?? true
  })
  const [credentialsFile, setCredentialsFile] = useState<File | null>(null)
  const [credentialsJson, setCredentialsJson] = useState('')
  const [showGuide, setShowGuide] = useState(false)
  const [testResult, setTestResult] = useState<any>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const { 
    setupCalendar, 
    testCalendar, 
    enableCalendar, 
    disableCalendar, 
    loading, 
    error 
  } = useCalendar()

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    try {
      const text = await file.text()
      const json = JSON.parse(text)
      
      // Validate JSON structure
      if (!json.type || json.type !== 'service_account') {
        throw new Error('Fișierul JSON trebuie să fie un Service Account')
      }
      
      if (!json.project_id || !json.private_key || !json.client_email) {
        throw new Error('Fișierul JSON nu conține toate câmpurile necesare')
      }

      setCredentialsFile(file)
      setCredentialsJson(btoa(text)) // Base64 encode
      
      // Auto-fill project info if available
      setFormData(prev => ({
        ...prev,
        calendar_name: prev.calendar_name || `Calendar ${json.project_id}`,
      }))

    } catch (err) {
      alert('Eroare la încărcarea fișierului JSON: ' + (err instanceof Error ? err.message : 'Format invalid'))
    }
  }

  const handleSetup = async () => {
    if (!credentialsJson) {
      alert('Vă rog încărcați fișierul de credentiale JSON')
      return
    }

    if (!formData.calendar_name || !formData.google_calendar_id) {
      alert('Vă rog completați toate câmpurile obligatorii')
      return
    }

    try {
      await setupCalendar({
        calendar_name: formData.calendar_name,
        google_calendar_id: formData.google_calendar_id,
        google_calendar_credentials_json: credentialsJson,
        timezone: formData.timezone,
        auto_create_events: formData.auto_create_events
      })

      setStep('success')
    } catch (err) {
      console.error('Setup failed:', err)
    }
  }

  const handleTest = async () => {
    try {
      const result = await testCalendar()
      setTestResult(result)
    } catch (err) {
      setTestResult({ success: false, message: 'Test eșuat' })
    }
  }

  const handleEnable = async () => {
    try {
      await enableCalendar()
      onSuccess?.()
    } catch (err) {
      console.error('Enable failed:', err)
    }
  }

  const handleDisable = async () => {
    try {
      await disableCalendar()
      onSuccess?.()
    } catch (err) {
      console.error('Disable failed:', err)
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black/60 z-[60] flex items-center justify-center p-4">
      <div className="bg-card rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-border">
          <div className="flex items-center gap-3">
            <Settings className="w-6 h-6 text-secondary" />
            <h2 className="text-xl font-bold text-primary">
              {step === 'manage' ? 'Gestionare Calendar' : 'Configurare Google Calendar'}
            </h2>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-card-hover rounded-lg transition-colors"
          >
            <X className="w-5 h-5 text-secondary" />
          </button>
        </div>

        <div className="p-6 overflow-y-auto max-h-[calc(90vh-120px)]">
          {/* Management View for Existing Calendar */}
          {step === 'manage' && existingCalendar && (
            <div className="space-y-6">
              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <div className="flex items-center gap-2 mb-2">
                  <CheckCircle className="w-5 h-5 text-green-600" />
                  <h3 className="font-semibold text-green-800">Calendar Configurat</h3>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
                  <div>
                    <span className="text-green-600">Nume:</span>
                    <p className="font-medium text-green-800">{existingCalendar.calendar_name}</p>
                  </div>
                  <div>
                    <span className="text-green-600">Status:</span>
                    <p className="font-medium text-green-800">
                      {existingCalendar.enabled ? 'Activ' : 'Inactiv'}
                    </p>
                  </div>
                  <div>
                    <span className="text-green-600">ID Calendar:</span>
                    <p className="font-medium text-green-800 truncate">{existingCalendar.calendar_id}</p>
                  </div>
                  <div>
                    <span className="text-green-600">Fus orar:</span>
                    <p className="font-medium text-green-800">{existingCalendar.timezone}</p>
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                <button
                  onClick={handleTest}
                  disabled={loading}
                  className="flex items-center justify-center gap-2 px-4 py-3 bg-blue-50 text-blue-700 rounded-lg border border-blue-200 hover:bg-blue-100 transition-colors disabled:opacity-50"
                >
                  {loading ? <Loader className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
                  <span>Test Conexiune</span>
                </button>

                {existingCalendar.enabled ? (
                  <button
                    onClick={handleDisable}
                    disabled={loading}
                    className="flex items-center justify-center gap-2 px-4 py-3 bg-orange-50 text-orange-700 rounded-lg border border-orange-200 hover:bg-orange-100 transition-colors disabled:opacity-50"
                  >
                    {loading ? <Loader className="w-4 h-4 animate-spin" /> : <PowerOff className="w-4 h-4" />}
                    <span>Dezactivează</span>
                  </button>
                ) : (
                  <button
                    onClick={handleEnable}
                    disabled={loading}
                    className="flex items-center justify-center gap-2 px-4 py-3 bg-green-50 text-green-700 rounded-lg border border-green-200 hover:bg-green-100 transition-colors disabled:opacity-50"
                  >
                    {loading ? <Loader className="w-4 h-4 animate-spin" /> : <Power className="w-4 h-4" />}
                    <span>Activează</span>
                  </button>
                )}

                <button
                  onClick={() => setStep('setup')}
                  className="flex items-center justify-center gap-2 px-4 py-3 bg-gray-50 text-gray-700 rounded-lg border border-gray-200 hover:bg-gray-100 transition-colors"
                >
                  <RotateCcw className="w-4 h-4" />
                  <span>Reconfigurează</span>
                </button>
              </div>

              {/* Test Results */}
              {testResult && (
                <div className={`rounded-lg p-4 ${
                  testResult.success 
                    ? 'bg-green-50 border border-green-200' 
                    : 'bg-red-50 border border-red-200'
                }`}>
                  <div className="flex items-center gap-2 mb-2">
                    {testResult.success ? (
                      <CheckCircle className="w-5 h-5 text-green-600" />
                    ) : (
                      <AlertCircle className="w-5 h-5 text-red-600" />
                    )}
                    <h3 className={`font-semibold ${
                      testResult.success ? 'text-green-800' : 'text-red-800'
                    }`}>
                      Rezultat Test
                    </h3>
                  </div>
                  <p className={`text-sm ${
                    testResult.success ? 'text-green-700' : 'text-red-700'
                  }`}>
                    {testResult.message}
                  </p>
                  {testResult.test_results && (
                    <div className="mt-2 text-xs text-green-600">
                      <p>✓ Event de test creat și șters cu succes</p>
                      <p>✓ Calendar ID: {testResult.test_results.calendar_id}</p>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}

          {/* Setup Form */}
          {step === 'setup' && (
            <div className="space-y-6">
              {/* Setup Guide Button */}
              <div className="flex justify-between items-center">
                <h3 className="text-lg font-semibold text-primary">Configurare Nouă</h3>
                <button
                  onClick={() => setShowGuide(!showGuide)}
                  className="flex items-center gap-2 px-3 py-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                >
                  <ExternalLink className="w-4 h-4" />
                  <span>Ghid de configurare</span>
                </button>
              </div>

              {showGuide && (
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 text-sm space-y-3">
                  <h4 className="font-semibold text-blue-800">Pași pentru configurare:</h4>
                  <ol className="list-decimal list-inside space-y-2 text-blue-700">
                    <li>Creează un proiect în Google Cloud Console</li>
                    <li>Activează Google Calendar API</li>
                    <li>Creează un Service Account</li>
                    <li>Generează și descarcă cheia JSON</li>
                    <li>Partajează calendarul cu email-ul service account-ului</li>
                    <li>Acordă permisiunea "Make changes to events"</li>
                  </ol>
                </div>
              )}

              {/* JSON Upload */}
              <div>
                <label className="block text-sm font-medium text-primary mb-2">
                  Fișier credentiale JSON *
                </label>
                <div className="border-2 border-dashed border-border rounded-lg p-6">
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept=".json"
                    onChange={handleFileUpload}
                    className="hidden"
                  />
                  <div className="text-center">
                    {credentialsFile ? (
                      <div className="flex items-center justify-center gap-2 text-green-600">
                        <CheckCircle className="w-5 h-5" />
                        <span>{credentialsFile.name}</span>
                      </div>
                    ) : (
                      <button
                        onClick={() => fileInputRef.current?.click()}
                        className="flex items-center justify-center gap-2 mx-auto px-4 py-2 bg-card-hover text-secondary hover:text-primary rounded-lg transition-colors"
                      >
                        <Upload className="w-5 h-5" />
                        <span>Încarcă fișierul JSON</span>
                      </button>
                    )}
                  </div>
                </div>
              </div>

              {/* Form Fields */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-primary mb-2">
                    Nume Calendar *
                  </label>
                  <input
                    type="text"
                    value={formData.calendar_name}
                    onChange={(e) => setFormData(prev => ({ ...prev, calendar_name: e.target.value }))}
                    className="w-full px-3 py-2 border border-border rounded-lg bg-background text-primary"
                    placeholder="Ex: Salon Booking Calendar"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-primary mb-2">
                    Calendar ID *
                  </label>
                  <input
                    type="text"
                    value={formData.google_calendar_id}
                    onChange={(e) => setFormData(prev => ({ ...prev, google_calendar_id: e.target.value }))}
                    className="w-full px-3 py-2 border border-border rounded-lg bg-background text-primary"
                    placeholder="calendar@gmail.com"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-primary mb-2">
                    Fus orar
                  </label>
                  <select
                    value={formData.timezone}
                    onChange={(e) => setFormData(prev => ({ ...prev, timezone: e.target.value }))}
                    className="w-full px-3 py-2 border border-border rounded-lg bg-background text-primary"
                  >
                    <option value="Europe/Bucharest">Europe/Bucharest</option>
                    <option value="Europe/London">Europe/London</option>
                    <option value="US/Eastern">US/Eastern</option>
                    <option value="US/Pacific">US/Pacific</option>
                  </select>
                </div>

                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    id="auto_create"
                    checked={formData.auto_create_events}
                    onChange={(e) => setFormData(prev => ({ ...prev, auto_create_events: e.target.checked }))}
                    className="rounded"
                  />
                  <label htmlFor="auto_create" className="text-sm text-primary">
                    Crează evenimente automat
                  </label>
                </div>
              </div>

              {error && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-3">
                  <div className="flex items-center gap-2">
                    <AlertCircle className="w-4 h-4 text-red-600" />
                    <span className="text-red-800 text-sm">{error}</span>
                  </div>
                </div>
              )}

              {/* Setup Button */}
              <button
                onClick={handleSetup}
                disabled={loading || !credentialsFile}
                className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
              >
                {loading ? <Loader className="w-4 h-4 animate-spin" /> : <Settings className="w-4 h-4" />}
                <span>{loading ? 'Se configurează...' : 'Configurează Calendar'}</span>
              </button>
            </div>
          )}

          {/* Success Step */}
          {step === 'success' && (
            <div className="text-center space-y-6">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto">
                <CheckCircle className="w-8 h-8 text-green-600" />
              </div>
              <div>
                <h3 className="text-xl font-semibold text-primary mb-2">
                  Calendar Configurat cu Succes!
                </h3>
                <p className="text-secondary">
                  Google Calendar a fost integrat și sincronizat cu sistemul de programări.
                </p>
              </div>
              <button
                onClick={() => {
                  onSuccess?.()
                  onClose()
                }}
                className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
              >
                Finalizează
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}