// T009: Home redirect page with cyberpunk styling

'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { isAuthenticated } from '@/lib/auth'
import PageTransition from '@/components/ui/PageTransition'

export default function Home() {
  const router = useRouter()

  useEffect(() => {
    if (isAuthenticated()) {
      router.push('/dashboard')
    } else {
      router.push('/login')
    }
  }, [router])

  return (
    <PageTransition>
      <div className="flex min-h-screen items-center justify-center">
        {/* Neon spinner */}
        <div className="flex flex-col items-center gap-4">
          <div
            className="w-10 h-10 border-2 border-neon-blue border-t-transparent rounded-full animate-spin"
            style={{
              boxShadow: '0 0 15px rgba(0, 212, 255, 0.5)',
            }}
          />
          <p className="text-cyber-text-muted font-heading text-sm uppercase tracking-wider">
            Initializing...
          </p>
        </div>
      </div>
    </PageTransition>
  )
}
