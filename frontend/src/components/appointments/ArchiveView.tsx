'use client'

import clsx from "clsx"
import { useAppointments } from '../../hooks/useAppointments'
import { AppointmentStatus } from '../../types/appointment'

import {
  Archive,
  Calendar,
  User,
  Phone,
  Search,
  Filter,
  Eye,
  Menu
} from 'lucide-react'

import { useState, useEffect } from 'react'
import HorizontalScroller from '../ui/HorizontalScroller'

interface ArchiveViewProps {
  isMobile?: boolean
  onMobileToggle?: () => void
}

export default function ArchiveView({ isMobile, onMobileToggle }: ArchiveViewProps) {
  const [searchTerm, setSearchTerm] = useState('')
  const [filterStatus, setFilterStatus] = useState<string>('all')
  const { appointments, isLoading, error, fetchAppointments } = useAppointments()

  // Fetch appointments on mount
  useEffect(() => {
    fetchAppointments()
  }, [fetchAppointments])

  // Filter appointments for archived (past dates with completed/cancelled/no-show status)
  const today = new Date().toISOString().split('T')[0]
  const archivedAppointments = appointments
    .filter(apt => apt.date < today && ['completed', 'cancelled', 'no-show'].includes(apt.status))
    .map(apt => ({
      id: apt.id,
      date: apt.date,
      time: apt.time,
      client: apt.client_name,
      phone: apt.phone,
      service: apt.service,
      status: apt.status,
      price: apt.price || '0 RON'
    }))
    .sort((a, b) => b.date.localeCompare(a.date))

  const filteredAppointments = archivedAppointments.filter(appointment => {
    const matchesSearch = appointment.client.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         appointment.service.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesFilter = filterStatus === 'all' || appointment.status === filterStatus
    return matchesSearch && matchesFilter
  })

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr)
    return date.toLocaleDateString('ro-RO', { 
      weekday: 'short', 
      day: 'numeric', 
      month: 'short',
      year: 'numeric'
    })
  }

  const getStatusBadge = (status: string) => {
    const styles = {
      completed: 'bg-secondary/20 text-primary border-border',
      cancelled: 'bg-secondary/20 text-secondary border-border',
      'no-show': 'bg-secondary/20 text-secondary border-border'
    }
    
    const labels = {
      completed: 'Finalizat',
      cancelled: 'Anulat',
      'no-show': 'Absent'
    }
    
    return (
      <span className={clsx(
        'inline-flex items-center px-2 py-1 rounded-2xl text-xs font-medium border',
        styles[status as keyof typeof styles] || 'bg-secondary/20 text-secondary border-border'
      )}>
        {labels[status as keyof typeof labels] || status}
      </span>
    )
  }

  const completedCount = archivedAppointments.filter(a => a.status === 'completed').length
  const totalRevenue = archivedAppointments
    .filter(a => a.status === 'completed')
    .reduce((sum, a) => sum + parseInt(a.price.replace(/[^\d]/g, '')), 0)

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
            <Archive className="w-8 h-8 text-secondary" />
            <div>
              <h1 className="text-3xl font-bold text-primary">Arhivă</h1>
              <p className="text-base text-secondary">
                Programări trecute și anulate ({archivedAppointments.length})
              </p>
            </div>
          </div>
        </div>

        {/* Stats */}
        <div className="hidden lg:grid lg:grid-cols-3 lg:gap-4 mb-6">
          <div className="bg-background rounded-2xl p-4 border border-border text-center">
            <div className="text-2xl font-bold text-primary">{completedCount}</div>
            <div className="text-sm text-secondary">Programări Finalizate</div>
          </div>
          <div className="bg-background rounded-2xl p-4 border border-border text-center">
            <div className="text-2xl font-bold text-primary">{totalRevenue} RON</div>
            <div className="text-sm text-secondary">Venituri Generate</div>
          </div>
          <div className="bg-background rounded-2xl p-4 border border-border text-center">
            <div className="text-2xl font-bold text-primary">{Math.round((completedCount / archivedAppointments.length) * 100)}%</div>
            <div className="text-sm text-secondary">Rata de Finalizare</div>
          </div>
        </div>

        <div className="mb-6">
          <HorizontalScroller>
            <div className="bg-background rounded-2xl p-3 border border-border text-center min-w-[200px] snap-start shrink-0">
              <div className="text-lg font-bold text-primary">{completedCount}</div>
              <div className="text-xs text-secondary">Programări Finalizate</div>
            </div>
            <div className="bg-background rounded-2xl p-3 border border-border text-center min-w-[200px] snap-start shrink-0">
              <div className="text-lg font-bold text-primary">{totalRevenue} RON</div>
              <div className="text-xs text-secondary">Venituri Generate</div>
            </div>
            <div className="bg-background rounded-2xl p-3 border border-border text-center min-w-[200px] snap-start shrink-0">
              <div className="text-lg font-bold text-primary">{Math.round((completedCount / archivedAppointments.length) * 100)}%</div>
              <div className="text-xs text-secondary">Rata de Finalizare</div>
            </div>
          </HorizontalScroller>
        </div>

        {/* Search and Filter */}
        <div className="flex flex-col lg:flex-row gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-secondary" />
            <input
              type="text"
              placeholder="Căutare după client sau serviciu..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 bg-background border border-border rounded-2xl text-primary placeholder-secondary focus:outline-none focus:border-secondary transition-colors"
            />
          </div>
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            className="px-4 py-2 bg-background border border-border rounded-2xl text-primary focus:outline-none focus:border-secondary transition-colors"
          >
            <option value="all">Toate</option>
            <option value="completed">Finalizate</option>
            <option value="cancelled">Anulate</option>
            <option value="no-show">Absențe</option>
          </select>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-6">
        {isLoading ? (
          <div className="text-center py-12">
            <div className="w-8 h-8 border-2 border-secondary border-t-primary rounded-full animate-spin mx-auto mb-4"></div>
            <p className="text-secondary">Se încarcă arhiva...</p>
          </div>
        ) : error ? (
          <div className="text-center py-12">
            <Archive className="w-12 h-12 text-secondary mx-auto mb-4" />
            <h3 className="text-lg font-medium text-primary mb-2">Eroare la încărcarea datelor</h3>
            <p className="text-secondary">{error}</p>
          </div>
        ) : (
        <div className="space-y-4">
          {filteredAppointments.map((appointment) => (
            <div key={appointment.id} className="bg-background rounded-2xl p-4 border border-border hover:bg-card-hover transition-colors">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className="text-center">
                    <div className="text-sm text-secondary">{formatDate(appointment.date)}</div>
                    <div className="text-lg font-bold text-primary">{appointment.time}</div>
                  </div>
                  
                  <div className="w-px h-12 bg-border"></div>
                  
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <User className="w-4 h-4 text-secondary" />
                      <span className="font-medium text-primary">{appointment.client}</span>
                    </div>
                    <div className="flex items-center gap-2 mb-1">
                      <Phone className="w-4 h-4 text-secondary" />
                      <span className="text-sm text-secondary">{appointment.phone}</span>
                    </div>
                    <div className="text-sm text-primary">{appointment.service}</div>
                  </div>
                </div>
                
                <div className="flex items-center gap-3">
                  {appointment.status === 'completed' && (
                    <div className="text-right mr-3">
                      <div className="font-semibold text-primary">{appointment.price}</div>
                    </div>
                  )}
                  {getStatusBadge(appointment.status)}
                  <button className="p-2 text-secondary hover:text-primary rounded-2xl hover:bg-card-hover transition-colors">
                    <Eye className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>

          {filteredAppointments.length === 0 && (
            <div className="text-center py-12">
              <Archive className="w-12 h-12 text-secondary mx-auto mb-4" />
              <h3 className="text-lg font-medium text-primary mb-2">Nu s-au găsit rezultate</h3>
              <p className="text-secondary">Încearcă să modifici criteriile de căutare.</p>
            </div>
          )}
        </div>
        )}
      </div>
    </div>
  )
}