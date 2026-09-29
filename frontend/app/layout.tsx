import type { Metadata } from 'next'
import { Inter } from 'next/font/google'

import './globals.css'
import { AppShell } from '@/components/layout'

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-sans',
})

export const metadata: Metadata = {
  title: 'BrokerOS - Sales Operations Platform',
  description: 'Professional B2B sales operations platform for insurance and consortium businesses',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="dark" suppressHydrationWarning>
      <body className={`${inter.variable} font-sans antialiased`}>
        <AppShell>{children}</AppShell>
      </body>
    </html>
  )
}
