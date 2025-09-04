'use client'

import { ReactNode } from 'react'

interface HorizontalScrollerProps {
  children: ReactNode
  className?: string
  showGradient?: boolean
}

export default function HorizontalScroller({ 
  children, 
  className = '', 
  showGradient = true 
}: HorizontalScrollerProps) {
  return (
    <div className="relative">
      <div
        className={`
          sm:hidden
          -mx-4 px-4 pb-2
          flex flex-nowrap gap-3
          overflow-x-auto snap-x snap-mandatory
          [scrollbar-width:none] [-ms-overflow-style:none]
          ${className}
        `}
        style={{ WebkitOverflowScrolling: 'touch' }}
        aria-label="Listă orizontală"
      >
        <style jsx>{`
          div::-webkit-scrollbar { 
            display: none; 
          }
        `}</style>
        {children}
      </div>
      
      {/* Gradient hint pentru scroll */}
      {showGradient && (
        <div className="pointer-events-none absolute inset-y-0 right-0 w-8 bg-gradient-to-l from-background to-transparent sm:hidden" />
      )}
    </div>
  )
}