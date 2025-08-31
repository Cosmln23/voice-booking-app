import type { Metadata } from 'next'
import '../styles/globals.css'

export const metadata: Metadata = {
  title: 'Tablou de Bord — Voice Booking',
  description: 'Sistem de programări automatizat cu interfață vocală',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="ro">
      <body>{children}</body>
    </html>
  )
}