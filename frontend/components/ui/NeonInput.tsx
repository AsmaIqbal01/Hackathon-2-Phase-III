// T005: Neon-styled input component with label and error states

'use client'

import { forwardRef, InputHTMLAttributes, useId } from 'react'

export interface NeonInputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string
  error?: string
}

const NeonInput = forwardRef<HTMLInputElement, NeonInputProps>(
  ({ label, error, className = '', id: providedId, ...props }, ref) => {
    const generatedId = useId()
    const id = providedId || generatedId
    const errorId = `${id}-error`

    return (
      <div className="w-full">
        {label && (
          <label
            htmlFor={id}
            className="block font-heading text-sm uppercase tracking-wider text-cyber-text-muted mb-2"
          >
            {label}
          </label>
        )}
        <input
          ref={ref}
          id={id}
          aria-invalid={error ? 'true' : 'false'}
          aria-describedby={error ? errorId : undefined}
          className={`
            w-full px-4 py-2.5 min-h-[44px]
            bg-cyber-surface
            border border-cyber-border
            text-cyber-text text-base
            placeholder:text-cyber-text-muted
            rounded-md
            transition-all duration-150 ease-out
            focus:border-neon-blue focus:shadow-glow-blue focus:outline-none
            disabled:opacity-50 disabled:cursor-not-allowed
            ${error ? 'border-neon-red shadow-glow-red' : ''}
            ${className}
          `}
          {...props}
        />
        {error && (
          <p
            id={errorId}
            className="mt-2 text-sm text-neon-red"
            role="alert"
          >
            {error}
          </p>
        )}
      </div>
    )
  }
)

NeonInput.displayName = 'NeonInput'

export default NeonInput
