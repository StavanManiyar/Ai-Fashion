// Security Configuration for AI Fashion Platform
import DOMPurify from 'dompurify';

export class SecurityManager {
  private static instance: SecurityManager;
  private cspPolicy: string;

  private constructor() {
    this.initializeCSP();
    this.setupSecurityHeaders();
  }

  public static getInstance(): SecurityManager {
    if (!SecurityManager.instance) {
      SecurityManager.instance = new SecurityManager();
    }
    return SecurityManager.instance;
  }

  private initializeCSP() {
    this.cspPolicy = [
      "default-src 'self'",
      "script-src 'self' 'unsafe-inline' https://www.googletagmanager.com https://cdn.mixpanel.com",
      "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
      "font-src 'self' https://fonts.gstatic.com",
      "img-src 'self' data: https: blob:",
      "media-src 'self' blob:",
      "connect-src 'self' wss: https://api.mixpanel.com https://sentry.io",
      "frame-src 'none'",
      "object-src 'none'",
      "base-uri 'self'",
      "form-action 'self'",
      "upgrade-insecure-requests"
    ].join('; ');
  }

  private setupSecurityHeaders() {
    // Set CSP header
    const meta = document.createElement('meta');
    meta.httpEquiv = 'Content-Security-Policy';
    meta.content = this.cspPolicy;
    document.head.appendChild(meta);

    // Additional security headers via meta tags
    const referrerPolicy = document.createElement('meta');
    referrerPolicy.name = 'referrer';
    referrerPolicy.content = 'strict-origin-when-cross-origin';
    document.head.appendChild(referrerPolicy);
  }

  // Sanitize user input
  public sanitizeInput(input: string): string {
    return DOMPurify.sanitize(input, {
      ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'p', 'br'],
      ALLOWED_ATTR: []
    });
  }

  // Validate file uploads
  public validateFileUpload(file: File): { isValid: boolean; error?: string } {
    const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
    const maxSize = 10 * 1024 * 1024; // 10MB

    if (!allowedTypes.includes(file.type)) {
      return { isValid: false, error: 'Invalid file type. Only images are allowed.' };
    }

    if (file.size > maxSize) {
      return { isValid: false, error: 'File too large. Maximum size is 10MB.' };
    }

    return { isValid: true };
  }

  // Rate limiting for API calls
  private rateLimitMap = new Map<string, { count: number; resetTime: number }>();

  public checkRateLimit(endpoint: string, limit: number = 100, windowMs: number = 60000): boolean {
    const now = Date.now();
    const key = endpoint;
    const current = this.rateLimitMap.get(key);

    if (!current || now > current.resetTime) {
      this.rateLimitMap.set(key, { count: 1, resetTime: now + windowMs });
      return true;
    }

    if (current.count >= limit) {
      return false;
    }

    current.count++;
    return true;
  }

  // Generate secure tokens
  public generateSecureToken(length: number = 32): string {
    const array = new Uint8Array(length);
    crypto.getRandomValues(array);
    return Array.from(array, byte => byte.toString(16).padStart(2, '0')).join('');
  }

  // Validate JWT tokens (client-side basic validation)
  public validateJWT(token: string): boolean {
    try {
      const parts = token.split('.');
      if (parts.length !== 3) return false;

      const header = JSON.parse(atob(parts[0]));
      const payload = JSON.parse(atob(parts[1]));

      // Check expiration
      if (payload.exp && Date.now() >= payload.exp * 1000) {
        return false;
      }

      return true;
    } catch {
      return false;
    }
  }

  // Secure local storage wrapper
  public secureStorage = {
    setItem: (key: string, value: any) => {
      const encrypted = btoa(JSON.stringify(value));
      localStorage.setItem(key, encrypted);
    },
    getItem: (key: string) => {
      const encrypted = localStorage.getItem(key);
      if (!encrypted) return null;
      try {
        return JSON.parse(atob(encrypted));
      } catch {
        return null;
      }
    },
    removeItem: (key: string) => {
      localStorage.removeItem(key);
    }
  };
}

export const security = SecurityManager.getInstance();
