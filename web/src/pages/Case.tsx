import { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useCase } from '../hooks/useCase';
import { DebriefCard } from '../components/DebriefCard';

export function Case() {
  const navigate = useNavigate();
  const { caseState, messages, loading, error, debrief, sendMessage, endCase, clearError } = useCase();
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const message = input.trim();
    setInput('');

    try {
      await sendMessage(message);
    } catch {
      // Error handled by hook
    }
  };

  const handleEndCase = async () => {
    try {
      await endCase();
    } catch {
      // Error handled by hook
    }
  };

  if (!caseState && !loading) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-12 text-center">
        <p className="text-gray-600">No active case. Start a new one from the home page.</p>
        <button onClick={() => navigate('/')} className="btn btn-primary mt-4">
          Go Home
        </button>
      </div>
    );
  }

  const isComplete = caseState?.phase === 'complete';

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)]">
      {/* Patient Info Header */}
      {caseState && (
        <div className="bg-white border-b border-gray-200 px-4 py-3">
          <div className="max-w-4xl mx-auto flex items-center justify-between">
            <div>
              <h2 className="font-medium text-gray-900">
                {caseState.patient.name}, {caseState.patient.age} {caseState.patient.age_unit} old {caseState.patient.sex}
              </h2>
              <p className="text-sm text-gray-500">
                {caseState.patient.condition_display} - Phase: {caseState.phase}
              </p>
            </div>
            {!isComplete && (
              <button
                onClick={handleEndCase}
                disabled={loading}
                className="btn btn-secondary text-sm"
              >
                End Case
              </button>
            )}
          </div>
        </div>
      )}

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-6">
        <div className="max-w-2xl mx-auto space-y-4">
          {messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                  msg.role === 'user'
                    ? 'bg-echo-600 text-white'
                    : 'bg-gray-100 text-gray-900'
                } ${msg.failed ? 'opacity-50' : ''}`}
              >
                <p className="whitespace-pre-wrap">{msg.content}</p>
                {msg.failed && (
                  <p className="text-xs mt-1 text-red-300">Failed to send</p>
                )}
              </div>
            </div>
          ))}

          {loading && (
            <div className="flex justify-start">
              <div className="bg-gray-100 rounded-2xl px-4 py-3">
                <div className="flex items-center gap-1">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Error Banner */}
      {error && (
        <div className="bg-red-50 border-t border-red-200 px-4 py-2">
          <div className="max-w-4xl mx-auto flex items-center justify-between">
            <p className="text-sm text-red-700">{error}</p>
            <button onClick={clearError} className="text-red-700 hover:text-red-900">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
      )}

      {/* Input Area */}
      {caseState && !isComplete && (
        <div className="bg-white border-t border-gray-200 px-4 py-4">
          <form onSubmit={handleSubmit} className="max-w-4xl mx-auto flex gap-3">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Type your response..."
              disabled={loading}
              className="input flex-1"
              autoFocus
            />
            <button
              type="submit"
              disabled={!input.trim() || loading}
              className="btn btn-primary"
            >
              Send
            </button>
          </form>
        </div>
      )}

      {/* Completed State with Debrief */}
      {isComplete && debrief && (
        <div className="border-t border-gray-200 px-4 py-6 bg-gray-50">
          <div className="max-w-2xl mx-auto">
            <DebriefCard debrief={debrief} onNewCase={() => navigate('/')} />
          </div>
        </div>
      )}

      {/* Fallback if complete but no structured debrief */}
      {isComplete && !debrief && (
        <div className="bg-echo-50 border-t border-echo-200 px-4 py-4">
          <div className="max-w-4xl mx-auto text-center">
            <p className="text-echo-700 font-medium mb-2">Case Complete!</p>
            <button onClick={() => navigate('/')} className="btn btn-primary">
              Start New Case
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
