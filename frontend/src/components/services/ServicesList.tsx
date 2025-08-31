'use client'

import { useState, useEffect } from 'react'
import {
  Search,
  Filter,
  Plus,
  Download,
  Scissors,
  Clock,
  DollarSign,
  Eye,
  Edit,
  Copy,
  MoreHorizontal,
  Package,
  Zap,
  Heart,
  Menu
  Activity,
  Ban
} from 'lucide-react'
import { cn } from '@/lib/utils'
import ServiceProfile from './ServiceProfile'
import AddServiceModal from './AddServiceModal'
import { useServices } from '@/hooks'
import type { Service as ApiService } from '@/types'

interface Service {
  id: string
  name: string
  category: 'Tuns' | 'Barbă' | 'Tratamente' | 'Pachete'
  description?: string
  serviceDuration: number // minutes
  bufferTime: number // minutes
  totalDuration: number // serviceDuration + bufferTime
  price: string
  status: 'Activ' | 'Inactiv'
  isPackage?: boolean
  packageItems?: string[] // for bundles
}

const convertedServices: Service[] = [
  {
    id: '1',
    name: 'Tunsoare Clasică',
    category: 'Tuns',
    description: 'Tunsoare clasică pentru bărbați cu spălat și aranjat',
    serviceDuration: 30,
    bufferTime: 10,
    totalDuration: 40,
    price: '45 RON',
    status: 'Activ'
  },
  {
    id: '2',
    name: 'Tunsoare + Styling',
    category: 'Tuns', 
    description: 'Tunsoare modernă cu styling și produse premium',
    serviceDuration: 45,
    bufferTime: 15,
    totalDuration: 60,
    price: '65 RON',
    status: 'Activ'
  },
  {
    id: '3',
    name: 'Aranjare Barbă',
    category: 'Barbă',
    description: 'Aranjare și conturare barbă cu produse profesionale',
    serviceDuration: 20,
    bufferTime: 5,
    totalDuration: 25,
    price: '25 RON',
    status: 'Activ'
  },
  {
    id: '4',
    name: 'Barbă Completă',
    category: 'Barbă',
    description: 'Aranjare barbă cu spălat, hidratare și styling complet',
    serviceDuration: 35,
    bufferTime: 10,
    totalDuration: 45,
    price: '40 RON',
    status: 'Activ'
  },
  {
    id: '5',
    name: 'Tratament Păr Anti-Mătreață',
    category: 'Tratamente',
    description: 'Tratament specializat pentru scalp sensibil și mătreață',
    serviceDuration: 40,
    bufferTime: 5,
    totalDuration: 45,
    price: '85 RON',
    status: 'Activ'
  },
  {
    id: '6',
    name: 'Masaj Scalp Relaxant',
    category: 'Tratamente',
    description: 'Masaj terapeutic pentru relaxare și stimulare circulație',
    serviceDuration: 25,
    bufferTime: 5,
    totalDuration: 30,
    price: '50 RON',
    status: 'Inactiv'
  },
  {
    id: '7',
    name: 'Pachet Complet Tuns + Barbă',
    category: 'Pachete',
    description: 'Combinație tunsoare clasică cu aranjare barbă',
    serviceDuration: 50,
    bufferTime: 15,
    totalDuration: 65,
    price: '60 RON',
    status: 'Activ',
    isPackage: true,
    packageItems: ['Tunsoare Clasică', 'Aranjare Barbă']
  },
  {
    id: '8',
    name: 'Pachet Premium Grooming',
    category: 'Pachete',
    description: 'Experiență completă: tuns, barbă și tratament scalp',
    serviceDuration: 90,
    bufferTime: 20,
    totalDuration: 110,
    price: '120 RON',
    status: 'Activ',
    isPackage: true,
    packageItems: ['Tunsoare + Styling', 'Barbă Completă', 'Masaj Scalp']
  }
]

interface ServicesListProps {
  isMobile?: boolean
  onMobileToggle?: () => void
}

