import type { Metadata } from 'next'
import '../styles/globals.css'
import SessionProvider from '../components/providers/SessionProvider'

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
      <body>
        <SessionProvider>
          {children}
        </SessionProvider>
      </body>
    </html>
  )
}