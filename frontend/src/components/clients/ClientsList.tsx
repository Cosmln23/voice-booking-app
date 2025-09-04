'use client'

import clsx from "clsx"

import { useState, useEffect } from 'react'
import {
  Search,
  Filter,
  Plus,
  Download,
  Menu,
  Phone,
  Mail,
  Calendar,
  Eye,
  Edit,
  MoreHorizontal,
  Users,
  Star,
  AlertTriangle,
  Activity,
  Ban
} from 'lucide-react'

import ClientProfile from './ClientProfile'
import AddClientModal from './AddClientModal'
import { useClients } from '../../hooks'
import type { Client as ApiClient, ClientStatus } from '../../types'
import ResponsiveTable, { ResponsiveTableRow, ResponsiveTableCell } from '../ui/ResponsiveTable'

// Extended client interface for component compatibility
interface Client {
  id: string
  name: string
  phone: string
  email: string
  lastVisit: string
  totalVisits: number
  status: 'VIP' | 'Standard' | 'New' | 'Inactive'
  ltv: string
  notes?: string
  preferences?: string
  noShows?: number
  gdprConsent: boolean
  nextAppointment?: string
}

const convertedClients: Client[] = [
  {
    id: '1',
    name: 'Maria Ionescu',
    phone: '+40 721 123 456',
    email: 'maria.ionescu@email.com',
    lastVisit: '2025-01-28',
    totalVisits: 24,
    status: 'VIP',
    ltv: '2,400 RON',
    notes: 'Preferă stilista Ana, alergică la sulfați',
    preferences: 'Tunsoare bob, balayage',
    gdprConsent: true,
    nextAppointment: '2025-02-05'
  },
  {
    id: '2', 
    name: 'Elena Popescu',
    phone: '+40 722 987 654',
    email: 'elena.popescu@email.com',
    lastVisit: '2025-01-25',
    totalVisits: 12,
    status: 'Standard',
    ltv: '1,200 RON',
    notes: 'Vine cu mama, întotdeauna punctuală',
    preferences: 'Coafura clasică, manichiură',
    gdprConsent: true
  },
  {
    id: '3',
    name: 'Andreea Tănase',
    phone: '+40 723 456 789',
    email: 'andreea.tanase@email.com', 
    lastVisit: '2025-01-30',
    totalVisits: 3,
    status: 'New',
    ltv: '450 RON',
    notes: 'Client nou, foarte entuziastă',
    preferences: 'Încă nu știe exact ce dorește',
    gdprConsent: true,
    nextAppointment: '2025-02-03'
  },
  {
    id: '4',
    name: 'Alexandra Radu',
    phone: '+40 724 111 222',
    email: 'alexandra.radu@email.com',
    lastVisit: '2024-11-15',
    totalVisits: 8,
    status: 'Inactive',
    ltv: '960 RON',
    notes: 'Nu a mai venit de 2 luni',
    preferences: 'Coafura evenimente speciale',
    gdprConsent: false
  },
  {
    id: '5',
    name: 'Diana Constantinescu',
    phone: '+40 725 333 444',
    email: 'diana.const@email.com',
    lastVisit: '2025-01-20',
    totalVisits: 15,
    status: 'Inactive',
    ltv: '1,800 RON',
    notes: 'Nu a mai venit de câteva săptămâni',
    preferences: 'Tratamente păr, vopsit',
    gdprConsent: true
  }
]

interface ClientsListProps {
  isMobile?: boolean
  onMobileToggle?: () => void
}

