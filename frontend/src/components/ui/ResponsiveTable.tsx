'use client'

import { ReactNode } from 'react'
import HorizontalScroller from './HorizontalScroller'

interface Column {
  key: string
  label: string
  minWidth: string  // ex: "120px"
  className?: string
  hideOnMobile?: boolean
}

interface ResponsiveTableProps {
  columns: Column[]
  children: ReactNode
  className?: string
  mobileMinWidth?: string // Total minimum width for mobile scroll
}

export default function ResponsiveTable({ 
  columns, 
  children, 
  className = '',
  mobileMinWidth = '800px'
}: ResponsiveTableProps) {
  return (
    <div className={`bg-background rounded-2xl border border-border overflow-hidden ${className}`}>
      {/* Desktop Table */}
      <div className="hidden lg:block">
        <div className="grid gap-4 p-4 border-b border-border text-xs font-semibold text-secondary uppercase tracking-wider"
             style={{ gridTemplateColumns: columns.map(col => col.minWidth || 'minmax(0, 1fr)').join(' ') }}>
          {columns.map((col) => (
            <div key={col.key} className={col.className}>
              {col.label}
            </div>
          ))}
        </div>
        <div className="divide-y divide-border">
          {children}
        </div>
      </div>

      {/* Mobile Horizontal Scroll */}
      <div className="lg:hidden">
        <HorizontalScroller>
          <div style={{ minWidth: mobileMinWidth }}>
            {/* Mobile Header */}
            <div className="flex border-b border-border bg-card">
              {columns
                .filter(col => !col.hideOnMobile)
                .map((col) => (
                  <div 
                    key={col.key} 
                    className={`px-3 py-3 text-xs font-semibold text-secondary uppercase tracking-wider ${col.className}`}
                    style={{ minWidth: col.minWidth }}
                  >
                    {col.label}
                  </div>
                ))}
            </div>
            
            {/* Mobile Body */}
            <div className="divide-y divide-border">
              {children}
            </div>
          </div>
        </HorizontalScroller>
      </div>
    </div>
  )
}

// Helper component for table rows
export function ResponsiveTableRow({ 
  columns, 
  children, 
  className = '' 
}: { 
  columns: Column[]
  children: ReactNode
  className?: string 
}) {
  return (
    <>
      {/* Desktop Row */}
      <div className={`hidden lg:grid gap-4 p-4 hover:bg-card-hover transition-colors ${className}`}
           style={{ gridTemplateColumns: columns.map(col => col.minWidth || 'minmax(0, 1fr)').join(' ') }}>
        {children}
      </div>
      
      {/* Mobile Row */}
      <div className={`lg:hidden flex hover:bg-card-hover transition-colors ${className}`}>
        {children}
      </div>
    </>
  )
}

// Helper component for table cells
export function ResponsiveTableCell({ 
  column, 
  children, 
  className = '' 
}: { 
  column: Column
  children: ReactNode
  className?: string 
}) {
  if (column.hideOnMobile) {
    return (
      <div className={`hidden lg:block ${column.className} ${className}`}>
        {children}
      </div>
    )
  }

  return (
    <div 
      className={`px-3 py-3 ${column.className} ${className}`}
      style={{ minWidth: column.minWidth }}
    >
      {children}
    </div>
  )
}