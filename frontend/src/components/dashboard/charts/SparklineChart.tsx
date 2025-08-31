'use client'

import { useEffect, useRef } from 'react'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  LineController,
  Filler,
  ChartOptions
} from 'chart.js'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, LineController, Filler)

interface SparklineChartProps {
  data: number[]
  labels?: string[]
  className?: string
}

export default function SparklineChart({ 
  data, 
  labels = ['L', 'Ma', 'Mi', 'J', 'V', 'S', 'D'],
  className = "w-24 h-12"
}: SparklineChartProps) {
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

    const options: ChartOptions<'line'> = {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: { enabled: false }
      },
      scales: {
        x: { display: false, grid: { display: false } },
        y: { display: false, grid: { display: false } }
      },
      elements: {
        line: { borderWidth: 2 },
        point: { radius: 0 }
      }
    }

    chartRef.current = new ChartJS(ctx, {
      type: 'line',
      data: {
        labels,
        datasets: [{
          data,
          borderColor: '#ffffff',
          backgroundColor: 'rgba(255,255,255,0.1)',
          tension: 0.4,
          fill: true
        }]
      },
      options
    })

    return () => {
      if (chartRef.current) {
        chartRef.current.destroy()
      }
    }
  }, [data, labels])

  return (
    <div className={className}>
      <div className="w-full h-full rounded-md bg-background border border-border p-1.5">
        <canvas ref={canvasRef} />
      </div>
    </div>
  )
}