/**
 * Security utilities for credential management
 */

// Generate a secure encryption key for the session
export function generateSessionKey(): string {
  const crypto = require('crypto');
  return crypto.randomBytes(32).toString('hex');
}

// Validate service account JSON structure
export function validateServiceAccountJSON(jsonData: any): boolean {
  const requiredFields = [
    'type', 
    'project_id', 
    'private_key_id', 
    'private_key', 
    'client_email',
    'client_id',
    'auth_uri',
    'token_uri'
  ];
  
  // Check if all required fields are present and non-empty
  return requiredFields.every(field => 
    jsonData.hasOwnProperty(field) && 
    jsonData[field] && 
    typeof jsonData[field] === 'string' &&
    jsonData[field].trim().length > 0
  );
}

// Sanitize logs to prevent credential exposure
export function sanitizeLogData(data: any): any {
  if (typeof data === 'string') {
    // Check if it looks like a credential
    if (data.includes('-----BEGIN PRIVATE KEY-----') || 
        data.startsWith('sk-') || 
        data.startsWith('sk-or-') ||
        data.length > 100) {
      return '[REDACTED]';
    }
    return data;
  }
  
  if (typeof data === 'object' && data !== null) {
    const sanitized: any = {};
    for (const [key, value] of Object.entries(data)) {
      if (key.toLowerCase().includes('key') || 
          key.toLowerCase().includes('secret') || 
          key.toLowerCase().includes('password') ||
          key.toLowerCase().includes('token')) {
        sanitized[key] = '[REDACTED]';
      } else {
        sanitized[key] = sanitizeLogData(value);
      }
    }
    return sanitized;
  }
  
  return data;
}

// Secure credential cleanup
export function secureCleanup(credentials: Record<string, any>): void {
  // Overwrite sensitive data with random values before clearing
  for (const [key, value] of Object.entries(credentials)) {
    if (typeof value === 'string' && value.length > 0) {
      // Overwrite with random data
      const randomData = require('crypto').randomBytes(value.length).toString('hex');
      credentials[key] = randomData;
    }
  }
  
  // Clear the object
  Object.keys(credentials).forEach(key => {
    delete credentials[key];
  });
}

// Rate limiting for credential attempts
export class CredentialRateLimiter {
  private attempts: Map<string, { count: number; lastAttempt: number }> = new Map();
  private maxAttempts = 5;
  private windowMs = 15 * 60 * 1000; // 15 minutes

  isAllowed(identifier: string): boolean {
    const now = Date.now();
    const attempt = this.attempts.get(identifier);

    if (!attempt) {
      this.attempts.set(identifier, { count: 1, lastAttempt: now });
      return true;
    }

    // Reset if window has passed
    if (now - attempt.lastAttempt > this.windowMs) {
      this.attempts.set(identifier, { count: 1, lastAttempt: now });
      return true;
    }

    // Check if under limit
    if (attempt.count < this.maxAttempts) {
      attempt.count++;
      attempt.lastAttempt = now;
      return true;
    }

    return false;
  }

  reset(identifier: string): void {
    this.attempts.delete(identifier);
  }
}

// Global rate limiter instance
export const credentialRateLimiter = new CredentialRateLimiter();
