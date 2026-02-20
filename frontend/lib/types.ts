// T005: TypeScript types for frontend

export type TaskStatus = 'todo' | 'in-progress' | 'completed';
export type TaskPriority = 'low' | 'medium' | 'high';

export interface Task {
  id: string;           // UUID from backend
  title: string;        // required
  description?: string; // optional
  status: TaskStatus;   // required
  priority?: TaskPriority;
  tags?: string[];
  created_at: string;   // ISO 8601
  updated_at: string;   // ISO 8601
}

export interface CreateTaskInput {
  title: string;        // required
  description?: string;
  priority?: TaskPriority;
  tags?: string[];
}

export interface User {
  id: string;    // UUID
  email: string;
}

export interface AuthResponse {
  user: User;
  access_token: string;
  refresh_token: string;  // Not used in minimal scope
  token_type: string;
  expires_in: number;
}

export interface ApiErrorResponse {
  error: {
    code: number | string;
    message: string;
    details?: Record<string, unknown>;
  };
}

// Phase III: Chat Types

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
}

export interface ChatRequest {
  message: string;
  conversation_id?: string | null;
  confirm_action?: {
    action: string;
    params: Record<string, any>;
  } | null;
}

export interface ChatResponse {
  message: string;
  conversation_id: string;
  requires_confirmation: boolean;
  confirmation_details?: {
    action: string;
    params: Record<string, any>;
  } | null;
}

export interface ConfirmationDetails {
  action: string;
  params: Record<string, any>;
  prompt: string;
}

/**
 * Typed API error with HTTP status code
 */
export class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
  }
}
