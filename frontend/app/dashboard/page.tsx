// T012: Dashboard page with full cyberpunk styling and logout confirmation

'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import toast from 'react-hot-toast'
import { apiClient } from '@/lib/api'
import { isAuthenticated, clearToken } from '@/lib/auth'
import { Task } from '@/lib/types'
import TaskList from '@/components/TaskList'
import TaskForm from '@/components/TaskForm'
import BlobBackground from '@/components/ui/BlobBackground'
import NeonButton from '@/components/ui/NeonButton'
import ConfirmModal from '@/components/ui/ConfirmModal'
import PageTransition from '@/components/ui/PageTransition'

export default function DashboardPage() {
  const router = useRouter()
  const [tasks, setTasks] = useState<Task[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [showLogoutModal, setShowLogoutModal] = useState(false)

  // Auth check - redirect unauthenticated users
  useEffect(() => {
    if (!isAuthenticated()) {
      router.push('/login')
    }
  }, [router])

  // Fetch tasks
  const fetchTasks = async () => {
    setLoading(true)
    setError(null)

    try {
      const data = await apiClient<Task[]>('/tasks', {
        method: 'GET',
      })
      setTasks(data)
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to load tasks'
      setError(message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (isAuthenticated()) {
      fetchTasks()
    }
  }, [])

  // Logout handler
  const handleLogout = () => {
    clearToken()
    toast.success('Logged out successfully')
    router.push('/login')
  }

  return (
    <>
      <BlobBackground />
      <PageTransition>
        <div className="min-h-screen">
          <div className="max-w-4xl mx-auto py-6 sm:py-8 px-4 sm:px-6 lg:px-8">
            {/* Main container */}
            <div className="bg-cyber-surface/80 backdrop-blur-md border border-cyber-border rounded-lg p-4 sm:p-6 relative z-10 shadow-lg">
              {/* Subtle glow effect */}
              <div
                className="absolute inset-0 rounded-lg pointer-events-none"
                style={{
                  boxShadow: '0 0 60px rgba(180, 77, 255, 0.08), inset 0 0 60px rgba(180, 77, 255, 0.01)',
                }}
              />

              <div className="relative">
                {/* Header */}
                <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
                  <h1 className="font-heading text-2xl font-bold text-neon-blue uppercase tracking-wider text-glow-blue">
                    My Tasks
                  </h1>
                  <NeonButton
                    variant="danger"
                    size="sm"
                    onClick={() => setShowLogoutModal(true)}
                  >
                    Logout
                  </NeonButton>
                </div>

                {/* Task Form */}
                <TaskForm onTaskCreated={fetchTasks} />

                {/* Task List */}
                <TaskList
                  tasks={tasks}
                  loading={loading}
                  error={error}
                  onTaskUpdate={fetchTasks}
                />
              </div>
            </div>
          </div>
        </div>
      </PageTransition>

      {/* Logout Confirmation Modal */}
      <ConfirmModal
        isOpen={showLogoutModal}
        title="Confirm Logout"
        description="Are you sure you want to log out? You will need to sign in again to access your tasks."
        confirmLabel="Logout"
        cancelLabel="Cancel"
        variant="danger"
        onConfirm={() => {
          setShowLogoutModal(false)
          handleLogout()
        }}
        onCancel={() => setShowLogoutModal(false)}
      />
    </>
  )
}
