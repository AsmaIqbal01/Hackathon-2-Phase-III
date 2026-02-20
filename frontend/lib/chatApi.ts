/**
 * Chat API client for backend communication
 * Handles chat messages, conversation history, and conversation management
 */

import { ChatRequest, ChatResponse, ChatMessage, ApiError } from './types';
export { ApiError };

// Constants - use same env var as api.ts
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || (
  typeof window !== 'undefined' && window.location.hostname !== 'localhost'
    ? 'https://hackathon-2-phase-iii.onrender.com/api'
    : 'http://localhost:8000/api'
);
export const CONVERSATION_ID_KEY = 'phase3_conversation_id';

/**
 * Send a chat message to the backend
 */
export async function sendChatMessage(
  request: ChatRequest,
  token: string
): Promise<ChatResponse> {
  const response = await fetch(`${API_BASE_URL}/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify(request)
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({
      error: { code: response.status, message: 'Chat request failed' }
    }));
    // Backend returns: { error: { code: number, message: string } }
    const errorMessage = error.error?.message || error.detail || `HTTP ${response.status}: ${response.statusText}`;
    throw new ApiError(errorMessage, response.status);
  }

  return response.json();
}

/**
 * Load conversation history from backend
 */
export async function loadConversationHistory(
  conversationId: string,
  token: string
): Promise<ChatMessage[]> {
  const response = await fetch(
    `${API_BASE_URL}/chat/conversations/${conversationId}/messages`,
    {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    }
  );

  if (!response.ok) {
    if (response.status === 404) {
      throw new ApiError('CONVERSATION_NOT_FOUND', 404);
    }
    const error = await response.json().catch(() => ({
      error: { code: response.status, message: 'Failed to load conversation history' }
    }));
    const errorMessage = error.error?.message || error.detail || `Failed to load conversation history: ${response.statusText}`;
    throw new ApiError(errorMessage, response.status);
  }

  const messages = await response.json();

  // Convert backend message format to frontend format
  return messages.map((msg: any) => ({
    id: msg.id,
    role: msg.role,
    content: msg.content,
    timestamp: new Date(msg.created_at)
  }));
}

/**
 * Delete a conversation
 */
export async function deleteConversation(
  conversationId: string,
  token: string
): Promise<void> {
  const response = await fetch(
    `${API_BASE_URL}/chat/conversations/${conversationId}`,
    {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    }
  );

  if (!response.ok) {
    const error = await response.json().catch(() => ({
      error: { code: response.status, message: 'Failed to delete conversation' }
    }));
    const errorMessage = error.error?.message || error.message || `HTTP ${response.status}: ${response.statusText}`;

    throw new ApiError(errorMessage, response.status);
  }
}
