'use client'

import clsx from "clsx"

import { useState } from 'react'
import {
  X,
  User,
  Phone,
  Mail,
  MapPin,
  Calendar,
  FileText,
  Shield,
  Save,
  AlertCircle
} from 'lucide-react'


interface ClientFormData {
  name: string
  phone: string
  email: string
  status: 'VIP' | 'Standard' | 'New' | 'Inactive'
  notes?: string
  preferences?: string
}

interface AddClientModalProps {
  onClose: () => void
  onSave: (clientData: ClientFormData) => void
}

export default function AddClientModal({ onClose, onSave }: AddClientModalProps) {
  const [formData, setFormData] = useState<ClientFormData>({
    name: '',
    phone: '',
    email: '',
    status: 'New',
    notes: '',
    preferences: ''
  })
  
  const [errors, setErrors] = useState<Partial<ClientFormData>>({})

  const validateForm = () => {
    const newErrors: Partial<ClientFormData> = {}
    
    if (!formData.name.trim()) {
      newErrors.name = 'Numele este obligatoriu'
    }
    
    if (!formData.phone.trim()) {
      newErrors.phone = 'Telefonul este obligatoriu'
    } else if (!/^(\+40|0)[0-9]{9}$/.test(formData.phone.replace(/\s/g, ''))) {
      newErrors.phone = 'Format telefon invalid'
    }
    
    if (!formData.email.trim()) {
      newErrors.email = 'Email-ul este obligatoriu'
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Format email invalid'
    }

    
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (validateForm()) {
      onSave(formData)
    }
  }

  const updateFormData = (field: keyof ClientFormData, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }))
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: undefined }))
    }
  }

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-card rounded-2xl border border-border w-full max-w-2xl max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="p-6 border-b border-border">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-secondary/20 flex items-center justify-center">
                <User className="w-5 h-5 text-secondary" />
              </div>
              <div>
                <h2 className="text-xl font-bold text-primary">Adaugă Client Nou</h2>
                <p className="text-sm text-secondary">Completează informațiile despre client</p>
              </div>
            </div>
            <button 
              onClick={onClose}
              className="p-2 text-secondary hover:text-primary rounded-2xl hover:bg-card-hover transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>


        {/* Form Content */}
        <form onSubmit={handleSubmit} className="flex-1 overflow-y-auto p-6">
          <div className="space-y-4">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                {/* Name */}
                <div className="lg:col-span-2">
                  <label className="block text-sm font-medium text-primary mb-2">
                    Nume Complet *
                  </label>
                  <div className="relative">
                    <User className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-secondary" />
                    <input
                      type="text"
                      value={formData.name}
                      onChange={(e) => updateFormData('name', e.target.value)}
                      className={clsx(
                        'w-full pl-10 pr-4 py-2 bg-background border rounded-2xl text-primary placeholder-secondary focus:outline-none focus:border-secondary transition-colors',
                        errors.name ? 'border-red-500' : 'border-border'
                      )}
                      placeholder="ex: Maria Ionescu"
                    />
                  </div>
                  {errors.name && (
                    <p className="mt-1 text-sm text-secondary flex items-center gap-1">
                      <AlertCircle className="w-3 h-3" />
                      {errors.name}
                    </p>
                  )}
                </div>

                {/* Phone */}
                <div>
                  <label className="block text-sm font-medium text-primary mb-2">
                    Telefon *
                  </label>
                  <div className="relative">
                    <Phone className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-secondary" />
                    <input
                      type="tel"
                      value={formData.phone}
                      onChange={(e) => updateFormData('phone', e.target.value)}
                      className={clsx(
                        'w-full pl-10 pr-4 py-2 bg-background border rounded-2xl text-primary placeholder-secondary focus:outline-none focus:border-secondary transition-colors',
                        errors.phone ? 'border-red-500' : 'border-border'
                      )}
                      placeholder="+40 721 123 456"
                    />
                  </div>
                  {errors.phone && (
                    <p className="mt-1 text-sm text-secondary flex items-center gap-1">
                      <AlertCircle className="w-3 h-3" />
                      {errors.phone}
                    </p>
                  )}
                </div>

                {/* Email */}
                <div>
                  <label className="block text-sm font-medium text-primary mb-2">
                    Email *
                  </label>
                  <div className="relative">
                    <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-secondary" />
                    <input
                      type="email"
                      value={formData.email}
                      onChange={(e) => updateFormData('email', e.target.value)}
                      className={clsx(
                        'w-full pl-10 pr-4 py-2 bg-background border rounded-2xl text-primary placeholder-secondary focus:outline-none focus:border-secondary transition-colors',
                        errors.email ? 'border-red-500' : 'border-border'
                      )}
                      placeholder="maria@example.com"
                    />
                  </div>
                  {errors.email && (
                    <p className="mt-1 text-sm text-secondary flex items-center gap-1">
                      <AlertCircle className="w-3 h-3" />
                      {errors.email}
                    </p>
                  )}
                </div>


                {/* Status */}
                <div>
                  <label className="block text-sm font-medium text-primary mb-2">
                    Status Client
                  </label>
                  <select
                    value={formData.status}
                    onChange={(e) => updateFormData('status', e.target.value)}
                    className="w-full px-4 py-2 bg-background border border-border rounded-2xl text-primary focus:outline-none focus:border-secondary transition-colors"
                  >
                    <option value="New">Nou</option>
                    <option value="Standard">Standard</option>
                    <option value="VIP">VIP</option>
                    <option value="Inactive">Inactiv</option>
                  </select>
                </div>
              </div>
              {/* Preferences */}
              <div>
                <label className="block text-sm font-medium text-primary mb-2">
                  Preferințe Servicii
                </label>
                <textarea
                  value={formData.preferences}
                  onChange={(e) => updateFormData('preferences', e.target.value)}
                  rows={3}
                  className="w-full px-4 py-2 bg-background border border-border rounded-2xl text-primary placeholder-secondary focus:outline-none focus:border-secondary transition-colors resize-none"
                  placeholder="ex: Preferă tunsoarea bob, îi place balayage-ul natural..."
                />
              </div>

              {/* Notes */}
              <div>
                <label className="block text-sm font-medium text-primary mb-2">
                  Note Generale
                </label>
                <textarea
                  value={formData.notes}
                  onChange={(e) => updateFormData('notes', e.target.value)}
                  rows={4}
                  className="w-full px-4 py-2 bg-background border border-border rounded-2xl text-primary placeholder-secondary focus:outline-none focus:border-secondary transition-colors resize-none"
                  placeholder="ex: Vine întotdeauna cu mama, foarte punctuală, îi place să discute despre călătorii..."
                />
              </div>
            </div>

          {/* Footer Actions */}
          <div className="mt-8 pt-4 border-t border-border flex justify-end gap-3">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-secondary border border-border rounded-2xl hover:text-primary hover:border-secondary transition-colors"
            >
              Anulează
            </button>
            <button
              type="submit"
              className="flex items-center gap-2 px-4 py-2 bg-background text-primary border border-border rounded-2xl hover:bg-card-hover transition-colors"
            >
              <Save className="w-4 h-4" />
              Salvează Client
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}