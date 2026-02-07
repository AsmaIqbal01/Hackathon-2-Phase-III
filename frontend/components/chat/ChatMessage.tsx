/**
 * ChatMessage Component
 * Displays individual messages with role-based styling
 */

import { formatDistanceToNow } from 'date-fns';

interface ChatMessageProps {
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
}

export default function ChatMessage({ role, content, timestamp }: ChatMessageProps) {
  // Format relative timestamp
  const relativeTime = formatDistanceToNow(timestamp, { addSuffix: true });

  // Role-based styling
  if (role === 'system') {
    return (
      <div className="flex justify-center my-2">
        <div className="text-gray-400 italic text-sm text-center max-w-md">
          {content}
        </div>
      </div>
    );
  }

  if (role === 'user') {
    return (
      <div className="flex justify-end mb-4">
        <div className="max-w-[70%]">
          <div className="bg-gradient-to-r from-neon-blue to-neon-purple text-white px-4 py-3 rounded-2xl rounded-tr-none shadow-lg">
            <p className="text-sm leading-relaxed">{content}</p>
          </div>
          <div className="text-xs text-gray-400 mt-1 text-right">{relativeTime}</div>
        </div>
      </div>
    );
  }

  // Assistant message
  return (
    <div className="flex justify-start mb-4">
      <div className="max-w-[70%]">
        <div className="bg-cyber-surface border border-cyber-border text-gray-200 px-4 py-3 rounded-2xl rounded-tl-none shadow-lg">
          <p className="text-sm leading-relaxed whitespace-pre-wrap">{content}</p>
        </div>
        <div className="text-xs text-gray-400 mt-1">{relativeTime}</div>
      </div>
    </div>
  );
}
