// T013: TaskForm with cyberpunk styling and toast notifications

'use client'

import { useState, FormEvent } from 'react'
import toast from 'react-hot-toast'
import { apiClient } from '@/lib/api'
import { Task, CreateTaskInput } from '@/lib/types'
import NeonInput from '@/components/ui/NeonInput'
import NeonButton from '@/components/ui/NeonButton'

interface TaskFormProps {
  onTaskCreated: () => void
}

export default function TaskForm({ onTaskCreated }: TaskFormProps) {
  const [title, setTitle] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError(null)

    // Client-side validation
    if (!title.trim()) {
      const message = 'Title is required'
      setError(message)
      toast.error(message)
      return
    }

    setSubmitting(true)

    try {
      const taskInput: CreateTaskInput = {
        title: title.trim(),
      }

      await apiClient<Task>('/tasks', {
        method: 'POST',
        body: JSON.stringify(taskInput),
      })

      // Clear form and show success
      setTitle('')
      toast.success('Task created')
      onTaskCreated()
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to create task'
      setError(message)
      toast.error(message)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="mb-6">
      <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row gap-3">
        <div className="flex-1">
          <NeonInput
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Enter task title..."
            disabled={submitting}
            error={error || undefined}
          />
        </div>
        <NeonButton
          type="submit"
          variant="primary"
          loading={submitting}
          disabled={submitting}
          className="sm:w-auto w-full"
        >
          {submitting ? 'Adding...' : 'Add Task'}
        </NeonButton>
      </form>
    </div>
  )
}
