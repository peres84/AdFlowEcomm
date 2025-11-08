/**
 * Session management utilities for ProductFlow
 * Handles session ID creation, retrieval, and cleanup
 */

const SESSION_ID_KEY = 'sessionId';

/**
 * Get the current session ID from localStorage
 * @returns The session ID or null if not found
 */
export const getSessionId = (): string | null => {
  return localStorage.getItem(SESSION_ID_KEY);
};

/**
 * Set a new session ID in localStorage
 * @param sessionId The session ID to store
 */
export const setSessionId = (sessionId: string): void => {
  localStorage.setItem(SESSION_ID_KEY, sessionId);
};

/**
 * Clear the session ID from localStorage
 */
export const clearSessionId = (): void => {
  localStorage.removeItem(SESSION_ID_KEY);
};

/**
 * Check if a session ID exists
 * @returns True if session ID exists, false otherwise
 */
export const hasSessionId = (): boolean => {
  return localStorage.getItem(SESSION_ID_KEY) !== null;
};
