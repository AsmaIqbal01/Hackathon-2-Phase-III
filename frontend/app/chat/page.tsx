/**
 * Chat Page
 * AI-powered conversational task management interface
 */

'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { isAuthenticated, clearToken } from '@/lib/auth';
import ChatInterface from '@/components/chat/ChatInterface';
import toast from 'react-hot-toast';

export default function ChatPage() {
  const router = useRouter();
  const [isClient, setIsClient] = useState(false);

  // Auth check
  useEffect(() => {
    setIsClient(true);
    if (!isAuthenticated()) {
      router.push('/login');
    }
  }, [router]);

  // Handle logout
  const handleLogout = () => {
    clearToken();
    toast.success('Logged out successfully');
    router.push('/login');
  };

  // Handle new chat
  const handleNewChat = () => {
    // This will be called via ref or context
    // For now, we'll trigger a page refresh to reset state
    localStorage.removeItem('phase3_conversation_id');
    window.location.reload();
  };

  if (!isClient || !isAuthenticated()) {
    return (
      <div className="min-h-screen bg-cyber-dark flex items-center justify-center">
        <div className="text-gray-400">Loading...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-cyber-dark flex flex-col">
      {/* Header */}
      <div className="bg-cyber-surface/80 backdrop-blur-md border-b border-cyber-border">
        <div className="max-w-5xl mx-auto px-4 py-4 flex items-center justify-between">
          <h1 className="font-heading text-2xl font-bold text-neon-blue uppercase tracking-wider text-glow-blue">
            AI Task Assistant
          </h1>
          <div className="flex gap-3">
            <button
              onClick={handleNewChat}
              className="px-4 py-2 bg-cyber-surface hover:bg-cyber-surface/70 border border-cyber-border text-gray-200 rounded-lg text-sm transition-colors"
            >
              New Chat
            </button>
            <button
              onClick={handleLogout}
              className="px-4 py-2 bg-red-600/20 hover:bg-red-600/30 border border-red-600/50 text-red-400 rounded-lg text-sm transition-colors"
            >
              Logout
            </button>
          </div>
        </div>
      </div>

      {/* Chat Interface */}
      <div className="flex-1 max-w-5xl w-full mx-auto">
        <div className="h-[calc(100vh-80px)]">
          <ChatInterface />
        </div>
      </div>

      {/* Background effect (optional) */}
      <div className="fixed inset-0 pointer-events-none -z-10">
        <div
          className="absolute top-0 left-1/4 w-96 h-96 bg-neon-blue/5 rounded-full blur-3xl"
          style={{ animation: 'pulse 4s ease-in-out infinite' }}
        />
        <div
          className="absolute bottom-0 right-1/4 w-96 h-96 bg-neon-purple/5 rounded-full blur-3xl"
          style={{ animation: 'pulse 4s ease-in-out infinite 2s' }}
        />
      </div>
    </div>
  );
}
