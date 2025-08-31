'use client'

import { useState } from 'react'
import {
  X,
  Scissors,
  Clock,
  DollarSign,
  FileText,
  Package,
  Zap,
  Heart,
  Edit,
  Trash2,
  Copy,
  ToggleLeft,
  ToggleRight,
  AlertCircle
} from 'lucide-react'
import { cn } from '@/lib/utils'

interface Service {
  id: string
  name: string
  category: 'Tuns' | 'Barbă' | 'Tratamente' | 'Pachete'
  description?: string
  serviceDuration: number
  bufferTime: number
  totalDuration: number
  price: string
  status: 'Activ' | 'Inactiv'
  isPackage?: boolean
  packageItems?: string[]
}

interface ServiceProfileProps {
  service: Service
  onClose: () => void
}

export default function ServiceProfile({ service, onClose }: ServiceProfileProps) {
  const [activeTab, setActiveTab] = useState<'overview' | 'details' | 'settings'>('overview')

  const getCategoryIcon = (category: Service['category']) => {
    switch (category) {
      case 'Tuns':
        return <Scissors className="w-5 h-5" />
      case 'Barbă':
        return <Zap className="w-5 h-5" />
      case 'Tratamente':
        return <Heart className="w-5 h-5" />
      case 'Pachete':
        return <Package className="w-5 h-5" />
      default:
        return <Scissors className="w-5 h-5" />
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

  const getCategoryColor = (category: Service['category']) => {
    // All colors are now grey/white as per design requirements
    return 'text-secondary bg-secondary/20'
  }

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-card rounded-2xl border border-border w-full max-w-4xl max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="p-6 border-b border-border">
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-4">
              <div className={cn(
                "w-16 h-16 rounded-full flex items-center justify-center",
                getCategoryColor(service.category)
              )}>
                {getCategoryIcon(service.category)}
              </div>
              <div>
                <div className="flex items-center gap-3 mb-2">
                  <h2 className="text-2xl font-bold text-primary">{service.name}</h2>
                  {service.isPackage && (
                    <span className="inline-flex items-center px-2 py-1 rounded-2xl text-sm bg-secondary/20 text-secondary border border-border">
                      <Package className="w-4 h-4 mr-1" />
                      Pachet
                    </span>
                  )}
                </div>
                <div className="flex items-center gap-4 text-sm text-secondary">
                  <span className="flex items-center gap-1">
                    {getCategoryIcon(service.category)}
                    {service.category}
                  </span>
                  <span className="flex items-center gap-1">
                    <Clock className="w-4 h-4" />
                    {formatDuration(service.totalDuration)}
                  </span>
                  <span className="flex items-center gap-1">
                    <DollarSign className="w-4 h-4" />
                    {service.price}
                  </span>
                  <span className={cn(
                    "inline-flex items-center px-2 py-1 rounded-2xl text-xs border",
                    service.status === 'Activ' 
                      ? 'bg-secondary/20 text-primary border-border'
                      : 'bg-secondary/20 text-secondary border-border'
                  )}>
                    {service.status}
                  </span>
                </div>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <button className="p-2 text-secondary hover:text-primary rounded-2xl hover:bg-card-hover transition-colors">
                <Copy className="w-5 h-5" />
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
              { key: 'overview', label: 'Prezentare Generală', icon: FileText },
              { key: 'details', label: 'Detalii Serviciu', icon: Clock },
              { key: 'settings', label: 'Setări', icon: Edit }
            ].map((tab) => (
              <button
                key={tab.key}
                onClick={() => setActiveTab(tab.key as any)}
                className={cn(
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
              {/* Service Description */}
              <div className="bg-background rounded-2xl p-4 border border-border">
                <h3 className="font-semibold text-primary mb-3 flex items-center gap-2">
                  <FileText className="w-4 h-4" />
                  Descriere Serviciu
                </h3>
                <p className="text-primary leading-relaxed">
                  {service.description || 'Nu există descriere disponibilă pentru acest serviciu.'}
                </p>
              </div>

              {/* Quick Stats */}
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
                <div className="bg-background rounded-2xl p-4 border border-border text-center">
                  <Clock className="w-8 h-8 text-secondary mx-auto mb-2" />
                  <div className="text-2xl font-bold text-primary">{formatDuration(service.totalDuration)}</div>
                  <div className="text-sm text-secondary">Durată Totală</div>
                </div>
                
                <div className="bg-background rounded-2xl p-4 border border-border text-center">
                  <div className="text-2xl font-bold text-primary">{service.price.replace(' RON', '').replace('RON', '')} RON</div>
                  <div className="text-sm text-secondary">Preț Serviciu</div>
                </div>

                <div className="bg-background rounded-2xl p-4 border border-border text-center">
                  {getCategoryIcon(service.category)}
                  <div className="text-2xl font-bold text-primary">{service.category}</div>
                  <div className="text-sm text-secondary">Categorie</div>
                </div>
              </div>

              {/* Package Details */}
              {service.isPackage && service.packageItems && (
                <div className="bg-background rounded-2xl p-4 border border-border">
                  <h3 className="font-semibold text-primary mb-3 flex items-center gap-2">
                    <Package className="w-4 h-4" />
                    Componente Pachet
                  </h3>
                  <div className="space-y-2">
                    {service.packageItems.map((item, index) => (
                      <div key={index} className="flex items-center gap-3 p-3 bg-card rounded-2xl">
                        <div className="w-2 h-2 bg-secondary rounded-full"></div>
                        <span className="text-primary">{item}</span>
                      </div>
                    ))}
                  </div>
                  <div className="mt-4 p-3 bg-secondary/10 rounded-2xl">
                    <p className="text-sm text-secondary">
                      <strong className="text-primary">Avantaj:</strong> Acest pachet oferă o economie față de rezervarea serviciilor individuale.
                    </p>
                  </div>
                </div>
              )}
            </div>
          )}

          {activeTab === 'details' && (
            <div className="space-y-6">
              {/* Duration Breakdown */}
              <div className="bg-background rounded-2xl p-4 border border-border">
                <h3 className="font-semibold text-primary mb-4 flex items-center gap-2">
                  <Clock className="w-4 h-4" />
                  Detalii Durată
                </h3>
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
                  <div className="text-center p-4 bg-card rounded-2xl">
                    <div className="text-xl font-bold text-primary">{formatDuration(service.serviceDuration)}</div>
                    <div className="text-sm text-secondary">Timp Efectiv Serviciu</div>
                    <div className="text-xs text-secondary mt-1">Timpul de lucru real</div>
                  </div>
                  <div className="text-center p-4 bg-card rounded-2xl">
                    <div className="text-xl font-bold text-primary">{formatDuration(service.bufferTime)}</div>
                    <div className="text-sm text-secondary">Timp Tampon</div>
                    <div className="text-xs text-secondary mt-1">Pentru curățenie/pregătire</div>
                  </div>
                  <div className="text-center p-4 bg-secondary/10 rounded-2xl border border-secondary/20">
                    <div className="text-xl font-bold text-primary">{formatDuration(service.totalDuration)}</div>
                    <div className="text-sm text-primary font-medium">Durată Totală</div>
                    <div className="text-xs text-secondary mt-1">Timpul rezervat în agendă</div>
                  </div>
                </div>
                <div className="mt-4 p-3 bg-secondary/10 rounded-2xl">
                  <div className="flex items-start gap-2">
                    <AlertCircle className="w-4 h-4 text-secondary mt-0.5" />
                    <div className="text-sm text-secondary">
                      <strong className="text-primary">Informație:</strong> Timpul tampon este adăugat automat după fiecare serviciu pentru a permite curățenia echipamentelor și pregătirea pentru următorul client.
                    </div>
                  </div>
                </div>
              </div>

              {/* Pricing Details */}
              <div className="bg-background rounded-2xl p-4 border border-border">
                <h3 className="font-semibold text-primary mb-4 flex items-center gap-2">
                  <span className="text-xs text-secondary">RON</span>
                  Detalii Preț
                </h3>
                <div className="space-y-4">
                  <div className="flex justify-between items-center p-3 bg-card rounded-2xl">
                    <span className="text-primary">Preț Serviciu:</span>
                    <span className="font-semibold text-primary">{service.price.replace(' RON', '').replace('RON', '')} RON</span>
                  </div>
                  <div className="flex justify-between items-center p-3 bg-card rounded-2xl">
                    <span className="text-secondary">Preț per minut:</span>
                    <span className="text-secondary">
                      {Math.round(parseInt(service.price.replace(/[^\d]/g, '')) / service.serviceDuration)} RON/min
                    </span>
                  </div>
                </div>
              </div>

              {/* Category Information */}
              <div className="bg-background rounded-2xl p-4 border border-border">
                <h3 className="font-semibold text-primary mb-3 flex items-center gap-2">
                  {getCategoryIcon(service.category)}
                  Informații Categorie
                </h3>
                <div className="p-3 bg-card rounded-2xl">
                  <div className="flex items-center gap-3 mb-2">
                    <div className={cn(
                      "w-8 h-8 rounded-full flex items-center justify-center",
                      getCategoryColor(service.category)
                    )}>
                      {getCategoryIcon(service.category)}
                    </div>
                    <span className="font-medium text-primary">{service.category}</span>
                  </div>
                  <p className="text-sm text-secondary">
                    {service.category === 'Tuns' && 'Servicii de tunsoare și aranjare păr pentru bărbați'}
                    {service.category === 'Barbă' && 'Servicii specializate pentru îngrijirea și stilizarea bărbii'}
                    {service.category === 'Tratamente' && 'Tratamente terapeutice și de îngrijire pentru păr și scalp'}
                    {service.category === 'Pachete' && 'Combinații de servicii cu prețuri avantajoase'}
                  </p>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'settings' && (
            <div className="space-y-6">
              {/* Status Toggle */}
              <div className="bg-background rounded-2xl p-4 border border-border">
                <h3 className="font-semibold text-primary mb-4">Status Serviciu</h3>
                <div className="flex items-center justify-between p-3 bg-card rounded-2xl">
                  <div>
                    <div className="font-medium text-primary">Serviciu {service.status}</div>
                    <div className="text-sm text-secondary">
                      {service.status === 'Activ' 
                        ? 'Serviciul este disponibil pentru programări'
                        : 'Serviciul nu este disponibil pentru programări noi'
                      }
                    </div>
                  </div>
                  <button className="flex items-center gap-2 text-secondary hover:text-primary transition-colors">
                    {service.status === 'Activ' ? (
                      <ToggleRight className="w-8 h-8" />
                    ) : (
                      <ToggleLeft className="w-8 h-8" />
                    )}
                  </button>
                </div>
              </div>

              {/* Quick Actions */}
              <div className="bg-background rounded-2xl p-4 border border-border">
                <h3 className="font-semibold text-primary mb-4">Acțiuni Rapide</h3>
                <div className="space-y-2">
                  <button className="w-full text-left p-3 text-secondary hover:text-primary hover:bg-card-hover rounded-2xl transition-colors">
                    📝 Editează detaliile serviciului
                  </button>
                  <button className="w-full text-left p-3 text-secondary hover:text-primary hover:bg-card-hover rounded-2xl transition-colors">
                    📋 Dublează serviciul
                  </button>
                  <button className="w-full text-left p-3 text-secondary hover:text-primary hover:bg-card-hover rounded-2xl transition-colors">
                    📊 Vezi statistici utilizare
                  </button>
                  <button className="w-full text-left p-3 text-secondary hover:text-primary hover:bg-card-hover rounded-2xl transition-colors">
                    🔧 Modifică prețul
                  </button>
                </div>
              </div>

              {/* Danger Zone */}
              <div className="bg-background rounded-2xl p-4 border border-border">
                <h3 className="font-semibold text-primary mb-4 flex items-center gap-2">
                  <AlertCircle className="w-4 h-4 text-secondary" />
                  Zona de Risc
                </h3>
                <div className="space-y-2">
                  <button className="w-full text-left p-3 text-secondary hover:text-primary hover:bg-card-hover rounded-2xl transition-colors">
                    ⏸️ Dezactivează serviciul temporar
                  </button>
                  <button className="w-full text-left p-3 text-secondary hover:bg-secondary/10 hover:text-primary rounded-2xl transition-colors">
                    🗑️ Șterge serviciul permanent
                  </button>
                </div>
                <div className="mt-3 p-3 bg-secondary/10 rounded-2xl">
                  <p className="text-xs text-secondary">
                    <strong>Atenție:</strong> Ștergerea serviciului va afecta toate programările viitoare care includ acest serviciu.
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}