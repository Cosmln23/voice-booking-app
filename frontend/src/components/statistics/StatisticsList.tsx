'use client'

import clsx from "clsx"

import { useState, useEffect } from 'react'
import { useStatistics } from '../../hooks/useStatistics'
import {
  TrendingUp,
  Calendar,
  Users,
  Clock,
  Activity,
  BarChart3,
  DollarSign,
  Target,
  ChevronDown,
  Filter,
  Download,
  Menu
} from 'lucide-react'
import HorizontalScroller from '../ui/HorizontalScroller'


type TimeInterval = 'week' | 'month' | 'year' | 'custom'

interface StatisticsListProps {
  isMobile?: boolean
  onMobileToggle?: () => void
}

export default function StatisticsList({ isMobile, onMobileToggle }: StatisticsListProps) {
  const [selectedInterval, setSelectedInterval] = useState<TimeInterval>('month')
  const [customDateFrom, setCustomDateFrom] = useState('')
  const [customDateTo, setCustomDateTo] = useState('')
  const { statistics, charts, isLoading, error, fetchStatistics, fetchCharts } = useStatistics()

  // Fetch data on mount and when interval changes
  useEffect(() => {
    fetchStatistics(selectedInterval === 'custom' ? 'month' : selectedInterval)
    fetchCharts(selectedInterval === 'custom' ? 'week' : selectedInterval)
  }, [selectedInterval, fetchStatistics, fetchCharts])

  // Fallback data when no API data is available
  const mockFinancialData = {
    revenue: [
      { date: '2024-12-01', value: 2450 },
      { date: '2024-12-08', value: 2890 },
      { date: '2024-12-15', value: 3200 },
      { date: '2024-12-22', value: 2980 },
      { date: '2024-12-29', value: 3450 }
    ],
    avgRevenuePerAppointment: 85,
    totalRevenue: 15970,
    totalAppointments: 188
  }

  const mockOperationalData = {
    occupancyRate: 78,
    heatmapData: [
      { hour: '09:00', mon: 45, tue: 67, wed: 89, thu: 78, fri: 92, sat: 56, sun: 23 },
      { hour: '10:00', mon: 67, tue: 78, wed: 95, thu: 89, fri: 98, sat: 78, sun: 34 },
      { hour: '11:00', mon: 78, tue: 89, wed: 87, thu: 92, fri: 89, sat: 89, sun: 45 },
      { hour: '12:00', mon: 56, tue: 67, wed: 78, thu: 67, fri: 78, sat: 95, sun: 67 },
      { hour: '13:00', mon: 34, tue: 45, wed: 56, thu: 45, fri: 56, sat: 87, sun: 78 },
      { hour: '14:00', mon: 67, tue: 78, wed: 89, thu: 78, fri: 89, sat: 92, sun: 56 },
      { hour: '15:00', mon: 89, tue: 92, wed: 95, thu: 89, fri: 95, sat: 78, sun: 34 },
      { hour: '16:00', mon: 78, tue: 89, wed: 87, thu: 92, fri: 87, sat: 67, sun: 23 },
      { hour: '17:00', mon: 56, tue: 67, wed: 78, thu: 67, fri: 78, sat: 45, sun: 12 },
      { hour: '18:00', mon: 45, tue: 56, wed: 67, thu: 56, fri: 67, sat: 34, sun: 8 }
    ]
  }

  const mockServicesData = [
    { name: 'Tunsoare Clasică', appointments: 45, revenue: 2025 },
    { name: 'Tunsoare + Styling', appointments: 32, revenue: 2080 },
    { name: 'Pachet Tuns + Barbă', appointments: 28, revenue: 1680 },
    { name: 'Barbă Completă', appointments: 22, revenue: 880 },
    { name: 'Tratament Păr', appointments: 18, revenue: 1530 }
  ]

  const mockClientsData = {
    newClients: 34,
    returningClients: 154,
    retentionRate: 82
  }

  const getIntervalLabel = (interval: TimeInterval) => {
    switch (interval) {
      case 'week': return 'Săptămână'
      case 'month': return 'Lună' 
      case 'year': return 'An'
      case 'custom': return 'Personalizat'
    }
  }

  const getHeatmapIntensity = (value: number) => {
    if (value >= 80) return 'bg-secondary/40'
    if (value >= 60) return 'bg-secondary/30'
    if (value >= 40) return 'bg-secondary/20'
    if (value >= 20) return 'bg-secondary/10'
    return 'bg-secondary/5'
  }

  return (
    <div className="flex-1 flex flex-col bg-card h-full">
      {/* Header */}
      <div className="p-6 lg:p-6 md:p-3 sm:p-3 border-b border-border">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3 lg:gap-3 md:gap-3 sm:gap-3">
            {isMobile && (
              <button 
                onClick={onMobileToggle}
                className="p-2 text-secondary hover:text-primary rounded-2xl hover:bg-card-hover transition-colors"
              >
                <Menu className="w-5 h-5" />
              </button>
            )}
            <TrendingUp className="w-8 h-8 lg:w-8 lg:h-8 md:w-6 md:h-6 sm:w-6 sm:h-6 text-secondary" />
            <div>
              <h1 className="text-3xl lg:text-3xl md:text-sm sm:text-sm font-bold lg:font-bold md:font-semibold sm:font-semibold text-primary">Statistici</h1>
              <p className="text-base lg:text-base md:text-sm sm:text-sm text-secondary">
                Analiza performanței pe termen lung
              </p>
            </div>
          </div>
          <button className="hidden lg:flex md:flex items-center px-4 py-2 lg:px-4 lg:py-2 md:px-3 md:py-2 sm:px-3 sm:py-2 bg-background text-secondary lg:text-secondary md:text-sm sm:text-sm border border-border rounded-2xl hover:text-primary hover:border-secondary transition-colors">
            <Download className="w-4 h-4 mr-2 lg:mr-2 md:mr-1 sm:mr-1" />
            <span className="lg:inline md:text-sm sm:text-sm">Export Raport</span>
          </button>
        </div>

        {/* Time Interval Selector */}
        <div className="flex flex-col lg:flex-row gap-4 lg:gap-4 md:gap-3 sm:gap-3">
          <div className="flex gap-2 lg:gap-2 md:gap-3 sm:gap-3">
            {(['week', 'month', 'year'] as TimeInterval[]).map((interval) => (
              <button
                key={interval}
                onClick={() => setSelectedInterval(interval)}
                className={clsx(
                  'px-4 py-2 lg:px-4 lg:py-2 md:px-3 md:py-2 sm:px-3 sm:py-2 rounded-2xl border transition-colors text-sm',
                  selectedInterval === interval
                    ? 'bg-secondary/20 text-primary border-border'
                    : 'bg-background text-secondary border-border hover:text-primary hover:border-secondary'
                )}
              >
                {getIntervalLabel(interval)}
              </button>
            ))}
            <button
              onClick={() => setSelectedInterval('custom')}
              className={clsx(
                'px-4 py-2 lg:px-4 lg:py-2 md:px-3 md:py-2 sm:px-3 sm:py-2 rounded-2xl border transition-colors text-sm',
                selectedInterval === 'custom'
                  ? 'bg-secondary/20 text-primary border-border'
                  : 'bg-background text-secondary border-border hover:text-primary hover:border-secondary'
              )}
            >
              Personalizat
            </button>
          </div>

          {selectedInterval === 'custom' && (
            <div className="flex gap-2 lg:gap-2 md:gap-3 sm:gap-3 items-center">
              <input
                type="date"
                value={customDateFrom}
                onChange={(e) => setCustomDateFrom(e.target.value)}
                className="px-3 py-2 lg:px-3 lg:py-2 md:px-3 md:py-2 sm:px-3 sm:py-2 bg-background border border-border rounded-2xl text-primary lg:text-primary md:text-sm sm:text-sm focus:outline-none focus:border-secondary transition-colors"
              />
              <span className="text-secondary">—</span>
              <input
                type="date"
                value={customDateTo}
                onChange={(e) => setCustomDateTo(e.target.value)}
                className="px-3 py-2 lg:px-3 lg:py-2 md:px-3 md:py-2 sm:px-3 sm:py-2 bg-background border border-border rounded-2xl text-primary lg:text-primary md:text-sm sm:text-sm focus:outline-none focus:border-secondary transition-colors"
              />
            </div>
          )}
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-6 lg:p-6 md:p-3 sm:p-3">
        <div className="space-y-6 lg:space-y-6 md:space-y-3 sm:space-y-3">
          {/* Financial KPIs */}
          <div className="hidden lg:grid lg:grid-cols-4 lg:gap-4">
            <div className="bg-background rounded-2xl p-4 border border-border">
              <div className="flex items-center gap-3 mb-2">
                <TrendingUp className="w-5 h-5 text-secondary" />
                <span className="text-sm text-secondary">Venituri Totale</span>
              </div>
              <div className="text-2xl font-bold text-primary">{mockFinancialData.totalRevenue.toLocaleString()} RON</div>
              <div className="text-xs text-secondary">+12% față de perioada precedentă</div>
            </div>

            <div className="bg-background rounded-2xl p-4 border border-border">
              <div className="flex items-center gap-3 mb-2">
                <Target className="w-5 h-5 text-secondary" />
                <span className="text-sm text-secondary">Venit Mediu/Programare</span>
              </div>
              <div className="text-2xl font-bold text-primary">{mockFinancialData.avgRevenuePerAppointment} RON</div>
              <div className="text-xs text-secondary">+5% față de perioada precedentă</div>
            </div>

            <div className="bg-background rounded-2xl p-4 border border-border">
              <div className="flex items-center gap-3 mb-2">
                <Calendar className="w-5 h-5 text-secondary" />
                <span className="text-sm text-secondary">Total Programări</span>
              </div>
              <div className="text-2xl font-bold text-primary">{mockFinancialData.totalAppointments}</div>
              <div className="text-xs text-secondary">+8% față de perioada precedentă</div>
            </div>

            <div className="bg-background rounded-2xl p-4 border border-border">
              <div className="flex items-center gap-3 mb-2">
                <Activity className="w-5 h-5 text-secondary" />
                <span className="text-sm text-secondary">Grad Ocupare</span>
              </div>
              <div className="text-2xl font-bold text-primary">{mockOperationalData.occupancyRate}%</div>
              <div className="text-xs text-secondary">+3% față de perioada precedentă</div>
            </div>
          </div>

          <HorizontalScroller>
            <div className="bg-background rounded-2xl p-3 lg:p-3 md:px-3 md:py-2 sm:px-3 sm:py-2 border border-border min-w-[200px] snap-start shrink-0">
              <div className="flex items-center gap-3 lg:gap-3 md:gap-3 sm:gap-3 mb-2">
                <TrendingUp className="w-5 h-5 lg:w-5 lg:h-5 md:w-4 md:h-4 sm:w-4 sm:h-4 text-secondary" />
                <span className="text-xs text-secondary">Venituri Totale</span>
              </div>
              <div className="text-lg lg:text-lg md:text-sm sm:text-sm font-bold lg:font-bold md:font-semibold sm:font-semibold text-primary">{mockFinancialData.totalRevenue.toLocaleString()} RON</div>
              <div className="text-xs text-secondary">+12% față de perioada precedentă</div>
            </div>

            <div className="bg-background rounded-2xl p-3 lg:p-3 md:px-3 md:py-2 sm:px-3 sm:py-2 border border-border min-w-[200px] snap-start shrink-0">
              <div className="flex items-center gap-3 lg:gap-3 md:gap-3 sm:gap-3 mb-2">
                <Target className="w-5 h-5 lg:w-5 lg:h-5 md:w-4 md:h-4 sm:w-4 sm:h-4 text-secondary" />
                <span className="text-xs text-secondary">Venit Mediu/Programare</span>
              </div>
              <div className="text-lg lg:text-lg md:text-sm sm:text-sm font-bold lg:font-bold md:font-semibold sm:font-semibold text-primary">{mockFinancialData.avgRevenuePerAppointment} RON</div>
              <div className="text-xs text-secondary">+5% față de perioada precedentă</div>
            </div>

            <div className="bg-background rounded-2xl p-3 lg:p-3 md:px-3 md:py-2 sm:px-3 sm:py-2 border border-border min-w-[200px] snap-start shrink-0">
              <div className="flex items-center gap-3 lg:gap-3 md:gap-3 sm:gap-3 mb-2">
                <Calendar className="w-5 h-5 lg:w-5 lg:h-5 md:w-4 md:h-4 sm:w-4 sm:h-4 text-secondary" />
                <span className="text-xs text-secondary">Total Programări</span>
              </div>
              <div className="text-lg lg:text-lg md:text-sm sm:text-sm font-bold lg:font-bold md:font-semibold sm:font-semibold text-primary">{mockFinancialData.totalAppointments}</div>
              <div className="text-xs text-secondary">+8% față de perioada precedentă</div>
            </div>

            <div className="bg-background rounded-2xl p-3 lg:p-3 md:px-3 md:py-2 sm:px-3 sm:py-2 border border-border min-w-[200px] snap-start shrink-0">
              <div className="flex items-center gap-3 lg:gap-3 md:gap-3 sm:gap-3 mb-2">
                <Activity className="w-5 h-5 lg:w-5 lg:h-5 md:w-4 md:h-4 sm:w-4 sm:h-4 text-secondary" />
                <span className="text-xs text-secondary">Grad Ocupare</span>
              </div>
              <div className="text-lg lg:text-lg md:text-sm sm:text-sm font-bold lg:font-bold md:font-semibold sm:font-semibold text-primary">{mockOperationalData.occupancyRate}%</div>
              <div className="text-xs text-secondary">+3% față de perioada precedentă</div>
            </div>
          </HorizontalScroller>

          {/* Revenue Evolution Chart */}
          <div className="bg-background rounded-2xl p-6 lg:p-6 md:p-3 sm:p-3 border border-border">
            <h3 className="font-semibold lg:font-semibold md:font-semibold sm:font-semibold text-primary lg:text-primary md:text-sm sm:text-sm mb-4 flex items-center gap-2 lg:gap-2 md:gap-3 sm:gap-3">
              <BarChart3 className="w-5 h-5 lg:w-5 lg:h-5 md:w-4 md:h-4 sm:w-4 sm:h-4" />
              Evoluția Veniturilor
            </h3>
            <div className="h-64 flex items-end justify-between gap-4">
              {mockFinancialData.revenue.map((item, index) => (
                <div key={index} className="flex-1 flex flex-col items-center">
                  <div 
                    className="w-full bg-secondary/20 rounded-t-2xl transition-all hover:bg-secondary/30"
                    style={{ height: `${(item.value / 3500) * 100}%` }}
                  ></div>
                  <div className="mt-2 text-xs text-secondary text-center">
                    {new Date(item.date).toLocaleDateString('ro-RO', { day: '2-digit', month: '2-digit' })}
                  </div>
                  <div className="text-xs font-semibold text-primary">
                    {item.value.toLocaleString()}
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Heatmap */}
            <div className="bg-background rounded-2xl p-6 border border-border">
              <h3 className="font-semibold text-primary mb-4 flex items-center gap-2">
                <Clock className="w-5 h-5" />
                Heatmap Ocupare Ore/Zile
              </h3>
              <div className="space-y-1">
                <div className="grid grid-cols-8 gap-1 text-xs text-secondary mb-2">
                  <div></div>
                  <div className="text-center">Lun</div>
                  <div className="text-center">Mar</div>
                  <div className="text-center">Mie</div>
                  <div className="text-center">Joi</div>
                  <div className="text-center">Vin</div>
                  <div className="text-center">Sâm</div>
                  <div className="text-center">Dum</div>
                </div>
                {mockOperationalData.heatmapData.map((row, index) => (
                  <div key={index} className="grid grid-cols-8 gap-1">
                    <div className="text-xs text-secondary text-right pr-2">{row.hour}</div>
                    <div className={clsx('h-6 rounded border border-border', getHeatmapIntensity(row.mon))}></div>
                    <div className={clsx('h-6 rounded border border-border', getHeatmapIntensity(row.tue))}></div>
                    <div className={clsx('h-6 rounded border border-border', getHeatmapIntensity(row.wed))}></div>
                    <div className={clsx('h-6 rounded border border-border', getHeatmapIntensity(row.thu))}></div>
                    <div className={clsx('h-6 rounded border border-border', getHeatmapIntensity(row.fri))}></div>
                    <div className={clsx('h-6 rounded border border-border', getHeatmapIntensity(row.sat))}></div>
                    <div className={clsx('h-6 rounded border border-border', getHeatmapIntensity(row.sun))}></div>
                  </div>
                ))}
              </div>
              <div className="mt-4 flex items-center gap-2 text-xs text-secondary">
                <span>Intensitate:</span>
                <div className="flex items-center gap-1">
                  <div className="w-3 h-3 bg-secondary/5 border border-border rounded"></div>
                  <span>Scăzută</span>
                </div>
                <div className="flex items-center gap-1">
                  <div className="w-3 h-3 bg-secondary/40 border border-border rounded"></div>
                  <span>Ridicată</span>
                </div>
              </div>
            </div>

            {/* Top Services */}
            <div className="bg-background rounded-2xl p-6 border border-border">
              <h3 className="font-semibold text-primary mb-4 flex items-center gap-2">
                <BarChart3 className="w-5 h-5" />
                Top 5 Servicii Solicitate
              </h3>
              <div className="space-y-4">
                {mockServicesData.map((service, index) => (
                  <div key={index} className="space-y-2">
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-primary font-medium">{service.name}</span>
                      <span className="text-xs text-secondary">{service.appointments} programări</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <div className="flex-1 bg-card rounded-full h-2 mr-3">
                        <div 
                          className="bg-secondary/30 h-2 rounded-full transition-all"
                          style={{ width: `${(service.appointments / 50) * 100}%` }}
                        ></div>
                      </div>
                      <span className="text-sm font-semibold text-primary">{service.revenue.toLocaleString()} RON</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Client Analysis */}
          <div className="bg-background rounded-2xl p-6 border border-border">
            <h3 className="font-semibold text-primary mb-4 flex items-center gap-2">
              <Users className="w-5 h-5" />
              Analiza Clienților
            </h3>
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="text-center">
                <div className="text-3xl font-bold text-primary mb-2">{mockClientsData.newClients}</div>
                <div className="text-sm text-secondary">Clienți Noi</div>
                <div className="text-xs text-secondary mt-1">Această perioadă</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-primary mb-2">{mockClientsData.returningClients}</div>
                <div className="text-sm text-secondary">Clienți Recurenți</div>
                <div className="text-xs text-secondary mt-1">Această perioadă</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-primary mb-2">{mockClientsData.retentionRate}%</div>
                <div className="text-sm text-secondary">Rata de Retenție</div>
                <div className="text-xs text-secondary mt-1">+4% față de perioada precedentă</div>
              </div>
            </div>
            
            {/* Client Retention Visualization */}
            <div className="mt-6 p-4 bg-card rounded-2xl">
              <div className="flex items-center justify-between mb-3">
                <span className="text-sm text-secondary">Distribuția Clienților</span>
                <span className="text-xs text-secondary">Total: {mockClientsData.newClients + mockClientsData.returningClients}</span>
              </div>
              <div className="flex rounded-2xl overflow-hidden h-4">
                <div 
                  className="bg-secondary/40"
                  style={{ width: `${(mockClientsData.returningClients / (mockClientsData.newClients + mockClientsData.returningClients)) * 100}%` }}
                ></div>
                <div 
                  className="bg-secondary/20"
                  style={{ width: `${(mockClientsData.newClients / (mockClientsData.newClients + mockClientsData.returningClients)) * 100}%` }}
                ></div>
              </div>
              <div className="flex justify-between mt-2 text-xs text-secondary">
                <span>Clienți Recurenți ({Math.round((mockClientsData.returningClients / (mockClientsData.newClients + mockClientsData.returningClients)) * 100)}%)</span>
                <span>Clienți Noi ({Math.round((mockClientsData.newClients / (mockClientsData.newClients + mockClientsData.returningClients)) * 100)}%)</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}