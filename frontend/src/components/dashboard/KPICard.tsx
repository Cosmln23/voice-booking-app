'use client'

import { cn } from '@/lib/utils'
import { ReactNode } from 'react'

interface KPICardProps {
  title: string
  value: string | number
  subtitle?: string
  trend?: {
    value: string
    direction: 'up' | 'down'
    icon: ReactNode
  }
  timeframe?: string
  icon: ReactNode
  chart?: ReactNode
  className?: string
}

export default function KPICard({
  title,
  value,
  subtitle,
  trend,
  timeframe,
  icon,
  chart,
  className
}: KPICardProps) {
  return (
    <div 
      className={cn(
        'group relative overflow-hidden rounded-lg bg-card border border-border p-4 hover:border-border-hover hover:bg-card-hover transition-colors min-w-[260px] md:min-w-0 snap-start',
        className
      )}
    >
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-2">
          <div className="p-2 rounded-md bg-accent/10 border border-accent/30">
            {icon}
          </div>
          <div className="text-sm text-secondary">{title}</div>
        </div>
        {timeframe && (
          <span className="text-xs text-secondary">{timeframe}</span>
        )}
      </div>
      
      <div className="mt-3 flex items-end justify-between">
        <div>
          <div className="text-2xl font-semibold tracking-tight text-primary">{value}</div>
          {subtitle && (
            <div className="text-xs text-secondary mt-1">{subtitle}</div>
          )}
          {trend && (
            <div className={cn(
              'text-xs mt-1 inline-flex items-center gap-1',
              trend.direction === 'up' ? 'text-accent' : 'text-red-400'
            )}>
              {trend.icon}
              {trend.value}
            </div>
          )}
        </div>
        
        {chart && (
          <div className="flex-shrink-0">
            {chart}
          </div>
        )}
      </div>
    </div>
  )
}