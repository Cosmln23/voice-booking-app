import { cn } from '@/lib/utils'

interface BadgeProps {
  variant: 'success' | 'warning' | 'error' | 'info' | 'neutral'
  children: React.ReactNode
  className?: string
}

const badgeVariants = {
  success: 'border-border text-primary bg-secondary/20',
  warning: 'border-border text-secondary bg-secondary/10',
  error: 'border-border text-secondary bg-secondary/10',
  info: 'border-border text-secondary bg-secondary/10',
  neutral: 'border-border text-secondary bg-secondary/10',
}

export default function Badge({ variant, children, className }: BadgeProps) {
  return (
    <span className={cn(
      'inline-flex items-center gap-1 text-[11px] px-1.5 py-0.5 rounded-2xl border',
      badgeVariants[variant],
      className
    )}>
      {children}
    </span>
  )
}