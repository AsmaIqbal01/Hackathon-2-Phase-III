/**
 * ConfirmationModal Component
 * Modal dialog for confirming destructive operations
 */

'use client';

import { useEffect } from 'react';

interface ConfirmationModalProps {
  isOpen: boolean;
  prompt: string;
  action: string;
  params: Record<string, any>;
  onConfirm: () => void;
  onCancel: () => void;
}

export default function ConfirmationModal({
  isOpen,
  prompt,
  action,
  params,
  onConfirm,
  onCancel
}: ConfirmationModalProps) {
  // Handle Escape key
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onCancel();
      }
    };

    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [isOpen, onCancel]);

  // Focus trap and body scroll lock
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }

    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center"
      onClick={onCancel}
    >
      {/* Overlay */}
      <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" />

      {/* Dialog */}
      <div
        className="relative bg-cyber-surface border border-cyber-border rounded-lg p-6 max-w-md w-full mx-4 shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Title */}
        <h3 className="text-xl font-bold text-neon-blue mb-4">
          Confirm Action
        </h3>

        {/* Prompt */}
        <p className="text-gray-200 mb-4">{prompt}</p>

        {/* Action Details */}
        <div className="bg-cyber-dark/50 border border-cyber-border rounded p-3 mb-6">
          <p className="text-sm text-gray-400 mb-1">Action:</p>
          <p className="text-sm text-white font-mono">{action}</p>
          {params && Object.keys(params).length > 0 && (
            <>
              <p className="text-sm text-gray-400 mt-2 mb-1">Parameters:</p>
              <p className="text-xs text-gray-300 font-mono">
                {JSON.stringify(params, null, 2)}
              </p>
            </>
          )}
        </div>

        {/* Buttons */}
        <div className="flex gap-3 justify-end">
          <button
            onClick={onCancel}
            className="px-4 py-2 bg-gray-600 hover:bg-gray-500 text-white rounded-lg transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={onConfirm}
            className="px-4 py-2 bg-red-600 hover:bg-red-500 text-white rounded-lg transition-colors font-semibold"
          >
            Confirm
          </button>
        </div>
      </div>
    </div>
  );
}