export default function ClientsList({ isMobile, onMobileToggle }: ClientsListProps) {
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedStatus, setSelectedStatus] = useState<string>('all')
  const [showFilters, setShowFilters] = useState(false)
  const [selectedClient, setSelectedClient] = useState<Client | null>(null)
  const [showAddClient, setShowAddClient] = useState(false)
  const [sortBy, setSortBy] = useState<'name' | 'lastVisit' | 'totalVisits' | 'ltv'>('lastVisit')
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc')

  // Use real API data
  const { 
    clients: apiClients, 
    total, 
    stats,
    isLoading, 
    error, 
    fetchClients,
    fetchStats,
    createClient
  } = useClients()

  // Fetch clients on component mount
  useEffect(() => {
    fetchClients({ limit: 50, offset: 0 })
    fetchStats()
  }, [fetchClients, fetchStats])

  // Convert API clients to component format for compatibility
  const convertApiClients = (clients: ApiClient[]): Client[] => {
    return clients.map(client => ({
      id: client.id,
      name: client.name,
      phone: client.phone,
      email: client.email || '',
      lastVisit: client.last_appointment ? new Date(client.last_appointment).toISOString().split('T')[0] : '2024-01-01',
      totalVisits: client.total_appointments,
      status: client.total_appointments > 10 ? 'VIP' : client.total_appointments > 0 ? 'Standard' : 'New',
      ltv: `${(client.total_appointments * 50)} RON`, // Estimate
      notes: client.notes,
      preferences: '',
      noShows: 0,
      gdprConsent: true,
      nextAppointment: undefined
    }))
  }

  const convertedClients = convertApiClients(apiClients)

  // Phone normalization for Romanian format
  const normalizePhone = (phone: string): string => {
    const digits = phone.replace(/[^\d+]/g, ''); // Keep only digits and +
    if (digits.startsWith('+')) return digits;   // Already has prefix
    if (digits.startsWith('0')) return `+4${digits}`; // 0712... -> +40712...
    return `+${digits}`; // Fallback
  }

  // Handle client creation with backend integration
  const handleCreateClient = async (clientData: any) => {
    try {
      // Convert form data to backend format  
      const clientPayload = {
        name: clientData.name.trim(),
        phone: normalizePhone(clientData.phone),
        email: clientData.email.trim(),
        status: (clientData.status === 'Inactive' ? 'inactive' : 'active') as ClientStatus, // Map to backend enum
        notes: clientData.notes?.trim() || undefined
        // Note: preferences not supported in backend model
      }
      
      await createClient(clientPayload)
      setShowAddClient(false)
      
      // Refresh client list
      fetchClients({ limit: 50, offset: 0 })
    } catch (error) {
      console.error('Error creating client:', error)
      alert('Eroare la crearea clientului')
    }
  }

  // Handle loading and error states
  if (isLoading && apiClients.length === 0) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <Activity className="w-8 h-8 animate-spin mx-auto mb-2 text-primary" />
          <p className="text-secondary">Se încarcă clienții...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <Ban className="w-8 h-8 mx-auto mb-2 text-destructive" />
          <p className="text-destructive mb-2">Eroare la încărcarea datelor</p>
          <button 
            onClick={() => fetchClients()}
            className="text-sm text-primary hover:underline"
          >
            Încearcă din nou
          </button>
        </div>
      </div>
    )
  }

  const filteredClients = convertedClients
    .filter(client => {
      const matchesSearch = client.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           client.phone.includes(searchTerm) ||
                           client.email.toLowerCase().includes(searchTerm.toLowerCase())
      const matchesStatus = selectedStatus === 'all' || client.status === selectedStatus
      return matchesSearch && matchesStatus
    })
    .sort((a, b) => {
      let aValue, bValue
      switch (sortBy) {
        case 'name':
          aValue = a.name
          bValue = b.name
          break
        case 'lastVisit':
          aValue = new Date(a.lastVisit).getTime()
          bValue = new Date(b.lastVisit).getTime()
          break
        case 'totalVisits':
          aValue = a.totalVisits
          bValue = b.totalVisits
          break
        case 'ltv':
          aValue = parseInt(a.ltv.replace(/[^\d]/g, ''))
          bValue = parseInt(b.ltv.replace(/[^\d]/g, ''))
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

  const getStatusBadge = (status: Client['status']) => {
    const styles = {
      VIP: 'bg-secondary/20 text-primary border-border',
      Standard: 'bg-secondary/20 text-primary border-border',
      New: 'bg-secondary/20 text-primary border-border',
      Inactive: 'bg-secondary/20 text-secondary border-border'
    }
    
    return (
      <span className={clsx(
        'inline-flex items-center px-2 py-1 rounded-2xl text-xs font-medium border',
        styles[status]
      )}>
        {status}
      </span>
    )
  }

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr)
    return date.toLocaleDateString('ro-RO', { 
      day: '2-digit', 
      month: 'short', 
      year: 'numeric' 
    })
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
            <Users className="w-8 h-8 text-secondary" />
            <div>
              <h1 className="text-3xl font-bold text-primary">Clienți</h1>
              <p className="text-base text-secondary">
                Baza de date
              </p>
            </div>
          </div>
          <button 
            onClick={() => setShowAddClient(true)}
            className="flex items-center px-4 py-2 bg-background text-secondary border border-border rounded-2xl hover:text-primary hover:border-accent transition-colors"
          >
            <Plus className="w-4 h-4 mr-2" />
            Adaugă Client
          </button>
        </div>

        {/* Search and Filters */}
        <div className="flex flex-col lg:flex-row gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-secondary" />
            <input
              type="text"
              placeholder="Căutare clienți după nume, telefon sau email..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 bg-background border border-border rounded-2xl text-primary placeholder-secondary focus:outline-none focus:border-accent transition-colors"
            />
          </div>
          <div className="flex gap-2">
            <button 
              onClick={() => setShowFilters(!showFilters)}
              className={clsx(
                "flex items-center px-4 py-2 rounded-2xl transition-colors border",
                showFilters 
                  ? 'bg-accent text-white border-accent' 
                  : 'bg-background text-secondary border-border hover:text-primary hover:border-accent'
              )}
            >
              <Filter className="w-4 h-4 mr-2" />
              Filtrare
            </button>
            <button className="flex items-center px-4 py-2 bg-background text-secondary border border-border rounded-2xl hover:text-primary hover:border-accent transition-colors">
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
                <label className="text-xs text-secondary uppercase tracking-wider mb-2">Status</label>
                <select 
                  value={selectedStatus}
                  onChange={(e) => setSelectedStatus(e.target.value)}
                  className="px-3 py-2 bg-card border border-border rounded-2xl text-primary focus:outline-none focus:border-accent"
                >
                  <option value="all">Toate</option>
                  <option value="VIP">VIP</option>
                  <option value="Standard">Standard</option>
                  <option value="New">Nou</option>
                  <option value="Inactive">Inactiv</option>
                </select>
              </div>
              <div className="flex flex-col">
                <label className="text-xs text-secondary uppercase tracking-wider mb-2">Sortare</label>
                <select 
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value as any)}
                  className="px-3 py-2 bg-card border border-border rounded-2xl text-primary focus:outline-none focus:border-accent"
                >
                  <option value="lastVisit">Ultima vizită</option>
                  <option value="name">Nume</option>
                  <option value="totalVisits">Total vizite</option>
                  <option value="ltv">Valoare client</option>
                </select>
              </div>
              <div className="flex flex-col">
                <label className="text-xs text-secondary uppercase tracking-wider mb-2">Ordine</label>
                <select 
                  value={sortOrder}
                  onChange={(e) => setSortOrder(e.target.value as 'asc' | 'desc')}
                  className="px-3 py-2 bg-card border border-border rounded-2xl text-primary focus:outline-none focus:border-accent"
                >
                  <option value="desc">Descrescător</option>
                  <option value="asc">Crescător</option>
                </select>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Clients Table */}
      <div className="flex-1 overflow-y-auto">
        <div className="p-6">
          <ResponsiveTable
            columns={[
              { key: 'client', label: 'Client', minWidth: '200px' },
              { key: 'contact', label: 'Contact', minWidth: '200px', hideOnMobile: true },
              { key: 'lastVisit', label: 'Ultima Vizită', minWidth: '150px' },
              { key: 'visits', label: 'Vizite', minWidth: '80px', className: 'text-center' },
              { key: 'status', label: 'Status', minWidth: '120px' },
              { key: 'actions', label: 'Acțiuni', minWidth: '120px', className: 'text-center' }
            ]}
            mobileMinWidth="800px"
          >
            {filteredClients.map((client) => (
              <ResponsiveTableRow
                key={client.id}
                columns={[
                  { key: 'client', label: 'Client', minWidth: '200px' },
                  { key: 'contact', label: 'Contact', minWidth: '200px', hideOnMobile: true },
                  { key: 'lastVisit', label: 'Ultima Vizită', minWidth: '150px' },
                  { key: 'visits', label: 'Vizite', minWidth: '80px', className: 'text-center' },
                  { key: 'status', label: 'Status', minWidth: '120px' },
                  { key: 'actions', label: 'Acțiuni', minWidth: '120px', className: 'text-center' }
                ]}
                className="group"
              >
                {/* Client Info */}
                <ResponsiveTableCell column={{ key: 'client', label: 'Client', minWidth: '200px' }}>
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-secondary/20 flex items-center justify-center text-primary font-semibold">
                      {client.name.split(' ').map(n => n[0]).join('').toUpperCase()}
                    </div>
                    <div>
                      <div className="font-medium text-primary">{client.name}</div>
                      {client.nextAppointment && (
                        <div className="text-xs text-secondary">
                          Următor: {formatDate(client.nextAppointment)}
                        </div>
                      )}
                    </div>
                  </div>
                </ResponsiveTableCell>

                {/* Contact - Hidden on mobile */}
                <ResponsiveTableCell column={{ key: 'contact', label: 'Contact', minWidth: '200px', hideOnMobile: true }}>
                  <div className="space-y-1">
                    <div className="flex items-center gap-2 text-sm text-primary">
                      <Phone className="w-3 h-3 text-secondary" />
                      {client.phone}
                    </div>
                    <div className="flex items-center gap-2 text-sm text-secondary">
                      <Mail className="w-3 h-3" />
                      {client.email}
                    </div>
                  </div>
                </ResponsiveTableCell>

                {/* Last Visit */}
                <ResponsiveTableCell column={{ key: 'lastVisit', label: 'Ultima Vizită', minWidth: '150px' }}>
                  <div className="flex items-center gap-2 text-sm text-primary">
                    <Calendar className="w-3 h-3 text-secondary" />
                    {formatDate(client.lastVisit)}
                  </div>
                </ResponsiveTableCell>

                {/* Total Visits */}
                <ResponsiveTableCell column={{ key: 'visits', label: 'Vizite', minWidth: '80px', className: 'text-center' }}>
                  <span className="inline-flex items-center justify-center w-8 h-8 bg-secondary/20 text-primary rounded-full text-sm font-semibold">
                    {client.totalVisits}
                  </span>
                </ResponsiveTableCell>

                {/* Status */}
                <ResponsiveTableCell column={{ key: 'status', label: 'Status', minWidth: '120px' }}>
                  {getStatusBadge(client.status)}
                </ResponsiveTableCell>

                {/* Actions */}
                <ResponsiveTableCell column={{ key: 'actions', label: 'Acțiuni', minWidth: '120px', className: 'text-center' }}>
                  <div className="flex items-center justify-center gap-1">
                    <button 
                      onClick={() => setSelectedClient(client)}
                      className="p-1 text-secondary hover:text-primary rounded transition-colors"
                      title="Vezi profil"
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
                      title="Mai multe opțiuni"
                    >
                      <MoreHorizontal className="w-4 h-4" />
                    </button>
                  </div>
                </ResponsiveTableCell>
              </ResponsiveTableRow>
            ))}
          </ResponsiveTable>

          {filteredClients.length === 0 && (
            <div className="text-center py-12">
              <Users className="w-12 h-12 text-secondary mx-auto mb-4" />
              <h3 className="text-lg font-medium text-primary mb-2">Niciun client găsit</h3>
              <p className="text-secondary">Încearcă să modifici criteriile de căutare sau filtrare.</p>
            </div>
          )}
        </div>
      </div>

      {/* Modals */}
      {selectedClient && (
        <ClientProfile
          client={selectedClient}
          onClose={() => setSelectedClient(null)}
        />
      )}

      {showAddClient && (
        <AddClientModal
          onClose={() => setShowAddClient(false)}
          onSave={handleCreateClient}
        />
      )}
    </div>
  )
}