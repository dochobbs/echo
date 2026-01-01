/**
 * Error display component for Echo widget
 */

import { AlertCircle, RefreshCw, X } from 'lucide-react';

interface EchoErrorProps {
  message: string;
  onRetry?: () => void;
  onDismiss?: () => void;
}

export function EchoError({ message, onRetry, onDismiss }: EchoErrorProps) {
  return (
    <div className="echo-error">
      <div className="echo-error-content">
        <AlertCircle size={16} />
        <span>{message}</span>
      </div>
      <div className="echo-error-actions">
        {onRetry && (
          <button
            className="echo-error-btn"
            onClick={onRetry}
            title="Try again"
          >
            <RefreshCw size={14} />
          </button>
        )}
        {onDismiss && (
          <button
            className="echo-error-btn"
            onClick={onDismiss}
            title="Dismiss"
          >
            <X size={14} />
          </button>
        )}
      </div>
    </div>
  );
}

/**
 * Parse API errors into user-friendly messages
 */
export function parseError(error: unknown): string {
  if (error instanceof Error) {
    const msg = error.message.toLowerCase();

    if (msg.includes('failed to fetch') || msg.includes('network')) {
      return 'Unable to connect. Check your internet connection.';
    }
    if (msg.includes('timeout')) {
      return 'Request timed out. Please try again.';
    }
    if (msg.includes('401') || msg.includes('unauthorized')) {
      return 'Authentication error. Please refresh the page.';
    }
    if (msg.includes('403') || msg.includes('forbidden')) {
      return 'Access denied.';
    }
    if (msg.includes('404')) {
      return 'Service not found. The API may be unavailable.';
    }
    if (msg.includes('429')) {
      return 'Too many requests. Please wait a moment.';
    }
    if (msg.includes('500') || msg.includes('502') || msg.includes('503')) {
      return 'Server error. Please try again later.';
    }

    return error.message;
  }

  return 'Something went wrong. Please try again.';
}
