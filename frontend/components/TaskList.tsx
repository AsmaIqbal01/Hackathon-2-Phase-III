// T015: TaskList with cyberpunk styling, skeleton loaders, and animations

'use client'

import { AnimatePresence } from 'framer-motion'
import { Task } from '@/lib/types'
import TaskItem from './TaskItem'
import SkeletonCard from '@/components/ui/SkeletonCard'

interface TaskListProps {
  tasks: Task[]
  loading: boolean
  error: string | null
  onTaskUpdate: () => void
}

export default function TaskList({ tasks, loading, error, onTaskUpdate }: TaskListProps) {
  // Loading state with skeleton cards
  if (loading) {
    return <SkeletonCard count={3} />
  }

  // Error state with cyberpunk styling
  if (error) {
    return (
      <div className="bg-neon-red/10 border border-neon-red/30 rounded-lg p-4">
        <p className="font-heading text-neon-red font-medium uppercase tracking-wider">
          Error loading tasks
        </p>
        <p className="text-sm text-cyber-text-muted mt-1">{error}</p>
      </div>
    )
  }

  // Empty state with cyberpunk styling
  if (tasks.length === 0) {
    return (
      <div className="text-center py-8 bg-cyber-surface border border-cyber-border rounded-lg">
        <p className="text-cyber-text-muted">
          No tasks yet.{' '}
          <span className="text-neon-blue">Create your first task above!</span>
        </p>
      </div>
    )
  }

  // Task list with animated entries/exits
  return (
    <div className="space-y-3">
      <AnimatePresence mode="popLayout">
        {tasks.map((task) => (
          <TaskItem key={task.id} task={task} onUpdate={onTaskUpdate} />
        ))}
      </AnimatePresence>
    </div>
  )
}
