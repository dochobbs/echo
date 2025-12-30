/**
 * Main chat panel for Echo interactions
 */

import { useState, useRef, useEffect } from 'react';
import {
  GraduationCap,
  // Volume2,  // TODO: Re-enable when TTS implemented
  // VolumeX,  // TODO: Re-enable when TTS implemented
  X,
  Star,
  Trash2,
  BookOpen,
} from 'lucide-react';
import type { EchoMessage, EchoMemoryItem, EchoWidgetProps } from '../types';
// import type { EchoVoice } from '../types';  // TODO: Re-enable when TTS implemented

interface EchoPanelProps {
  position: EchoWidgetProps['position'];
  messages: EchoMessage[];
  memories: EchoMemoryItem[];
  isLoading: boolean;
  // voiceEnabled: boolean;  // TODO: Re-enable when TTS implemented
  // defaultVoice: EchoVoice;  // TODO: Re-enable when TTS implemented
  onSend: (message: string) => void;
  // onSpeak: (text: string) => void;  // TODO: Re-enable when TTS implemented
  onClose: () => void;
  // onToggleVoice: () => void;  // TODO: Re-enable when TTS implemented
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
  // voiceEnabled,  // TODO: Re-enable when TTS implemented
  onSend,
  // onSpeak,  // TODO: Re-enable when TTS implemented
  onClose,
  // onToggleVoice,  // TODO: Re-enable when TTS implemented
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
          <GraduationCap size={20} />
          <span>Echo</span>
        </div>
        <div className="echo-header-actions">
          {/* TODO: Re-enable voice toggle when TTS is fully implemented
          <button
            className="echo-header-btn"
            onClick={onToggleVoice}
            title={voiceEnabled ? 'Disable voice' : 'Enable voice'}
          >
            {voiceEnabled ? <Volume2 size={18} /> : <VolumeX size={18} />}
          </button>
          */}
          <button
            className="echo-header-btn"
            onClick={onClose}
            title="Close"
          >
            <X size={18} />
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
                <GraduationCap size={48} strokeWidth={1.5} />
                <p>Hi! I'm Echo, your AI tutor.</p>
                <p>Ask me anything about your case.</p>
              </div>
            )}

            {messages.map((msg) => (
              <div key={msg.id} className={`echo-message ${msg.role}`}>
                <div>{msg.content}</div>
                {/* TODO: Re-enable voice features when TTS is fully implemented
                {msg.role === 'echo' && (
                  <div className="echo-message-actions">
                    <button
                      className="echo-message-btn"
                      onClick={() => onSpeak(msg.content)}
                      title="Read aloud"
                    >
                      <Volume2 size={14} /> Listen
                    </button>
                  </div>
                )}
                */}
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
              <BookOpen size={48} strokeWidth={1.5} />
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
                      <Star size={14} fill={memory.starred ? 'currentColor' : 'none'} />
                    </button>
                    <button
                      className="echo-message-btn"
                      onClick={(e) => {
                        e.stopPropagation();
                        onMemoryDelete(memory.id);
                      }}
                    >
                      <Trash2 size={14} />
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
