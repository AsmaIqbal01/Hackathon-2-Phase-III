// T014: TaskItem with cyberpunk styling, confirmation modal, and toasts

'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import toast from 'react-hot-toast'
import { Task, TaskStatus } from '@/lib/types'
import { apiClient } from '@/lib/api'
import NeonButton from '@/components/ui/NeonButton'
import ConfirmModal from '@/components/ui/ConfirmModal'

interface TaskItemProps {
  task: Task
  onUpdate: () => void
}

export default function TaskItem({ task, onUpdate }: TaskItemProps) {
  const [toggling, setToggling] = useState(false)
  const [deleting, setDeleting] = useState(false)
  const [showDeleteModal, setShowDeleteModal] = useState(false)

  // Toggle status
  const handleToggleStatus = async () => {
    setToggling(true)

    try {
      const newStatus: TaskStatus =
        task.status === 'completed' ? 'todo' : 'completed'

      await apiClient(`/tasks/${task.id}`, {
        method: 'PATCH',
        body: JSON.stringify({ status: newStatus }),
      })

      toast.success(newStatus === 'completed' ? 'Task completed' : 'Task reopened')
      onUpdate()
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to update task'
      toast.error(message)
    } finally {
      setToggling(false)
    }
  }

  // Execute delete (called from modal confirmation)
  const executeDelete = async () => {
    setDeleting(true)

    try {
      await apiClient(`/tasks/${task.id}`, {
        method: 'DELETE',
      })

      toast.success('Task deleted')
      onUpdate()
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to delete task'
      toast.error(message)
    } finally {
      setDeleting(false)
    }
  }

  // Status badge styles
  const getStatusStyles = () => {
    switch (task.status) {
      case 'completed':
        return 'bg-neon-green/20 text-neon-green border-neon-green/30'
      case 'in-progress':
        return 'bg-neon-yellow/20 text-neon-yellow border-neon-yellow/30'
      default:
        return 'bg-neon-purple/20 text-neon-purple border-neon-purple/30'
    }
  }

  return (
    <>
      <motion.div
        layout
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, x: -20 }}
        transition={{ duration: 0.2 }}
        className="bg-cyber-surface border border-cyber-border rounded-lg p-4 hover:border-neon-purple/50 hover:shadow-glow-purple transition-all duration-150"
      >
        <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-3">
          {/* Task content */}
          <div className="flex-1 min-w-0">
            <h3 className="font-medium text-cyber-text truncate" title={task.title}>
              {task.title}
            </h3>
            {task.description && (
              <p className="text-sm text-cyber-text-muted mt-1 line-clamp-2">
                {task.description}
              </p>
            )}
            <div className="flex flex-wrap items-center gap-2 mt-2">
              <span
                className={`inline-block px-2 py-1 text-xs rounded border ${getStatusStyles()}`}
              >
                {task.status}
              </span>
              {task.priority && (
                <span className="text-xs text-cyber-text-muted">
                  Priority: <span className="text-neon-blue">{task.priority}</span>
                </span>
              )}
            </div>
          </div>

          {/* Action buttons */}
          <div className="flex flex-wrap items-center gap-2">
            <NeonButton
              variant="secondary"
              size="sm"
              onClick={handleToggleStatus}
              loading={toggling}
              disabled={toggling || deleting}
            >
              {task.status === 'completed' ? 'Undo' : 'Complete'}
            </NeonButton>

            <NeonButton
              variant="danger"
              size="sm"
              onClick={() => setShowDeleteModal(true)}
              loading={deleting}
              disabled={toggling || deleting}
            >
              Delete
            </NeonButton>
          </div>
        </div>
      </motion.div>

      {/* Delete Confirmation Modal */}
      <ConfirmModal
        isOpen={showDeleteModal}
        title="Delete Task"
        description="Are you sure you want to delete this task? This action cannot be undone."
        confirmLabel="Delete"
        cancelLabel="Cancel"
        variant="danger"
        onConfirm={() => {
          setShowDeleteModal(false)
          executeDelete()
        }}
        onCancel={() => setShowDeleteModal(false)}
      />
    </>
  )
}
