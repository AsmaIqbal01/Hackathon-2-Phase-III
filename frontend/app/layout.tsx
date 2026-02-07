// T002: Root layout with cyberpunk fonts and toast provider

import type { Metadata } from 'next'
import { Orbitron, Rajdhani } from 'next/font/google'
import { Toaster } from 'react-hot-toast'
import './globals.css'

// Load Orbitron for headings (futuristic, geometric)
const orbitron = Orbitron({
  subsets: ['latin'],
  variable: '--font-heading',
  display: 'swap',
  weight: ['400', '500', '600', '700', '800', '900'],
})

// Load Rajdhani for body text (readable, futuristic)
const rajdhani = Rajdhani({
  subsets: ['latin'],
  variable: '--font-body',
  display: 'swap',
  weight: ['300', '400', '500', '600', '700'],
})

export const metadata: Metadata = {
  title: 'Todo App | Cyberpunk Edition',
  description: 'A full-stack multi-user todo application with a cyberpunk aesthetic',
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en" className={`${orbitron.variable} ${rajdhani.variable}`}>
      <body className="min-h-screen bg-cyber-bg text-cyber-text font-body antialiased">
        {children}
        <Toaster
          position="top-right"
          gutter={12}
          containerStyle={{
            top: 20,
            right: 20,
          }}
          toastOptions={{
            duration: 3000,
            style: {
              background: '#12121a',
              color: '#e0e0ff',
              border: '1px solid #2a2a3e',
              borderRadius: '8px',
              padding: '12px 16px',
              fontSize: '14px',
              fontFamily: 'var(--font-body)',
            },
            success: {
              style: {
                borderColor: 'rgba(0, 255, 136, 0.5)',
                boxShadow: '0 0 15px rgba(0, 255, 136, 0.2)',
              },
              iconTheme: {
                primary: '#00ff88',
                secondary: '#12121a',
              },
            },
            error: {
              style: {
                borderColor: 'rgba(255, 51, 85, 0.5)',
                boxShadow: '0 0 15px rgba(255, 51, 85, 0.2)',
              },
              iconTheme: {
                primary: '#ff3355',
                secondary: '#12121a',
              },
            },
          }}
        />
      </body>
    </html>
  )
}
