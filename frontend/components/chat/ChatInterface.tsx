/**
 * ChatInterface Component
 * Main chat orchestrator with message management, API integration, and state handling
 */

'use client';

import { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import ChatMessage from './ChatMessage';
import ConfirmationModal from './ConfirmationModal';
import { ChatMessage as ChatMessageType, ChatRequest, ConfirmationDetails } from '@/lib/types';
import { sendChatMessage, loadConversationHistory, CONVERSATION_ID_KEY } from '@/lib/chatApi';
import { getToken, clearToken } from '@/lib/auth';
import toast from 'react-hot-toast';

export default function ChatInterface() {
  const router = useRouter();

  // State
  const [messages, setMessages] = useState<ChatMessageType[]>([]);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [confirmationRequest, setConfirmationRequest] = useState<ConfirmationDetails | null>(null);
  const [inputValue, setInputValue] = useState('');

  // Refs
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const lastMessageRef = useRef<string>(''); // For retry functionality

  // Load conversation history on mount
  useEffect(() => {
    loadHistory();
  }, []);

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  /**
   * Load conversation history from localStorage and backend
   */
  const loadHistory = async () => {
    try {
      // Check if conversation_id exists in localStorage
      const storedConversationId = localStorage.getItem(CONVERSATION_ID_KEY);

      if (!storedConversationId) {
        return; // No existing conversation
      }

      setConversationId(storedConversationId);

      // Load message history from backend
      const token = getToken();
      if (!token) {
        router.push('/login');
        return;
      }

      const history = await loadConversationHistory(storedConversationId, token);
      setMessages(history);

    } catch (err) {
      if (err instanceof Error) {
        if (err.message === 'CONVERSATION_NOT_FOUND') {
          // Conversation doesn't exist - clear localStorage and start fresh
          localStorage.removeItem(CONVERSATION_ID_KEY);
          setConversationId(null);
          setMessages([]);
          return;
        }

        // Other errors - display but don't block
        console.error('Failed to load conversation history:', err);
        addSystemMessage('Failed to load conversation history. Starting fresh.');
      }
    }
  };

  /**
   * Handle sending a message
   */
  const handleSendMessage = async (text?: string) => {
    const messageText = text || inputValue.trim();

    if (!messageText || loading) return;

    // Get auth token
    const token = getToken();
    if (!token) {
      router.push('/login');
      return;
    }

    // Save message for retry
    lastMessageRef.current = messageText;

    // Add user message to UI immediately
    const userMessage: ChatMessageType = {
      id: `temp-${Date.now()}`,
      role: 'user',
      content: messageText,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setLoading(true);
    setError(null);

    try {
      // Send to backend
      const request: ChatRequest = {
        message: messageText,
        conversation_id: conversationId
      };

      const response = await sendChatMessage(request, token);

      // Save conversation_id if this is the first message
      if (!conversationId && response.conversation_id) {
        setConversationId(response.conversation_id);
        localStorage.setItem(CONVERSATION_ID_KEY, response.conversation_id);
      }

      // Check if confirmation is required
      if (response.requires_confirmation && response.confirmation_details) {
        setConfirmationRequest({
          action: response.confirmation_details.action,
          params: response.confirmation_details.params,
          prompt: response.message || 'Are you sure you want to proceed?'
        });
      } else {
        // Add assistant response
        const assistantMessage: ChatMessageType = {
          id: `assistant-${Date.now()}`,
          role: 'assistant',
          content: response.message,
          timestamp: new Date()
        };
        setMessages(prev => [...prev, assistantMessage]);
      }

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to send message');

      // Handle 401 (unauthorized) - check status code instead of string matching
      if (err instanceof Error && (err as any).status === 401) {
        clearToken();
        router.push('/login');
        return;
      }

      // Add error message to chat
      addSystemMessage(`⚠️ Error: ${err instanceof Error ? err.message : 'Unknown error'}. Click retry to try again.`);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Handle confirmation dialog actions
   */
  const handleConfirmation = async (confirmed: boolean) => {
    if (!confirmed || !confirmationRequest) {
      // User cancelled
      addSystemMessage('Action cancelled.');
      setConfirmationRequest(null);
      return;
    }

    // User confirmed - send confirm_action to backend
    const token = getToken();
    if (!token) {
      router.push('/login');
      return;
    }

    setLoading(true);
    setConfirmationRequest(null);

    try {
      const request: ChatRequest = {
        message: '', // Empty message for confirmation
        conversation_id: conversationId,
        confirm_action: {
          action: confirmationRequest.action,
          params: confirmationRequest.params
        }
      };

      const response = await sendChatMessage(request, token);

      // Add result message
      const assistantMessage: ChatMessageType = {
        id: `assistant-${Date.now()}`,
        role: 'assistant',
        content: response.message,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, assistantMessage]);

    } catch (err) {
      // Handle 401 (unauthorized)
      if (err instanceof Error && (err as any).status === 401) {
        clearToken();
        router.push('/login');
        return;
      }

      addSystemMessage(`⚠️ Error executing action: ${err instanceof Error ? err.message : 'Unknown error'}`);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Start a new conversation
   */
  const startNewConversation = () => {
    setMessages([]);
    setConversationId(null);
    localStorage.removeItem(CONVERSATION_ID_KEY);
    setError(null);
    toast.success('Started new conversation');
  };

  /**
   * Add a system message to the chat
   */
  const addSystemMessage = (content: string) => {
    const systemMessage: ChatMessageType = {
      id: `system-${Date.now()}`,
      role: 'system',
      content,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, systemMessage]);
  };

  /**
   * Retry last failed message
   */
  const handleRetry = () => {
    if (lastMessageRef.current) {
      handleSendMessage(lastMessageRef.current);
    }
  };

  return (
    <div className="flex flex-col h-full">
      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto p-4 space-y-2">
        {messages.length === 0 && (
          <div className="text-center text-gray-400 mt-8">
            <p className="text-lg mb-2">👋 Welcome to AI Task Assistant</p>
            <p className="text-sm">Ask me to create, list, update, or manage your tasks using natural language.</p>
          </div>
        )}

        {messages.map((msg) => (
          <ChatMessage
            key={msg.id}
            role={msg.role}
            content={msg.content}
            timestamp={msg.timestamp}
          />
        ))}

        {/* Show retry button if error */}
        {error && (
          <div className="flex justify-center">
            <button
              onClick={handleRetry}
              className="px-4 py-2 bg-neon-blue hover:bg-neon-blue/80 text-white rounded-lg text-sm transition-colors"
            >
              Retry
            </button>
          </div>
        )}

        {/* Loading indicator */}
        {loading && (
          <div className="flex justify-start mb-4">
            <div className="bg-cyber-surface border border-cyber-border px-4 py-3 rounded-2xl">
              <div className="flex space-x-2">
                <div className="w-2 h-2 bg-neon-blue rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                <div className="w-2 h-2 bg-neon-blue rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                <div className="w-2 h-2 bg-neon-blue rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
              </div>
            </div>
          </div>
        )}

        {/* Scroll anchor */}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="border-t border-cyber-border bg-cyber-surface/50 p-4">
        <div className="flex gap-2">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={(e) => {
              if (e.key === 'Enter' && !e.shiftKey && !loading) {
                e.preventDefault();
                handleSendMessage();
              }
            }}
            placeholder="Ask me to create, update, or manage your tasks..."
            disabled={loading}
            className="flex-1 bg-cyber-dark border border-cyber-border rounded-lg px-4 py-3 text-gray-200 placeholder-gray-500 focus:outline-none focus:border-neon-blue transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          />
          <button
            onClick={() => handleSendMessage()}
            disabled={loading || !inputValue.trim()}
            className="px-6 py-3 bg-gradient-to-r from-neon-blue to-neon-purple text-white rounded-lg font-semibold hover:opacity-90 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Send
          </button>
        </div>
      </div>

      {/* Confirmation Modal */}
      {confirmationRequest && (
        <ConfirmationModal
          isOpen={true}
          prompt={confirmationRequest.prompt}
          action={confirmationRequest.action}
          params={confirmationRequest.params}
          onConfirm={() => handleConfirmation(true)}
          onCancel={() => handleConfirmation(false)}
        />
      )}
    </div>
  );
}
