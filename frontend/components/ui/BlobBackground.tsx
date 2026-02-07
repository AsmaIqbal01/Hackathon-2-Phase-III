// T003: Animated blob background component using GSAP

'use client'

import { useEffect, useRef } from 'react'
import gsap from 'gsap'

export default function BlobBackground() {
  const containerRef = useRef<HTMLDivElement>(null)
  const timelineRef = useRef<gsap.core.Timeline | null>(null)

  useEffect(() => {
    // Check for reduced motion preference
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches

    if (prefersReducedMotion || !containerRef.current) {
      return // Render static blobs without animation
    }

    const blobs = containerRef.current.querySelectorAll('.blob')

    // Create GSAP timeline for continuous morphing animation
    timelineRef.current = gsap.timeline()

    blobs.forEach((blob, index) => {
      // Each blob has different animation parameters for organic feel
      const duration = 8 + index * 3 // 8s, 11s, 14s
      const delay = index * 0.5

      // Animate position, scale, and border-radius
      gsap.to(blob, {
        x: () => gsap.utils.random(-100, 100),
        y: () => gsap.utils.random(-100, 100),
        scale: () => gsap.utils.random(0.8, 1.2),
        borderRadius: () => `${gsap.utils.random(40, 60)}%`,
        duration,
        delay,
        repeat: -1,
        yoyo: true,
        ease: 'sine.inOut',
      })
    })

    // Cleanup on unmount
    return () => {
      if (timelineRef.current) {
        timelineRef.current.kill()
      }
      gsap.killTweensOf('.blob')
    }
  }, [])

  return (
    <div
      ref={containerRef}
      className="fixed inset-0 z-0 pointer-events-none overflow-hidden"
      aria-hidden="true"
    >
      {/* Pink blob - top left */}
      <div
        className="blob absolute -top-32 -left-32 w-96 h-96 rounded-full opacity-40 will-change-transform"
        style={{
          background: 'radial-gradient(circle, rgba(255,45,123,0.6) 0%, rgba(255,45,123,0) 70%)',
          filter: 'blur(80px)',
        }}
      />

      {/* Blue blob - top right */}
      <div
        className="blob absolute -top-20 -right-20 w-80 h-80 rounded-full opacity-40 will-change-transform"
        style={{
          background: 'radial-gradient(circle, rgba(0,212,255,0.6) 0%, rgba(0,212,255,0) 70%)',
          filter: 'blur(80px)',
        }}
      />

      {/* Purple blob - bottom center */}
      <div
        className="blob absolute -bottom-32 left-1/2 -translate-x-1/2 w-[500px] h-[500px] rounded-full opacity-30 will-change-transform"
        style={{
          background: 'radial-gradient(circle, rgba(180,77,255,0.6) 0%, rgba(180,77,255,0) 70%)',
          filter: 'blur(100px)',
        }}
      />
    </div>
  )
}
