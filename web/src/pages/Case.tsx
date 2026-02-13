import { useState, useRef, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { motion } from 'motion/react';
import { useCase } from '../hooks/useCase';
import { DebriefCard } from '../components/DebriefCard';
import { MessageBubble } from '../components/MessageBubble';
import { TypingIndicator } from '../components/TypingIndicator';
import { CaseTimeline } from '../components/CaseTimeline';

export function Case() {
  const navigate = useNavigate();
  const { sessionId } = useParams<{ sessionId?: string }>();
  const { caseState, messages, loading, error, debrief, sendMessage, endCase, loadCase, clearError } = useCase();
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const [loadError, setLoadError] = useState<string | null>(null);

  useEffect(() => {
    if (sessionId && !caseState && !isLoading && !loadError) {
      setIsLoading(true);
      loadCase(sessionId)
        .catch(err => setLoadError(err instanceof Error ? err.message : 'Failed to load case'))
        .finally(() => setIsLoading(false));
    }
  }, [sessionId, caseState, loadCase, isLoading, loadError]);

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

  if (!caseState && !loading && !isLoading) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-12 text-center">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="card p-8"
        >
          <p className="text-gray-400 mb-6">No active case. Start a new one from the home page.</p>
          <button onClick={() => navigate('/')} className="btn btn-primary">
            Go Home
          </button>
        </motion.div>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-12 text-center">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
          className="w-8 h-8 border-2 border-echo-500 border-t-transparent rounded-full mx-auto"
        />
        <p className="text-gray-400 mt-4">Loading case...</p>
      </div>
    );
  }

  if (loadError) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-12 text-center">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="card p-8"
        >
          <p className="text-red-400 mb-6">{loadError}</p>
          <button onClick={() => navigate('/')} className="btn btn-primary">
            Go Home
          </button>
        </motion.div>
      </div>
    );
  }

  const isComplete = caseState?.phase === 'complete';

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)]">
      {caseState && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-surface-1 border-b border-surface-3 px-4 py-3"
        >
          <div className="max-w-4xl mx-auto">
            <div className="flex items-center justify-between mb-3">
              <div>
                <h2 className="font-medium text-gray-100">
                  {caseState.patient.name}, {caseState.patient.age} {caseState.patient.age_unit} old {caseState.patient.sex}
                </h2>
                <p className="text-sm text-gray-500">
                  {caseState.patient.condition_display}
                </p>
              </div>
              {!isComplete && (
                <motion.button
                  onClick={handleEndCase}
                  disabled={loading}
                  className="btn btn-secondary text-sm"
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  End Case
                </motion.button>
              )}
            </div>
            
            <CaseTimeline currentPhase={caseState.phase} compact visitType={caseState.visit_type} />
          </div>
        </motion.div>
      )}

      <div className="flex-1 overflow-y-auto px-4 py-6 bg-surface-0">
        <div className="max-w-2xl mx-auto space-y-4">
          {messages.map((msg, index) => (
            <MessageBubble key={msg.id} message={msg} index={index} />
          ))}

          {loading && <TypingIndicator />}

          <div ref={messagesEndRef} />
        </div>
      </div>

      {error && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-red-500/10 border-t border-red-500/20 px-4 py-2"
        >
          <div className="max-w-4xl mx-auto flex items-center justify-between">
            <p className="text-sm text-red-400">{error}</p>
            <button onClick={clearError} className="text-red-400 hover:text-red-300 p-1">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </motion.div>
      )}

      {caseState && !isComplete && (
        <div className="bg-surface-1 border-t border-surface-3 px-4 py-4">
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
            <motion.button
              type="submit"
              disabled={!input.trim() || loading}
              className="btn btn-primary"
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              Send
            </motion.button>
          </form>
        </div>
      )}

      {isComplete && debrief && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="border-t border-surface-3 px-4 py-6 bg-surface-1"
        >
          <div className="max-w-2xl mx-auto">
            <DebriefCard debrief={debrief} onNewCase={() => navigate('/')} />
          </div>
        </motion.div>
      )}

      {isComplete && !debrief && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-echo-500/10 border-t border-echo-500/20 px-4 py-4"
        >
          <div className="max-w-4xl mx-auto text-center">
            <p className="text-echo-400 font-medium mb-3">Case Complete! 🎉</p>
            <button onClick={() => navigate('/')} className="btn btn-primary">
              Start New Case
            </button>
          </div>
        </motion.div>
      )}
    </div>
  );
}
