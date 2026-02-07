// T006: Skeleton card loader with shimmer animation

interface SkeletonCardProps {
  count?: number
}

export default function SkeletonCard({ count = 3 }: SkeletonCardProps) {
  return (
    <div className="space-y-3">
      {Array.from({ length: count }).map((_, index) => (
        <div
          key={index}
          className="bg-cyber-surface border border-cyber-border rounded-lg p-4"
          role="status"
          aria-label="Loading..."
        >
          <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-3">
            {/* Left side: Title, description, badges */}
            <div className="flex-1 space-y-3">
              {/* Title placeholder */}
              <div className="h-5 w-3/5 rounded shimmer" />

              {/* Description placeholder */}
              <div className="h-4 w-2/5 rounded shimmer" />

              {/* Badge and priority placeholders */}
              <div className="flex items-center gap-2">
                <div className="h-6 w-20 rounded shimmer" />
                <div className="h-4 w-24 rounded shimmer" />
              </div>
            </div>

            {/* Right side: Action buttons */}
            <div className="flex items-center gap-2">
              <div className="h-8 w-20 rounded shimmer" />
              <div className="h-8 w-16 rounded shimmer" />
            </div>
          </div>
        </div>
      ))}
      <span className="sr-only">Loading tasks...</span>
    </div>
  )
}
