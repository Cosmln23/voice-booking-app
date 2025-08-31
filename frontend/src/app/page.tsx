'use client'

import { useState } from 'react'
import AppointmentsSidebar from '@/components/appointments/AppointmentsSidebar'
import AppointmentsList from '@/components/appointments/AppointmentsList'
import TodayView from '@/components/appointments/TodayView'
import UpcomingView from '@/components/appointments/UpcomingView'
import PendingView from '@/components/appointments/PendingView'
import ArchiveView from '@/components/appointments/ArchiveView'
import ClientsList from '@/components/clients/ClientsList'
import ServicesList from '@/components/services/ServicesList'
import StatisticsList from '@/components/statistics/StatisticsList'
import AgentControlCenter from '@/components/agent/AgentControlCenter'
import SettingsPanel from '@/components/settings/SettingsPanel'
import MobileDrawer from '@/components/layout/MobileDrawer'

type PageType = 'dashboard' | 'today' | 'upcoming' | 'pending' | 'archive' | 'clients' | 'services' | 'statistics' | 'agent' | 'settings'

export default function Dashboard() {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)
  const [selectedAppointment, setSelectedAppointment] = useState<string | null>('2')
  const [mobileView, setMobileView] = useState<'sidebar' | 'main'>('main')
  const [currentPage, setCurrentPage] = useState<PageType>('dashboard')

  const handleMobileMenuToggle = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen)
  }

  const handleMobileViewToggle = () => {
    setMobileView(mobileView === 'sidebar' ? 'main' : 'sidebar')
  }

  const handlePageChange = (page: PageType) => {
    setCurrentPage(page)
  }

  const renderMainContent = () => {
    switch (currentPage) {
      case 'dashboard':
        return (
          <AppointmentsList 
            selectedAppointment={selectedAppointment}
            onSelectAppointment={setSelectedAppointment}
            isMobile={mobileView !== 'sidebar'}
            onMobileToggle={handleMobileViewToggle}
          />
        )
      case 'today':
        return (
          <TodayView 
            isMobile={mobileView !== 'sidebar'}
            onMobileToggle={handleMobileViewToggle}
          />
        )
      case 'upcoming':
        return (
          <UpcomingView 
            isMobile={mobileView !== 'sidebar'}
            onMobileToggle={handleMobileViewToggle}
          />
        )
      case 'pending':
        return (
          <PendingView 
            isMobile={mobileView !== 'sidebar'}
            onMobileToggle={handleMobileViewToggle}
          />
        )
      case 'archive':
        return (
          <ArchiveView 
            isMobile={mobileView !== 'sidebar'}
            onMobileToggle={handleMobileViewToggle}
          />
        )
      case 'clients':
        return (
          <ClientsList 
            isMobile={mobileView !== 'sidebar'}
            onMobileToggle={handleMobileViewToggle}
          />
        )
      case 'services':
        return (
          <ServicesList 
            isMobile={mobileView !== 'sidebar'}
            onMobileToggle={handleMobileViewToggle}
          />
        )
      case 'statistics':
        return (
          <StatisticsList 
            isMobile={mobileView !== 'sidebar'}
            onMobileToggle={handleMobileViewToggle}
          />
        )
      case 'agent':
        return (
          <AgentControlCenter 
            isMobile={mobileView !== 'sidebar'}
            onMobileToggle={handleMobileViewToggle}
          />
        )
      case 'settings':
        return (
          <SettingsPanel 
            isMobile={mobileView !== 'sidebar'}
            onMobileToggle={handleMobileViewToggle}
          />
        )
      default:
        return (
          <AppointmentsList 
            selectedAppointment={selectedAppointment}
            onSelectAppointment={setSelectedAppointment}
            isMobile={mobileView !== 'sidebar'}
            onMobileToggle={handleMobileViewToggle}
          />
        )
    }
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Desktop Layout - 2 Columns */}
      <div className="hidden md:flex h-screen">
        <AppointmentsSidebar 
          currentPage={currentPage}
          onPageChange={handlePageChange}
        />
        {renderMainContent()}
      </div>

      {/* Mobile Layout - Single Screen */}
      <div className="md:hidden h-screen flex flex-col">
        {mobileView === 'sidebar' ? (
          <AppointmentsSidebar 
            isMobile={true}
            onMobileToggle={handleMobileViewToggle}
            currentPage={currentPage}
            onPageChange={handlePageChange}
          />
        ) : (
          renderMainContent()
        )}
      </div>

      <MobileDrawer 
        isOpen={isMobileMenuOpen}
        onClose={() => setIsMobileMenuOpen(false)}
      />
    </div>
  )
}