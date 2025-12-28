/**
 * Main chat panel for Echo interactions
 */

import { useState, useRef, useEffect } from 'react';
import type { EchoMessage, EchoMemoryItem, EchoWidgetProps, EchoVoice } from '../types';

interface EchoPanelProps {
  position: EchoWidgetProps['position'];
  messages: EchoMessage[];
  memories: EchoMemoryItem[];
  isLoading: boolean;
  voiceEnabled: boolean;
  defaultVoice: EchoVoice;
  onSend: (message: string) => void;
  onSpeak: (text: string) => void;
  onClose: () => void;
  onToggleVoice: () => void;
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
  voiceEnabled,
  onSend,
  onSpeak,
  onClose,
  onToggleVoice,
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
  }, [messages]);

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
          <span>🎓</span>
          <span>Echo</span>
        </div>
        <div className="echo-header-actions">
          <button
            className="echo-header-btn"
            onClick={onToggleVoice}
            title={voiceEnabled ? 'Disable voice' : 'Enable voice'}
          >
            {voiceEnabled ? '🔊' : '🔇'}
          </button>
          <button
            className="echo-header-btn"
            onClick={onClose}
            title="Close"
          >
            ✕
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

      {/* Content */}
      {activeTab === 'chat' ? (
        <>
          {/* Messages */}
          <div className="echo-messages">
            {messages.length === 0 && !isLoading && (
              <div className="echo-empty">
                <div className="echo-empty-icon">🎓</div>
                <p>Hi! I'm Echo, your AI tutor.</p>
                <p>Ask me anything about your case.</p>
              </div>
            )}

            {messages.map((msg) => (
              <div key={msg.id} className={`echo-message ${msg.role}`}>
                <div>{msg.content}</div>
                {msg.role === 'echo' && (
                  <div className="echo-message-actions">
                    <button
                      className="echo-message-btn"
                      onClick={() => onSpeak(msg.content)}
                      title="Read aloud"
                    >
                      🔊 Listen
                    </button>
                  </div>
                )}
              </div>
            ))}

            {isLoading && (
              <div className="echo-message echo">
                <div className="echo-loading">
                  <div className="echo-loading-dot" />
                  <div className="echo-loading-dot" />
                  <div className="echo-loading-dot" />
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
                Send
              </button>
            </form>
          </div>
        </>
      ) : (
        /* History */
        <div className="echo-messages">
          {memories.length === 0 ? (
            <div className="echo-empty">
              <div className="echo-empty-icon">📚</div>
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
                      {memory.starred ? '⭐' : '☆'}
                    </button>
                    <button
                      className="echo-message-btn"
                      onClick={(e) => {
                        e.stopPropagation();
                        onMemoryDelete(memory.id);
                      }}
                    >
                      🗑️
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