export default function ServicesList({ isMobile, onMobileToggle }: ServicesListProps) {
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedCategory, setSelectedCategory] = useState<string>('all')
  const [selectedStatus, setSelectedStatus] = useState<string>('all')
  const [showFilters, setShowFilters] = useState(false)
  const [selectedService, setSelectedService] = useState<Service | null>(null)
  const [showAddService, setShowAddService] = useState(false)
  const [sortBy, setSortBy] = useState<'name' | 'category' | 'duration' | 'price'>('category')
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc')

  const categories = ['Tuns', 'Barbă', 'Tratamente', 'Pachete']

  const filteredServices = convertedServices
    .filter(service => {
      const matchesSearch = service.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           service.description?.toLowerCase().includes(searchTerm.toLowerCase())
      const matchesCategory = selectedCategory === 'all' || service.category === selectedCategory
      const matchesStatus = selectedStatus === 'all' || service.status === selectedStatus
      return matchesSearch && matchesCategory && matchesStatus
    })
    .sort((a, b) => {
      let aValue, bValue
      switch (sortBy) {
        case 'name':
          aValue = a.name
          bValue = b.name
          break
        case 'category':
          aValue = a.category
          bValue = b.category
          break
        case 'duration':
          aValue = a.totalDuration
          bValue = b.totalDuration
          break
        case 'price':
          aValue = parseInt(a.price.replace(/[^\d]/g, ''))
          bValue = parseInt(b.price.replace(/[^\d]/g, ''))
          break
        default:
          return 0
      }
      if (sortOrder === 'asc') {
        return aValue < bValue ? -1 : aValue > bValue ? 1 : 0
      } else {
        return aValue > bValue ? -1 : aValue < bValue ? 1 : 0
      }
    })

  const getCategoryIcon = (category: Service['category']) => {
    switch (category) {
      case 'Tuns':
        return <Scissors className="w-4 h-4" />
      case 'Barbă':
        return <Zap className="w-4 h-4" />
      case 'Tratamente':
        return <Heart className="w-4 h-4" />
      case 'Pachete':
        return <Package className="w-4 h-4" />
      default:
        return <Scissors className="w-4 h-4" />
    }
  }

  const getStatusBadge = (status: Service['status']) => {
    const styles = {
      Activ: 'bg-secondary/20 text-primary border-border',
      Inactiv: 'bg-secondary/20 text-secondary border-border'
    }
    
    return (
      <span className={cn(
        'inline-flex items-center px-2 py-1 rounded-2xl text-xs font-medium border',
        styles[status]
      )}>
        {status}
      </span>
    )
  }

  const formatDuration = (minutes: number) => {
    if (minutes >= 60) {
      const hours = Math.floor(minutes / 60)
      const mins = minutes % 60
      return mins > 0 ? `${hours}h ${mins}min` : `${hours}h`
    }
    return `${minutes}min`
  }

  const getServicesByCategory = (category: string) => {
    return convertedServices.filter(s => s.category === category && s.status === 'Activ').length
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
            <Scissors className="w-8 h-8 text-secondary" />
            <div>
              <h1 className="text-3xl font-bold text-primary">Servicii</h1>
              <p className="text-base text-secondary">
                Catalog servicii
              </p>
            </div>
          </div>
          <button 
            onClick={() => setShowAddService(true)}
            className="flex items-center px-4 py-2 bg-background text-secondary border border-border rounded-2xl hover:text-primary hover:border-secondary transition-colors"
          >
            <Plus className="w-4 h-4 mr-2" />
            Adaugă Serviciu
          </button>
        </div>


        {/* Search and Filters */}
        <div className="flex flex-col lg:flex-row gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-secondary" />
            <input
              type="text"
              placeholder="Căutare servicii după nume sau descriere..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 bg-background border border-border rounded-2xl text-primary placeholder-secondary focus:outline-none focus:border-secondary transition-colors"
            />
          </div>
          <div className="flex gap-2">
            <button 
              onClick={() => setShowFilters(!showFilters)}
              className={cn(
                "flex items-center px-4 py-2 rounded-2xl transition-colors border",
                showFilters 
                  ? 'bg-secondary/20 text-primary border-border' 
                  : 'bg-background text-secondary border-border hover:text-primary hover:border-secondary'
              )}
            >
              <Filter className="w-4 h-4 mr-2" />
              Filtrare
            </button>
            <button className="flex items-center px-4 py-2 bg-background text-secondary border border-border rounded-2xl hover:text-primary hover:border-secondary transition-colors">
              <Download className="w-4 h-4 mr-2" />
              Export
            </button>
          </div>
        </div>

        {/* Filter Panel */}
        {showFilters && (
          <div className="mt-4 p-4 bg-background rounded-2xl border border-border">
            <div className="flex flex-wrap gap-4">
              <div className="flex flex-col">
                <label className="text-xs text-secondary uppercase tracking-wider mb-2">Categorie</label>
                <select 
                  value={selectedCategory}
                  onChange={(e) => setSelectedCategory(e.target.value)}
                  className="px-3 py-2 bg-card border border-border rounded-2xl text-primary focus:outline-none focus:border-secondary"
                >
                  <option value="all">Toate</option>
                  <option value="Tuns">Tuns</option>
                  <option value="Barbă">Barbă</option>
                  <option value="Tratamente">Tratamente</option>
                  <option value="Pachete">Pachete</option>
                </select>
              </div>
              <div className="flex flex-col">
                <label className="text-xs text-secondary uppercase tracking-wider mb-2">Status</label>
                <select 
                  value={selectedStatus}
                  onChange={(e) => setSelectedStatus(e.target.value)}
                  className="px-3 py-2 bg-card border border-border rounded-2xl text-primary focus:outline-none focus:border-secondary"
                >
                  <option value="all">Toate</option>
                  <option value="Activ">Activ</option>
                  <option value="Inactiv">Inactiv</option>
                </select>
              </div>
              <div className="flex flex-col">
                <label className="text-xs text-secondary uppercase tracking-wider mb-2">Sortare</label>
                <select 
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value as any)}
                  className="px-3 py-2 bg-card border border-border rounded-2xl text-primary focus:outline-none focus:border-secondary"
                >
                  <option value="category">Categorie</option>
                  <option value="name">Nume</option>
                  <option value="duration">Durată</option>
                  <option value="price">Preț</option>
                </select>
              </div>
              <div className="flex flex-col">
                <label className="text-xs text-secondary uppercase tracking-wider mb-2">Ordine</label>
                <select 
                  value={sortOrder}
                  onChange={(e) => setSortOrder(e.target.value as 'asc' | 'desc')}
                  className="px-3 py-2 bg-card border border-border rounded-2xl text-primary focus:outline-none focus:border-secondary"
                >
                  <option value="asc">Crescător</option>
                  <option value="desc">Descrescător</option>
                </select>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Services Table */}
      <div className="flex-1 overflow-y-auto">
        <div className="p-6">
          <div className="bg-background rounded-2xl border border-border overflow-hidden">
            {/* Table Header */}
            <div className="grid grid-cols-12 gap-4 p-4 border-b border-border text-xs font-semibold text-secondary uppercase tracking-wider">
              <div className="col-span-4">Serviciu</div>
              <div className="col-span-2">Categorie</div>
              <div className="col-span-2">Durată Totală</div>
              <div className="col-span-2">Preț</div>
              <div className="col-span-1">Status</div>
              <div className="col-span-1 text-center">Acțiuni</div>
            </div>

            {/* Table Body */}
            <div className="divide-y divide-border">
              {filteredServices.map((service) => (
                <div key={service.id} className="grid grid-cols-12 gap-4 p-4 hover:bg-card-hover transition-colors group">
                  {/* Service Info */}
                  <div className="col-span-4">
                    <div className="flex items-start gap-3">
                      <div className="w-10 h-10 rounded-full bg-secondary/20 flex items-center justify-center text-secondary">
                        {getCategoryIcon(service.category)}
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          <span className="font-medium text-primary">{service.name}</span>
                          {service.isPackage && (
                            <span className="inline-flex items-center px-1 py-0.5 rounded text-xs bg-secondary/20 text-secondary border border-border">
                              <Package className="w-3 h-3 mr-1" />
                              Pachet
                            </span>
                          )}
                        </div>
                        {service.description && (
                          <div className="text-sm text-secondary mt-1 line-clamp-2">
                            {service.description}
                          </div>
                        )}
                        {service.isPackage && service.packageItems && (
                          <div className="text-xs text-secondary mt-1">
                            Include: {service.packageItems.join(', ')}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Category */}
                  <div className="col-span-2">
                    <div className="flex items-center gap-2">
                      {getCategoryIcon(service.category)}
                      <span className="text-primary">{service.category}</span>
                    </div>
                  </div>

                  {/* Duration */}
                  <div className="col-span-2">
                    <div className="flex items-center gap-2">
                      <Clock className="w-4 h-4 text-secondary" />
                      <span className="font-semibold text-primary">
                        {formatDuration(service.totalDuration)}
                      </span>
                    </div>
                    <div className="text-xs text-secondary">
                      Serviciu: {formatDuration(service.serviceDuration)} + Tampon: {formatDuration(service.bufferTime)}
                    </div>
                  </div>

                  {/* Price */}
                  <div className="col-span-2">
                    <div className="flex items-center gap-2">
                      <span className="font-semibold text-primary">{service.price.replace(' RON', '').replace('RON', '')} RON</span>
                    </div>
                  </div>

                  {/* Status */}
                  <div className="col-span-1">
                    {getStatusBadge(service.status)}
                  </div>

                  {/* Actions */}
                  <div className="col-span-1 text-center">
                    <div className="flex items-center justify-center gap-1">
                      <button 
                        onClick={() => setSelectedService(service)}
                        className="p-1 text-secondary hover:text-primary rounded transition-colors"
                        title="Vezi detalii"
                      >
                        <Eye className="w-4 h-4" />
                      </button>
                      <button 
                        className="p-1 text-secondary hover:text-primary rounded transition-colors"
                        title="Editează"
                      >
                        <Edit className="w-4 h-4" />
                      </button>
                      <button 
                        className="p-1 text-secondary hover:text-primary rounded transition-colors"
                        title="Dublează"
                      >
                        <Copy className="w-4 h-4" />
                      </button>
                      <button 
                        className="p-1 text-secondary hover:text-primary rounded transition-colors"
                        title="Mai multe opțiuni"
                      >
                        <MoreHorizontal className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {filteredServices.length === 0 && (
            <div className="text-center py-12">
              <Scissors className="w-12 h-12 text-secondary mx-auto mb-4" />
              <h3 className="text-lg font-medium text-primary mb-2">Niciun serviciu găsit</h3>
              <p className="text-secondary">Încearcă să modifici criteriile de căutare sau filtrare.</p>
            </div>
          )}
        </div>
      </div>

      {/* Modals */}
      {selectedService && (
        <ServiceProfile
          service={selectedService}
          onClose={() => setSelectedService(null)}
        />
      )}

      {showAddService && (
        <AddServiceModal
          onClose={() => setShowAddService(false)}
          onSave={(serviceData) => {
            console.log('New service:', serviceData)
            setShowAddService(false)
          }}
        />
      )}
    </div>
  )
}