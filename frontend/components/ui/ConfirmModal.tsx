// T007: Accessible confirmation modal with Framer Motion animation

'use client'

import { useEffect, useRef, useState, useCallback } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import NeonButton from './NeonButton'

export interface ConfirmModalProps {
  isOpen: boolean
  title: string
  description: string
  confirmLabel?: string
  cancelLabel?: string
  onConfirm: () => void
  onCancel: () => void
  variant?: 'danger' | 'warning'
}

export default function ConfirmModal({
  isOpen,
  title,
  description,
  confirmLabel = 'Confirm',
  cancelLabel = 'Cancel',
  onConfirm,
  onCancel,
  variant = 'danger',
}: ConfirmModalProps) {
  const [prefersReducedMotion, setPrefersReducedMotion] = useState(false)
  const cancelButtonRef = useRef<HTMLButtonElement>(null)
  const confirmButtonRef = useRef<HTMLButtonElement>(null)
  const previousActiveElement = useRef<Element | null>(null)

  // Check for reduced motion preference
  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)')
    setPrefersReducedMotion(mediaQuery.matches)

    const handleChange = (e: MediaQueryListEvent) => {
      setPrefersReducedMotion(e.matches)
    }

    mediaQuery.addEventListener('change', handleChange)
    return () => mediaQuery.removeEventListener('change', handleChange)
  }, [])

  // Store previously focused element and focus first button on open
  useEffect(() => {
    if (isOpen) {
      previousActiveElement.current = document.activeElement
      // Small delay to ensure modal is rendered
      setTimeout(() => {
        cancelButtonRef.current?.focus()
      }, 50)
    } else {
      // Return focus to previous element on close
      if (previousActiveElement.current instanceof HTMLElement) {
        previousActiveElement.current.focus()
      }
    }
  }, [isOpen])

  // Handle escape key
  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onCancel()
      }

      // Focus trap: Tab and Shift+Tab cycle between buttons
      if (e.key === 'Tab') {
        const focusableElements = [cancelButtonRef.current, confirmButtonRef.current].filter(
          Boolean
        ) as HTMLButtonElement[]

        const firstElement = focusableElements[0]
        const lastElement = focusableElements[focusableElements.length - 1]

        if (e.shiftKey) {
          // Shift+Tab: if on first element, go to last
          if (document.activeElement === firstElement) {
            e.preventDefault()
            lastElement?.focus()
          }
        } else {
          // Tab: if on last element, go to first
          if (document.activeElement === lastElement) {
            e.preventDefault()
            firstElement?.focus()
          }
        }
      }
    },
    [onCancel]
  )

  useEffect(() => {
    if (isOpen) {
      document.addEventListener('keydown', handleKeyDown)
      // Prevent body scroll when modal is open
      document.body.style.overflow = 'hidden'
    }

    return () => {
      document.removeEventListener('keydown', handleKeyDown)
      document.body.style.overflow = ''
    }
  }, [isOpen, handleKeyDown])

  // Handle backdrop click
  const handleBackdropClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      onCancel()
    }
  }

  const confirmButtonVariant = variant === 'danger' ? 'danger' : 'secondary'

  // Animation variants
  const backdropVariants = {
    hidden: { opacity: 0 },
    visible: { opacity: 1 },
  }

  const modalVariants = {
    hidden: { opacity: 0, scale: 0.95 },
    visible: { opacity: 1, scale: 1 },
  }

  const transition = prefersReducedMotion
    ? { duration: 0 }
    : { duration: 0.2, ease: 'easeOut' as const }

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          className="fixed inset-0 z-50 flex items-center justify-center p-4"
          initial="hidden"
          animate="visible"
          exit="hidden"
          variants={backdropVariants}
          transition={transition}
          onClick={handleBackdropClick}
          role="presentation"
        >
          {/* Backdrop */}
          <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" />

          {/* Modal */}
          <motion.div
            role="dialog"
            aria-modal="true"
            aria-labelledby="modal-title"
            aria-describedby="modal-description"
            variants={modalVariants}
            transition={transition}
            className="relative bg-cyber-surface border border-cyber-border rounded-lg p-6 max-w-md w-full shadow-2xl"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Neon border glow effect */}
            <div
              className="absolute inset-0 rounded-lg pointer-events-none"
              style={{
                boxShadow:
                  variant === 'danger'
                    ? '0 0 30px rgba(255, 51, 85, 0.2), inset 0 0 30px rgba(255, 51, 85, 0.05)'
                    : '0 0 30px rgba(255, 204, 0, 0.2), inset 0 0 30px rgba(255, 204, 0, 0.05)',
              }}
            />

            {/* Content */}
            <div className="relative">
              <h2
                id="modal-title"
                className="font-heading text-xl font-bold text-cyber-text mb-2"
              >
                {title}
              </h2>
              <p
                id="modal-description"
                className="text-cyber-text-muted mb-6"
              >
                {description}
              </p>

              {/* Actions */}
              <div className="flex items-center justify-end gap-3">
                <NeonButton
                  ref={cancelButtonRef}
                  variant="ghost"
                  onClick={onCancel}
                >
                  {cancelLabel}
                </NeonButton>
                <NeonButton
                  ref={confirmButtonRef}
                  variant={confirmButtonVariant}
                  onClick={onConfirm}
                >
                  {confirmLabel}
                </NeonButton>
              </div>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}
