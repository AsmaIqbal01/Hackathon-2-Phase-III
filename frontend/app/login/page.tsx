// T010: Login page with full cyberpunk styling

'use client'

import { useState, FormEvent, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import toast from 'react-hot-toast'
import { apiClient } from '@/lib/api'
import { setToken, isAuthenticated } from '@/lib/auth'
import { AuthResponse } from '@/lib/types'
import BlobBackground from '@/components/ui/BlobBackground'
import NeonInput from '@/components/ui/NeonInput'
import NeonButton from '@/components/ui/NeonButton'
import PageTransition from '@/components/ui/PageTransition'

export default function LoginPage() {
  const router = useRouter()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  // Redirect authenticated users to dashboard
  useEffect(() => {
    if (isAuthenticated()) {
      router.push('/dashboard')
    }
  }, [router])

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError(null)

    // Basic validation
    if (!email || !password) {
      const message = 'Email and password are required'
      setError(message)
      toast.error(message)
      return
    }

    setSubmitting(true)

    try {
      const response = await apiClient<AuthResponse>('/auth/login', {
        method: 'POST',
        requiresAuth: false,
        body: JSON.stringify({ email, password }),
      })

      // Store token and show success toast
      setToken(response.access_token)
      toast.success('Logged in successfully')
      router.push('/dashboard')
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Login failed'
      setError(message)
      toast.error(message)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <>
      <BlobBackground />
      <PageTransition>
        <div className="flex min-h-screen items-center justify-center px-4 sm:px-6">
          <div className="w-full max-w-md relative z-10">
            {/* Cyberpunk card */}
            <div className="bg-cyber-surface/80 backdrop-blur-md border border-cyber-border rounded-lg px-6 py-8 sm:px-8 shadow-lg">
              {/* Subtle glow effect */}
              <div
                className="absolute inset-0 rounded-lg pointer-events-none"
                style={{
                  boxShadow: '0 0 40px rgba(0, 212, 255, 0.1), inset 0 0 40px rgba(0, 212, 255, 0.02)',
                }}
              />

              <div className="relative">
                <h1 className="font-heading text-2xl font-bold text-neon-blue text-center mb-6 uppercase tracking-wider text-glow-blue">
                  Login
                </h1>

                {/* Error display */}
                {error && (
                  <div className="mb-4 p-3 bg-neon-red/10 border border-neon-red/30 text-neon-red rounded-md text-sm">
                    {error}
                  </div>
                )}

                <form onSubmit={handleSubmit} className="space-y-4">
                  <NeonInput
                    id="email"
                    type="email"
                    label="Email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    disabled={submitting}
                    required
                    placeholder="Enter your email"
                    autoComplete="email"
                  />

                  <NeonInput
                    id="password"
                    type="password"
                    label="Password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    disabled={submitting}
                    required
                    placeholder="Enter your password"
                    autoComplete="current-password"
                  />

                  <div className="pt-2">
                    <NeonButton
                      type="submit"
                      variant="primary"
                      loading={submitting}
                      disabled={submitting}
                      className="w-full"
                    >
                      {submitting ? 'Logging in...' : 'Login'}
                    </NeonButton>
                  </div>
                </form>

                <p className="mt-6 text-center text-sm text-cyber-text-muted">
                  Don&apos;t have an account?{' '}
                  <Link
                    href="/register"
                    className="text-neon-blue hover:text-neon-pink transition-colors duration-150"
                  >
                    Register
                  </Link>
                </p>
              </div>
            </div>
          </div>
        </div>
      </PageTransition>
    </>
  )
}
