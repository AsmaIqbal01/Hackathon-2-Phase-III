// T007: API client with JWT header injection and 401 handling

import { getToken, clearToken } from './auth';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

export interface ApiClientOptions extends RequestInit {
  requiresAuth?: boolean;
}

/**
 * Centralized API client with JWT injection and error handling
 */
export async function apiClient<T>(
  endpoint: string,
  options: ApiClientOptions = {}
): Promise<T> {
  const { requiresAuth = true, ...fetchOptions } = options;

  // Build headers
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(fetchOptions.headers as Record<string, string>),
  };

  // Inject JWT token if required
  if (requiresAuth) {
    const token = getToken();
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
  }

  // Build full URL
  const url = `${API_BASE_URL}${endpoint}`;

  // Log API request (no sensitive data)
  console.log(`[API] ${fetchOptions.method || 'GET'} ${endpoint}`);

  // Make request
  const response = await fetch(url, {
    ...fetchOptions,
    headers,
  });

  // Handle 401 Unauthorized - redirect to login
  if (response.status === 401) {
    console.log(`[API] Unauthorized access to ${endpoint} - redirecting to login`);
    clearToken();
    if (typeof window !== 'undefined') {
      window.location.href = '/login';
    }
    throw new Error('Unauthorized');
  }

  // Handle non-OK responses
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({
      detail: `API error: ${response.status}`,
    }));

    // FastAPI returns errors in { detail: { error: { code, message } } } format
    // or sometimes just { detail: "message" }
    let errorMessage: string;
    if (typeof errorData.detail === 'object' && errorData.detail?.error) {
      errorMessage = errorData.detail.error.message || `API error: ${response.status}`;
    } else if (typeof errorData.detail === 'string') {
      errorMessage = errorData.detail;
    } else {
      errorMessage = errorData.error?.message || `API error: ${response.status}`;
    }

    console.error(`[API] Error ${response.status} on ${endpoint}: ${errorMessage}`);
    throw new Error(errorMessage);
  }

  // Log successful response
  console.log(`[API] Success ${response.status} on ${endpoint}`);

  // Handle 204 No Content
  if (response.status === 204) {
    return {} as T;
  }

  // Parse and return JSON
  return response.json();
}
