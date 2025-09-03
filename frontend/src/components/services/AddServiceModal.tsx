'use client'

import clsx from "clsx"

import { useState } from 'react'
import {
  X,
  Scissors,
  Clock,
  DollarSign,
  FileText,
  Save,
  AlertCircle,
  Package,
  Plus,
  Trash2
} from 'lucide-react'


interface ServiceFormData {
  name: string
  category: 'individual' | 'package'
  description: string
  serviceDuration: number  // Pentru UI, dar se convertește la duration
  price: string
  status: 'active' | 'inactive'
}

interface ServiceFormErrors {
  name?: string
  category?: string
  description?: string
  serviceDuration?: string
  price?: string
  status?: string
}

interface AddServiceModalProps {
  onClose: () => void
  onSave: (serviceData: ServiceFormData) => void
  initialData?: Partial<ServiceFormData>
}

export default function AddServiceModal({ onClose, onSave, initialData }: AddServiceModalProps) {
  const [formData, setFormData] = useState<ServiceFormData>({
    name: initialData?.name || '',
    category: initialData?.category || 'individual',
    description: initialData?.description || '',
    serviceDuration: initialData?.serviceDuration || 30,
    price: initialData?.price || '',
    status: initialData?.status || 'active'
  })
  
  const [errors, setErrors] = useState<ServiceFormErrors>({})

  const validateForm = () => {
    const newErrors: ServiceFormErrors = {}
    
    if (!formData.name.trim()) {
      newErrors.name = 'Numele serviciului este obligatoriu'
    }
    
    if (!formData.description.trim()) {
      newErrors.description = 'Descrierea este obligatorie'
    }
    
    if (!formData.price.trim()) {
      newErrors.price = 'Prețul este obligatoriu'
    } else if (!/^\d+(\.\d{1,2})?\s*(RON|ron|Lei|lei)?$/i.test(formData.price.trim())) {
      newErrors.price = 'Format preț invalid (ex: 50 RON)'
    }

    if (formData.serviceDuration < 5) {
      newErrors.serviceDuration = 'Durata minimă este 5 minute'
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

  const updateFormData = (field: keyof ServiceFormData, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }))
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: undefined }))
    }
  }

  const formatDuration = (minutes: number) => {
    if (minutes >= 60) {
      const hours = Math.floor(minutes / 60)
      const mins = minutes % 60
      return mins > 0 ? `${hours}h ${mins}min` : `${hours}h`
    }
    return `${minutes}min`
  }

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-card rounded-2xl border border-border w-full max-w-3xl max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="p-6 border-b border-border">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-secondary/20 flex items-center justify-center">
                <Scissors className="w-5 h-5 text-secondary" />
              </div>
              <div>
                <h2 className="text-xl font-bold text-primary">Adaugă Serviciu Nou</h2>
                <p className="text-sm text-secondary">Configurează un serviciu pentru catalog</p>
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
          <div className="space-y-6">
            {/* Basic Info */}
            <div className="bg-background rounded-2xl p-4 border border-border">
              <h3 className="font-semibold text-primary mb-4 flex items-center gap-2">
                <FileText className="w-4 h-4" />
                Informații de Bază
              </h3>
              
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                {/* Name */}
                <div className="lg:col-span-2">
                  <label className="block text-sm font-medium text-primary mb-2">
                    Nume Serviciu *
                  </label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => updateFormData('name', e.target.value)}
                    className={clsx(
                      'w-full px-4 py-2 bg-background border rounded-2xl text-primary placeholder-secondary focus:outline-none focus:border-secondary transition-colors',
                      errors.name ? 'border-red-500' : 'border-border'
                    )}
                    placeholder="ex: Tunsoare Clasică Bărbați"
                  />
                  {errors.name && (
                    <p className="mt-1 text-sm text-secondary flex items-center gap-1">
                      <AlertCircle className="w-3 h-3" />
                      {errors.name}
                    </p>
                  )}
                </div>

                {/* Category */}
                <div>
                  <label className="block text-sm font-medium text-primary mb-2">
                    Categorie *
                  </label>
                  <select
                    value={formData.category}
                    onChange={(e) => updateFormData('category', e.target.value)}
                    className="w-full px-4 py-2 bg-background border border-border rounded-2xl text-primary focus:outline-none focus:border-secondary transition-colors"
                  >
                    <option value="individual">Individual</option>
                    <option value="package">Pachet</option>
                  </select>
                </div>

                {/* Status */}
                <div>
                  <label className="block text-sm font-medium text-primary mb-2">
                    Status
                  </label>
                  <select
                    value={formData.status}
                    onChange={(e) => updateFormData('status', e.target.value)}
                    className="w-full px-4 py-2 bg-background border border-border rounded-2xl text-primary focus:outline-none focus:border-secondary transition-colors"
                  >
                    <option value="active">Activ</option>
                    <option value="inactive">Inactiv</option>
                  </select>
                </div>

                {/* Description */}
                <div className="lg:col-span-2">
                  <label className="block text-sm font-medium text-primary mb-2">
                    Descriere Serviciu *
                  </label>
                  <textarea
                    value={formData.description}
                    onChange={(e) => updateFormData('description', e.target.value)}
                    rows={3}
                    className={clsx(
                      'w-full px-4 py-2 bg-background border rounded-2xl text-primary placeholder-secondary focus:outline-none focus:border-secondary transition-colors resize-none',
                      errors.description ? 'border-red-500' : 'border-border'
                    )}
                    placeholder="Descrie serviciul, tehnicile folosite, beneficiile pentru client..."
                  />
                  {errors.description && (
                    <p className="mt-1 text-sm text-secondary flex items-center gap-1">
                      <AlertCircle className="w-3 h-3" />
                      {errors.description}
                    </p>
                  )}
                </div>
              </div>
            </div>

            {/* Duration & Pricing */}
            <div className="bg-background rounded-2xl p-4 border border-border">
              <h3 className="font-semibold text-primary mb-4 flex items-center gap-2">
                <Clock className="w-4 h-4" />
                Durată și Preț
              </h3>
              
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                {/* Service Duration */}
                <div>
                  <label className="block text-sm font-medium text-primary mb-2">
                    Durată Serviciu (minute) *
                  </label>
                  <input
                    type="number"
                    min="5"
                    step="5"
                    value={formData.serviceDuration}
                    onChange={(e) => updateFormData('serviceDuration', parseInt(e.target.value) || 0)}
                    className={clsx(
                      'w-full px-4 py-2 bg-background border rounded-2xl text-primary focus:outline-none focus:border-secondary transition-colors',
                      errors.serviceDuration ? 'border-red-500' : 'border-border'
                    )}
                  />
                  <p className="mt-1 text-xs text-secondary">Timpul efectiv de lucru</p>
                  {errors.serviceDuration && (
                    <p className="mt-1 text-sm text-secondary flex items-center gap-1">
                      <AlertCircle className="w-3 h-3" />
                      {errors.serviceDuration}
                    </p>
                  )}
                </div>

                {/* Duration Display */}
                <div>
                  <div className="p-3 bg-secondary/10 rounded-2xl border border-secondary/20">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-secondary">Durată Serviciu:</span>
                      <span className="font-semibold text-primary text-lg">
                        {formatDuration(formData.serviceDuration)}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Price */}
                <div className="lg:col-span-2">
                  <label className="block text-sm font-medium text-primary mb-2">
                    Preț Serviciu (RON) *
                  </label>
                  <input
                    type="text"
                    value={formData.price}
                    onChange={(e) => updateFormData('price', e.target.value)}
                    className={clsx(
                      'w-full px-4 py-2 bg-background border rounded-2xl text-primary placeholder-secondary focus:outline-none focus:border-secondary transition-colors',
                      errors.price ? 'border-red-500' : 'border-border'
                    )}
                    placeholder="ex: 50 RON"
                  />
                  {errors.price && (
                    <p className="mt-1 text-sm text-secondary flex items-center gap-1">
                      <AlertCircle className="w-3 h-3" />
                      {errors.price}
                    </p>
                  )}
                </div>
              </div>
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
              Salvează Serviciu
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}