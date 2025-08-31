'use client'

import { useEffect, useRef } from 'react'
import {
  Chart as ChartJS,
  ArcElement,
  DoughnutController,
  ChartOptions
} from 'chart.js'

ChartJS.register(ArcElement, DoughnutController)

interface DonutChartProps {
  percentage: number
  className?: string
}

export default function DonutChart({ 
  percentage, 
  className = "w-16 h-16" 
}: DonutChartProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const chartRef = useRef<ChartJS | null>(null)

  useEffect(() => {
    if (!canvasRef.current) return

    const ctx = canvasRef.current.getContext('2d')
    if (!ctx) return

    // Destroy existing chart
    if (chartRef.current) {
      chartRef.current.destroy()
    }

    const options: ChartOptions<'doughnut'> = {
      responsive: true,
      maintainAspectRatio: false,
      cutout: '70%',
      plugins: {
        legend: { display: false },
        tooltip: { enabled: false }
      }
    }

    chartRef.current = new ChartJS(ctx, {
      type: 'doughnut',
      data: {
        labels: ['Ocupat', 'Liber'],
        datasets: [{
          data: [percentage, 100 - percentage],
          backgroundColor: ['#ffffff', 'rgba(160,160,160,0.1)'],
          borderWidth: 0
        }]
      },
      options
    })

    return () => {
      if (chartRef.current) {
        chartRef.current.destroy()
      }
    }
  }, [percentage])

  return (
    <div className={className}>
      <div className="w-full h-full rounded-full bg-background border border-border grid place-items-center">
        <div className="w-14 h-14">
          <canvas ref={canvasRef} />
        </div>
      </div>
    </div>
  )
}