// T006: Auth helpers for token management

import { CONVERSATION_ID_KEY } from './chatApi';

const TOKEN_KEY = 'auth_token';
const USER_KEY = 'user_info';

/**
 * Get JWT token from localStorage
 */
export function getToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem(TOKEN_KEY);
}

/**
 * Store JWT token in localStorage
 */
export function setToken(token: string): void {
  if (typeof window === 'undefined') return;
  localStorage.setItem(TOKEN_KEY, token);
}

/**
 * Store user info in localStorage
 */
export function setUserInfo(email: string, userId: string): void {
  if (typeof window === 'undefined') return;
  localStorage.setItem(USER_KEY, JSON.stringify({ email, userId }));
}

/**
 * Get user info from localStorage
 */
export function getUserInfo(): { email: string; userId: string } | null {
  if (typeof window === 'undefined') return null;
  const userInfo = localStorage.getItem(USER_KEY);
  if (!userInfo) return null;
  try {
    return JSON.parse(userInfo);
  } catch {
    return null;
  }
}

/**
 * Clear JWT token and user info from localStorage
 */
export function clearToken(): void {
  if (typeof window === 'undefined') return;
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
  localStorage.removeItem(CONVERSATION_ID_KEY);
}

/**
 * Check if user is authenticated
 */
export function isAuthenticated(): boolean {
  return getToken() !== null;
}
