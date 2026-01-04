/**
 * Main chat panel for Echo interactions
 */

import { useState, useRef, useEffect } from 'react';
import {
  MessageCircleIcon,
  XIcon,
  StarIcon,
  TrashIcon,
  BookIcon,
  TriangleAlertIcon,
  RefreshIcon,
} from '../icons';
import type { EchoMessage, EchoMemoryItem, EchoWidgetProps } from '../types';

interface EchoPanelProps {
  position: EchoWidgetProps['position'];
  messages: EchoMessage[];
  memories: EchoMemoryItem[];
  isLoading: boolean;
  error: string | null;
  onSend: (message: string) => void;
  onClose: () => void;
  onRetry?: () => void;
  onClearError?: () => void;
  onMemoryClick: (memory: EchoMemoryItem) => void;
  onMemoryStar: (id: string) => void;
  onMemoryDelete: (id: string) => void;
}

type Tab = 'chat' | 'history';

export function EchoPanel({
  position = 'bottom-right',
  messages,
  memories,
  isLoading,
  error,
  onSend,
  onClose,
  onRetry,
  onClearError,
  onMemoryClick,
  onMemoryStar,
  onMemoryDelete,
}: EchoPanelProps) {
  const [input, setInput] = useState('');
  const [activeTab, setActiveTab] = useState<Tab>('chat');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim() && !isLoading) {
      onSend(input.trim());
      setInput('');
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const formatDate = (date: Date) => {
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));

    if (days === 0) return 'Today';
    if (days === 1) return 'Yesterday';
    if (days < 7) return `${days} days ago`;
    return date.toLocaleDateString();
  };

  return (
    <div className={`echo-panel ${position}`}>
      {/* Header */}
      <div className="echo-header">
        <div className="echo-header-title">
          <MessageCircleIcon size={20} />
          <span>Echo</span>
        </div>
        <div className="echo-header-actions">
          <button
            className="echo-header-btn"
            onClick={onClose}
            title="Close"
          >
            <XIcon size={18} />
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="echo-tabs">
        <button
          className={`echo-tab ${activeTab === 'chat' ? 'active' : ''}`}
          onClick={() => setActiveTab('chat')}
        >
          Chat
        </button>
        <button
          className={`echo-tab ${activeTab === 'history' ? 'active' : ''}`}
          onClick={() => setActiveTab('history')}
        >
          History ({memories.length})
        </button>
      </div>

      {/* Error Banner */}
      {error && (
        <div className="echo-error">
          <div className="echo-error-content">
            <TriangleAlertIcon size={16} />
            <span>{error}</span>
          </div>
          <div className="echo-error-actions">
            {onRetry && (
              <button
                className="echo-error-btn"
                onClick={onRetry}
                title="Try again"
              >
                <RefreshIcon size={14} />
              </button>
            )}
            {onClearError && (
              <button
                className="echo-error-btn"
                onClick={onClearError}
                title="Dismiss"
              >
                <XIcon size={14} />
              </button>
            )}
          </div>
        </div>
      )}

      {/* Content */}
      {activeTab === 'chat' ? (
        <>
          {/* Messages */}
          <div className="echo-messages">
            {messages.length === 0 && !isLoading && (
              <div className="echo-empty">
                <MessageCircleIcon size={48} strokeWidth={1.5} />
                <p>Hi! I'm Echo, your AI tutor.</p>
                <p>Ask me anything about your case.</p>
              </div>
            )}

            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`echo-message ${msg.role} ${msg.failed ? 'failed' : ''}`}
              >
                <div>{msg.content}</div>
                {msg.failed && (
                  <div className="echo-message-failed">
                    <TriangleAlertIcon size={12} />
                    <span>Failed to send</span>
                    {onRetry && (
                      <button className="echo-message-retry" onClick={onRetry}>
                        Retry
                      </button>
                    )}
                  </div>
                )}
              </div>
            ))}

            {isLoading && (
              <div className="echo-message echo">
                <div className="echo-typing">
                  <span>Echo is thinking</span>
                  <div className="echo-typing-dots">
                    <div className="echo-typing-dot" />
                    <div className="echo-typing-dot" />
                    <div className="echo-typing-dot" />
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <div className="echo-input-area">
            <form className="echo-input-wrapper" onSubmit={handleSubmit}>
              <input
                className="echo-input"
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Ask Echo a question..."
                disabled={isLoading}
                autoFocus
              />
              <button
                type="submit"
                className="echo-send-btn"
                disabled={!input.trim() || isLoading}
              >
                {isLoading ? (
                  <div className="echo-spinner" />
                ) : (
                  'Send'
                )}
              </button>
            </form>
          </div>
        </>
      ) : (
        /* History */
        <div className="echo-messages">
          {memories.length === 0 ? (
            <div className="echo-empty">
              <BookIcon size={48} strokeWidth={1.5} />
              <p>No saved interactions yet.</p>
              <p>Your conversations with Echo will appear here.</p>
            </div>
          ) : (
            memories.map((memory) => (
              <div
                key={memory.id}
                className="echo-memory-item"
                onClick={() => {
                  onMemoryClick(memory);
                  setActiveTab('chat');
                }}
              >
                <div className="echo-memory-item-query">{memory.query}</div>
                <div className="echo-memory-item-response">{memory.response}</div>
                <div className="echo-memory-item-meta">
                  <span>{formatDate(memory.timestamp)}</span>
                  <div style={{ display: 'flex', gap: '8px' }}>
                    <button
                      className="echo-message-btn"
                      onClick={(e) => {
                        e.stopPropagation();
                        onMemoryStar(memory.id);
                      }}
                    >
                      <StarIcon size={14} filled={memory.starred} />
                    </button>
                    <button
                      className="echo-message-btn"
                      onClick={(e) => {
                        e.stopPropagation();
                        onMemoryDelete(memory.id);
                      }}
                    >
                      <TrashIcon size={14} />
                    </button>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}
