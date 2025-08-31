'use client'

import { 
  Mic,
  Activity,
  Calendar,
  TrendingUp,
  Users,
  Clock
} from 'lucide-react'
import { cn } from '@/lib/utils'

export default function RightPanel() {
  return (
    <div className="w-80 bg-card border-l border-border flex flex-col">
      {/* Space for future widgets or details */}
      <div className="p-4">
        <div className="text-center text-secondary">
          <p className="text-sm">Panou pentru detalii</p>
          <p className="text-xs mt-1">Selectează o programare pentru a vedea detaliile</p>
        </div>
      </div>
    </div>
  )
}