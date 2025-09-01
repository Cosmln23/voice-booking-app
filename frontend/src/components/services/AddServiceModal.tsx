'use client'

import { clsx } from "clsx"

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
  category: 'Tuns' | 'Barbă' | 'Tratamente' | 'Pachete'
  description: string
  serviceDuration: number
  bufferTime: number
  price: string
  status: 'Activ' | 'Inactiv'
  isPackage: boolean
  packageItems: string[]
}

interface ServiceFormErrors {
  name?: string
  category?: string
  description?: string
  serviceDuration?: string
  bufferTime?: string
  price?: string
  status?: string
  isPackage?: string
  packageItems?: string
}

interface AddServiceModalProps {
  onClose: () => void
  onSave: (serviceData: ServiceFormData) => void
}

export default function AddServiceModal({ onClose, onSave }: AddServiceModalProps) {
  const [formData, setFormData] = useState<ServiceFormData>({
    name: '',
    category: 'Tuns',
    description: '',
    serviceDuration: 30,
    bufferTime: 5,
    price: '',
    status: 'Activ',
    isPackage: false,
    packageItems: []
  })
  
  const [errors, setErrors] = useState<ServiceFormErrors>({})
  const [newPackageItem, setNewPackageItem] = useState('')

  const availableServices = [
    'Tunsoare Clasică',
    'Tunsoare + Styling', 
    'Aranjare Barbă',
    'Barbă Completă',
    'Tratament Păr Anti-Mătreață',
    'Masaj Scalp Relaxant'
  ]

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

    if (formData.bufferTime < 0) {
      newErrors.bufferTime = 'Timpul tampon nu poate fi negativ'
    }

    if (formData.isPackage && formData.packageItems.length === 0) {
      newErrors.packageItems = 'Un pachet trebuie să conțină cel puțin un serviciu'
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

  const addPackageItem = () => {
    if (newPackageItem.trim() && !formData.packageItems.includes(newPackageItem.trim())) {
      updateFormData('packageItems', [...formData.packageItems, newPackageItem.trim()])
      setNewPackageItem('')
    }
  }

  const removePackageItem = (index: number) => {
    const newItems = formData.packageItems.filter((_, i) => i !== index)
    updateFormData('packageItems', newItems)
  }

  const getTotalDuration = () => {
    return formData.serviceDuration + formData.bufferTime
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
                    <option value="Tuns">Tuns</option>
                    <option value="Barbă">Barbă</option>
                    <option value="Tratamente">Tratamente</option>
                    <option value="Pachete">Pachete</option>
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
                    <option value="Activ">Activ</option>
                    <option value="Inactiv">Inactiv</option>
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

                {/* Buffer Time */}
                <div>
                  <label className="block text-sm font-medium text-primary mb-2">
                    Timp Tampon (minute)
                  </label>
                  <input
                    type="number"
                    min="0"
                    step="5"
                    value={formData.bufferTime}
                    onChange={(e) => updateFormData('bufferTime', parseInt(e.target.value) || 0)}
                    className={clsx(
                      'w-full px-4 py-2 bg-background border rounded-2xl text-primary focus:outline-none focus:border-secondary transition-colors',
                      errors.bufferTime ? 'border-red-500' : 'border-border'
                    )}
                  />
                  <p className="mt-1 text-xs text-secondary">Pentru curățenie/pregătire</p>
                  {errors.bufferTime && (
                    <p className="mt-1 text-sm text-secondary flex items-center gap-1">
                      <AlertCircle className="w-3 h-3" />
                      {errors.bufferTime}
                    </p>
                  )}
                </div>

                {/* Total Duration Display */}
                <div className="lg:col-span-2">
                  <div className="p-3 bg-secondary/10 rounded-2xl border border-secondary/20">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-secondary">Durată Totală în Agendă:</span>
                      <span className="font-semibold text-primary text-lg">
                        {formatDuration(getTotalDuration())}
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

            {/* Package Configuration */}
            <div className="bg-background rounded-2xl p-4 border border-border">
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-semibold text-primary flex items-center gap-2">
                  <Package className="w-4 h-4" />
                  Configurație Pachet
                </h3>
                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    id="isPackage"
                    checked={formData.isPackage}
                    onChange={(e) => updateFormData('isPackage', e.target.checked)}
                    className="rounded"
                  />
                  <label htmlFor="isPackage" className="text-sm text-secondary cursor-pointer">
                    Este pachet de servicii
                  </label>
                </div>
              </div>

              {formData.isPackage && (
                <div className="space-y-4">
                  <div className="p-3 bg-secondary/10 rounded-2xl">
                    <p className="text-sm text-secondary">
                      <strong className="text-primary">Pachet:</strong> Combină mai multe servicii individuale cu un preț și o durată totală optimizate.
                    </p>
                  </div>

                  {/* Add Package Item */}
                  <div>
                    <label className="block text-sm font-medium text-primary mb-2">
                      Adaugă Servicii în Pachet
                    </label>
                    <div className="flex gap-2">
                      <select
                        value={newPackageItem}
                        onChange={(e) => setNewPackageItem(e.target.value)}
                        className="flex-1 px-4 py-2 bg-background border border-border rounded-2xl text-primary focus:outline-none focus:border-secondary transition-colors"
                      >
                        <option value="">Selectează un serviciu...</option>
                        {availableServices
                          .filter(service => !formData.packageItems.includes(service))
                          .map((service, index) => (
                            <option key={index} value={service}>
                              {service}
                            </option>
                          ))
                        }
                      </select>
                      <button
                        type="button"
                        onClick={addPackageItem}
                        disabled={!newPackageItem.trim()}
                        className="px-4 py-2 bg-background text-secondary border border-border rounded-2xl hover:text-primary hover:border-secondary transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        <Plus className="w-4 h-4" />
                      </button>
                    </div>
                  </div>

                  {/* Package Items List */}
                  {formData.packageItems.length > 0 && (
                    <div>
                      <label className="block text-sm font-medium text-primary mb-2">
                        Servicii în Pachet:
                      </label>
                      <div className="space-y-2">
                        {formData.packageItems.map((item, index) => (
                          <div key={index} className="flex items-center justify-between p-3 bg-card rounded-2xl">
                            <span className="text-primary">{item}</span>
                            <button
                              type="button"
                              onClick={() => removePackageItem(index)}
                              className="p-1 text-secondary hover:text-primary transition-colors"
                            >
                              <Trash2 className="w-4 h-4" />
                            </button>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {errors.packageItems && (
                    <p className="text-sm text-secondary flex items-center gap-1">
                      <AlertCircle className="w-3 h-3" />
                      {errors.packageItems}
                    </p>
                  )}
                </div>
              )}
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