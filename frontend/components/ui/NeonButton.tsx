// T004: Neon-styled button component with variants

'use client'

import { forwardRef, ButtonHTMLAttributes } from 'react'

export interface NeonButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost'
  size?: 'sm' | 'md' | 'lg'
  loading?: boolean
}

const NeonButton = forwardRef<HTMLButtonElement, NeonButtonProps>(
  ({ variant = 'primary', size = 'md', loading = false, disabled, children, className = '', ...props }, ref) => {
    // Size classes - all sizes have min-h-[44px] for touch target accessibility
    const sizeClasses = {
      sm: 'px-3 py-2 text-sm min-h-[44px]',
      md: 'px-5 py-2.5 text-base min-h-[44px]',
      lg: 'px-7 py-3 text-lg min-h-[48px]',
    }

    // Variant classes (colors, hover, focus)
    const variantClasses = {
      primary: `
        bg-cyber-surface text-neon-pink border border-neon-pink/50
        hover:bg-neon-pink/10 hover:border-neon-pink hover:shadow-glow-pink
        focus:outline-none focus:ring-2 focus:ring-neon-pink focus:ring-offset-2 focus:ring-offset-cyber-bg
      `,
      secondary: `
        bg-cyber-surface text-neon-blue border border-neon-blue/50
        hover:bg-neon-blue/10 hover:border-neon-blue hover:shadow-glow-blue
        focus:outline-none focus:ring-2 focus:ring-neon-blue focus:ring-offset-2 focus:ring-offset-cyber-bg
      `,
      danger: `
        bg-cyber-surface text-neon-red border border-neon-red/50
        hover:bg-neon-red/10 hover:border-neon-red hover:shadow-glow-red
        focus:outline-none focus:ring-2 focus:ring-neon-red focus:ring-offset-2 focus:ring-offset-cyber-bg
      `,
      ghost: `
        bg-transparent text-cyber-text border border-cyber-border
        hover:bg-cyber-surface-hover hover:border-cyber-text/30
        focus:outline-none focus:ring-2 focus:ring-cyber-text/50 focus:ring-offset-2 focus:ring-offset-cyber-bg
      `,
    }

    const isDisabled = disabled || loading

    return (
      <button
        ref={ref}
        disabled={isDisabled}
        className={`
          inline-flex items-center justify-center
          font-heading uppercase tracking-wider font-medium
          rounded-md
          transition-all duration-150 ease-out
          active:scale-[0.97]
          disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none disabled:shadow-none
          ${sizeClasses[size]}
          ${variantClasses[variant]}
          ${className}
        `}
        {...props}
      >
        {loading ? (
          <span className="flex items-center gap-2">
            <svg
              className="animate-spin h-4 w-4"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              />
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              />
            </svg>
            <span>Loading...</span>
          </span>
        ) : (
          children
        )}
      </button>
    )
  }
)

NeonButton.displayName = 'NeonButton'

export default NeonButton
