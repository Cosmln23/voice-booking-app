'use client'

import clsx from "clsx"

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
  Menu,
  Activity,
  Ban
} from 'lucide-react'

import ServiceProfile from './ServiceProfile'
import AddServiceModal from './AddServiceModal'
import { useServices } from '../../hooks'
import type { Service, ServiceStatus, ServiceCategory } from '../../types'
import ResponsiveTable, { ResponsiveTableRow, ResponsiveTableCell } from '../ui/ResponsiveTable'


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
  const [showEditService, setShowEditService] = useState(false)
  const [serviceToEdit, setServiceToEdit] = useState<Service | null>(null)
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false)
  const [serviceToDelete, setServiceToDelete] = useState<Service | null>(null)
  const [showDropdownForService, setShowDropdownForService] = useState<string | null>(null)
  const [sortBy, setSortBy] = useState<'name' | 'category' | 'duration' | 'price'>('category')
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc')

  // Use real API data
  const {
    services,
    total,
    isLoading,
    error,
    fetchServices,
    createService,
    updateService,
    deleteService
  } = useServices()

  // Fetch services on component mount
  useEffect(() => {
    fetchServices({ limit: 50, offset: 0 })
  }, [fetchServices])

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (showDropdownForService) {
        setShowDropdownForService(null)
      }
    }
    
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [showDropdownForService])

  // Helper to normalize service data for API
  const toServiceCreatePayload = (s: Service) => {
    return {
      name: `${s.name} (Copie)`,
      price: s.price,
      currency: s.currency,
      duration: s.duration,
      category: s.category,
      status: s.status,
      description: s.description ?? ''
    }
  }

  // Action handlers
  const handleEditService = (service: Service) => {
    setServiceToEdit(service)
    setShowEditService(true)
  }

  const handleDuplicateService = async (service: Service) => {
    try {
      await createService(toServiceCreatePayload(service))
      await fetchServices()  // Refresh lista după creare
    } catch (error) {
      console.error('Error duplicating service:', error)
    }
  }

  const handleDeleteService = (service: Service) => {
    setServiceToDelete(service)
    setShowDeleteConfirm(true)
  }

  const confirmDelete = async () => {
    if (!serviceToDelete) return
    
    try {
      await deleteService(serviceToDelete.id)
      await fetchServices()  // Refresh lista după ștergere
      setShowDeleteConfirm(false)
      setServiceToDelete(null)
    } catch (error) {
      console.error('Error deleting service:', error)
    }
  }

  const categories = ['Tuns', 'Barbă', 'Tratamente', 'Pachete']

  // Use only API services - no mock data fallback
  const loading = isLoading && services.length === 0
  const hasData = services.length > 0
  const servicesToUse = services
  
  const filteredServices = servicesToUse
    .filter(service => {
      const matchesSearch = service.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           service.description?.toLowerCase().includes(searchTerm.toLowerCase())
      const matchesCategory = selectedCategory === 'all' || service.category === selectedCategory
      const matchesStatus = selectedStatus === 'all' || service.status === selectedStatus
      return matchesSearch && matchesCategory && matchesStatus
    })
    .sort((a, b) => {
      let aValue: string | number, bValue: string | number
      switch (sortBy) {
        case 'name':
          aValue = a.name
          bValue = b.name
          return sortOrder === 'asc' ? aValue.localeCompare(bValue) : bValue.localeCompare(aValue)
        case 'category':
          aValue = a.category
          bValue = b.category
          return sortOrder === 'asc' ? aValue.localeCompare(bValue) : bValue.localeCompare(aValue)
        case 'duration':
          aValue = parseInt(a.duration?.replace('min', '') || '0')
          bValue = parseInt(b.duration?.replace('min', '') || '0')
          break
        case 'price':
          aValue = a.price
          bValue = b.price
          break
        default:
          return 0
      }
      if (sortOrder === 'asc') {
        return (aValue as number) < (bValue as number) ? -1 : (aValue as number) > (bValue as number) ? 1 : 0
      } else {
        return (aValue as number) > (bValue as number) ? -1 : (aValue as number) < (bValue as number) ? 1 : 0
      }
    })

  // Handle service creation with backend integration
  const handleCreateService = async (serviceData: any) => {
    try {
      // Convert form data to backend format
      const servicePayload = {
        name: serviceData.name.trim(),
        price: typeof serviceData.price === 'string' 
          ? parseFloat(serviceData.price.replace(/[^\d.,]/g, '').replace(',', '.'))
          : serviceData.price,
        currency: 'RON',
        duration: `${serviceData.serviceDuration || 30}min`,
        category: serviceData.category as ServiceCategory,
        description: serviceData.description?.trim() || undefined,
        status: serviceData.status as ServiceStatus
      }
      
      await createService(servicePayload)
      setShowAddService(false)
      
      // Refresh services list
      fetchServices({ limit: 50, offset: 0 })
    } catch (error) {
      console.error('Error creating service:', error)
      alert('Eroare la crearea serviciului')
    }
  }

  const getCategoryIcon = (category: ServiceCategory) => {
    switch (category) {
      case 'individual':
        return <Scissors className="w-4 h-4" />
      case 'package':
        return <Package className="w-4 h-4" />
      default:
        return <Scissors className="w-4 h-4" />
    }
  }

  const getStatusBadge = (status: ServiceStatus) => {
    const displayStatus = status === 'active' ? 'Activ' : 'Inactiv';
    const styles = {
      Activ: 'bg-secondary/20 text-primary border-border',
      Inactiv: 'bg-secondary/20 text-secondary border-border'
    }
    
    return (
      <span className={clsx(
        'inline-flex items-center px-2 py-1 rounded-2xl text-xs font-medium border',
        styles[displayStatus as keyof typeof styles]
      )}>
        {displayStatus}
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

  const getServicesByCategory = (category: ServiceCategory) => {
    return services.filter(s => s.category === category && s.status === 'active').length
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
              className={clsx(
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
                  <option value="individual">Individual</option>
                  <option value="package">Pachet</option>
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
                  <option value="active">Activ</option>
                  <option value="inactive">Inactiv</option>
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
          {loading && (
            <div className="bg-background rounded-2xl border border-border p-8 text-center text-secondary">
              Se încarcă serviciile...
            </div>
          )}
          
          {!loading && !hasData && (
            <div className="bg-background rounded-2xl border border-border p-8 text-center text-secondary">
              Nu există servicii încă.
            </div>
          )}
          
          {!loading && hasData && (
            <ResponsiveTable
              columns={[
                { key: 'service', label: 'Serviciu', minWidth: '250px' },
                { key: 'category', label: 'Categorie', minWidth: '120px' },
                { key: 'duration', label: 'Durată Totală', minWidth: '150px' },
                { key: 'price', label: 'Preț', minWidth: '100px' },
                { key: 'status', label: 'Status', minWidth: '100px' },
                { key: 'actions', label: 'Acțiuni', minWidth: '200px', className: 'text-center' }
              ]}
              mobileMinWidth="1000px"
            >
              {filteredServices.map((service) => (
                <ResponsiveTableRow
                  key={service.id}
                  columns={[
                    { key: 'service', label: 'Serviciu', minWidth: '250px' },
                    { key: 'category', label: 'Categorie', minWidth: '120px' },
                    { key: 'duration', label: 'Durată Totală', minWidth: '150px' },
                    { key: 'price', label: 'Preț', minWidth: '100px' },
                    { key: 'status', label: 'Status', minWidth: '100px' },
                    { key: 'actions', label: 'Acțiuni', minWidth: '200px', className: 'text-center' }
                  ]}
                  className="group"
                >
                  {/* Service Info */}
                  <ResponsiveTableCell column={{ key: 'service', label: 'Serviciu', minWidth: '250px' }}>
                    <div className="flex items-start gap-3">
                      <div className="w-10 h-10 rounded-full bg-secondary/20 flex items-center justify-center text-secondary">
                        {getCategoryIcon(service.category)}
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          <span className="font-medium text-primary">{service.name}</span>
                          {service.category === 'package' && (
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
                      </div>
                    </div>
                  </ResponsiveTableCell>

                  {/* Category */}
                  <ResponsiveTableCell column={{ key: 'category', label: 'Categorie', minWidth: '120px' }}>
                    <div className="flex items-center gap-2">
                      {getCategoryIcon(service.category)}
                      <span className="text-primary">{service.category === 'individual' ? 'Individual' : 'Pachet'}</span>
                    </div>
                  </ResponsiveTableCell>

                  {/* Duration */}
                  <ResponsiveTableCell column={{ key: 'duration', label: 'Durată Totală', minWidth: '150px' }}>
                    <div className="flex items-center gap-2">
                      <Clock className="w-4 h-4 text-secondary" />
                      <span className="font-semibold text-primary">
                        {service.duration}
                      </span>
                    </div>
                    <div className="text-xs text-secondary">
                      Durata: {service.duration}
                    </div>
                  </ResponsiveTableCell>

                  {/* Price */}
                  <ResponsiveTableCell column={{ key: 'price', label: 'Preț', minWidth: '100px' }}>
                    <div className="flex items-center gap-2">
                      <span className="font-semibold text-primary">
                        {service.price} {service.currency}
                      </span>
                    </div>
                  </ResponsiveTableCell>

                  {/* Status */}
                  <ResponsiveTableCell column={{ key: 'status', label: 'Status', minWidth: '100px' }}>
                    {getStatusBadge(service.status)}
                  </ResponsiveTableCell>

                  {/* Actions */}
                  <ResponsiveTableCell column={{ key: 'actions', label: 'Acțiuni', minWidth: '200px', className: 'text-center' }}>
                    <div className="relative flex items-center justify-center gap-1">
                      <button 
                        onClick={() => setSelectedService(service)}
                        className="p-1 text-secondary hover:text-primary rounded transition-colors"
                        title="Vezi detalii"
                      >
                        <Eye className="w-4 h-4" />
                      </button>
                      <button 
                        onClick={() => handleEditService(service)}
                        className="p-1 text-secondary hover:text-primary rounded transition-colors"
                        title="Editează"
                      >
                        <Edit className="w-4 h-4" />
                      </button>
                      <button 
                        onClick={() => handleDuplicateService(service)}
                        className="p-1 text-secondary hover:text-primary rounded transition-colors"
                        title="Dublează"
                      >
                        <Copy className="w-4 h-4" />
                      </button>
                      <button 
                        onClick={() => setShowDropdownForService(showDropdownForService === service.id ? null : service.id)}
                        className="p-1 text-secondary hover:text-primary rounded transition-colors"
                        title="Mai multe opțiuni"
                        type="button"
                      >
                        <MoreHorizontal className="w-4 h-4" />
                      </button>
                      
                      {/* Dropdown în afara butonului */}
                      {showDropdownForService === service.id && (
                        <div className="absolute right-0 top-8 bg-card border border-border rounded-lg shadow-lg z-50 min-w-[140px]">
                          <button
                            type="button"
                            onClick={(e) => {
                              e.stopPropagation()
                              handleDeleteService(service)
                              setShowDropdownForService(null)
                            }}
                            className="flex items-center w-full px-3 py-2 text-sm text-destructive hover:bg-destructive/10 rounded-lg transition-colors text-left"
                          >
                            Șterge
                          </button>
                        </div>
                      )}
                    </div>
                  </ResponsiveTableCell>
                </ResponsiveTableRow>
              ))}
            </ResponsiveTable>
          )}

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
          onSave={handleCreateService}
        />
      )}

      {showEditService && serviceToEdit && (
        <AddServiceModal
          onClose={() => {
            setShowEditService(false)
            setServiceToEdit(null)
          }}
          onSave={async (serviceData) => {
            if (!serviceToEdit) return
            const servicePayload = {
              name: serviceData.name?.trim(),
              price: typeof serviceData.price === 'string' 
                ? parseFloat(serviceData.price.replace(/[^\d.,]/g, '').replace(',', '.'))
                : serviceData.price,
              currency: 'RON',
              duration: `${serviceData.serviceDuration || 30}min`,
              category: serviceData.category as ServiceCategory,
              status: serviceData.status as ServiceStatus,
              description: serviceData.description?.trim()
            }
            await updateService(serviceToEdit.id, servicePayload)
            setShowEditService(false)
            setServiceToEdit(null)
          }}
          initialData={{
            name: serviceToEdit.name,
            category: serviceToEdit.category,
            description: serviceToEdit.description,
            serviceDuration: parseInt(serviceToEdit.duration?.replace('min', '') || '30'),
            price: serviceToEdit.price.toString(),
            status: serviceToEdit.status
          }}
        />
      )}

      {showDeleteConfirm && serviceToDelete && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-card border border-border rounded-lg p-6 max-w-md mx-4">
            <h3 className="text-lg font-semibold text-primary mb-4">Confirmă ștergerea</h3>
            <p className="text-secondary mb-6">
              Ești sigur că vrei să ștergi serviciul &quot;{serviceToDelete.name}&quot;? Această acțiune nu poate fi anulată.
            </p>
            <div className="flex gap-3 justify-end">
              <button
                onClick={() => {
                  setShowDeleteConfirm(false)
                  setServiceToDelete(null)
                }}
                className="px-4 py-2 text-secondary hover:text-primary border border-border rounded-lg transition-colors"
              >
                Anulează
              </button>
              <button
                onClick={confirmDelete}
                className="px-4 py-2 bg-destructive text-white rounded-lg hover:bg-destructive/90 transition-colors"
              >
                Șterge
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}