'use client'

import { 
  CalendarCheck, 
  Banknote, 
  Clock9, 
  Bot,
  TrendingUp,
  ArrowUpRight,
  CheckCircle,
  Clock,
  XCircle
} from 'lucide-react'
import KPICard from './KPICard'
import SparklineChart from './charts/SparklineChart'
import DonutChart from './charts/DonutChart'

export default function KPISection() {
  const revenueData = [920, 1080, 980, 1180, 1250, 1020, 0]
  
  return (
    <section className="flex md:grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-3 md:gap-4 mb-6 overflow-x-auto md:overflow-visible -mx-4 px-4 snap-x snap-mandatory">
      {/* Programări Azi */}
      <KPICard
        title="Programări Azi"
        value="14"
        timeframe="08:00–18:00"
        trend={{
          value: "+2 față de ieri",
          direction: "up",
          icon: <TrendingUp className="w-3.5 h-3.5" />
        }}
        icon={<CalendarCheck className="w-4.5 h-4.5 text-accent" />}
        chart={
          <div className="w-24 h-12">
            <div className="w-full h-full rounded-md bg-background border border-border grid place-items-center text-[10px] text-secondary">
              timeline
            </div>
          </div>
        }
      />

      {/* Venit Estimat */}
      <KPICard
        title="Venit Estimat"
        value="1.250 RON"
        subtitle="Medie: 1.180 RON"
        timeframe="azi"
        icon={<Banknote className="w-4.5 h-4.5 text-accent" />}
        chart={<SparklineChart data={revenueData} className="w-28 h-14" />}
      />

      {/* Grad de Ocupare */}
      <KPICard
        title="Grad de Ocupare"
        value="85%"
        subtitle="Sloturi ocupate"
        timeframe="azi"
        trend={{
          value: "+3% vs. săptămâna trecută",
          direction: "up",
          icon: <ArrowUpRight className="w-3.5 h-3.5" />
        }}
        icon={<Clock9 className="w-4.5 h-4.5 text-accent" />}
        chart={<DonutChart percentage={85} />}
      />

      {/* Rata de Succes AI */}
      <KPICard
        title="Rata de Succes AI"
        value="92%"
        subtitle="Programări finalizate automat"
        timeframe="ultimele 24h"
        icon={<Bot className="w-4.5 h-4.5 text-accent" />}
        chart={
          <div className="inline-flex items-center gap-2 text-xs">
            <span className="text-accent inline-flex items-center gap-1">
              <CheckCircle className="w-3.5 h-3.5" /> 46
            </span>
            <span className="text-yellow-400 inline-flex items-center gap-1">
              <Clock className="w-3.5 h-3.5" /> 3
            </span>
            <span className="text-red-400 inline-flex items-center gap-1">
              <XCircle className="w-3.5 h-3.5" /> 1
            </span>
          </div>
        }
      />
    </section>
  )
}