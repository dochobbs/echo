import { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'motion/react';
import { api } from '../api/client';
import { MessageBubble } from '../components/MessageBubble';
import { TypingIndicator } from '../components/TypingIndicator';
import type { Message, LearnerLevel } from '../types';

export function Describe() {
  const navigate = useNavigate();
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [describeState, setDescribeState] = useState<any>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    async function startSession() {
      setLoading(true);
      try {
        const response = await api.startDescribeCase('student' as LearnerLevel);
        setDescribeState(response.case_state);
        setMessages([{
          id: crypto.randomUUID(),
          session_id: 'describe',
          role: 'echo',
          content: response.message,
          created_at: new Date().toISOString(),
        }]);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to start session');
      } finally {
        setLoading(false);
      }
    }
    startSession();
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading || !describeState) return;

    const userMsg = input.trim();
    setInput('');

    const userMessage: Message = {
      id: crypto.randomUUID(),
      session_id: 'describe',
      role: 'user',
      content: userMsg,
      created_at: new Date().toISOString(),
    };
    setMessages(prev => [...prev, userMessage]);
    setLoading(true);

    try {
      const response = await fetch('/api/case/describe/message', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMsg, state: describeState }),
      });
      
      if (!response.ok) throw new Error('Failed to send message');
      
      const data = await response.json();
      setDescribeState(data.state);
      
      setMessages(prev => [...prev, {
        id: crypto.randomUUID(),
        session_id: 'describe',
        role: 'echo',
        content: data.message,
        created_at: new Date().toISOString(),
      }]);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to send');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)]">
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-surface-1 border-b border-surface-3 px-4 py-3"
      >
        <div className="max-w-4xl mx-auto flex items-center justify-between">
          <div>
            <h2 className="font-medium text-gray-100">Describe Your Case</h2>
            <p className="text-sm text-gray-500">Tell me about a patient you saw</p>
          </div>
          <motion.button
            onClick={() => navigate('/')}
            className="btn btn-secondary text-sm"
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            Done
          </motion.button>
        </div>
      </motion.div>

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
          <p className="text-sm text-red-400 text-center">{error}</p>
        </motion.div>
      )}

      <div className="bg-surface-1 border-t border-surface-3 px-4 py-4">
        <form onSubmit={handleSubmit} className="max-w-4xl mx-auto flex gap-3">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Describe your case..."
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
    </div>
  );
}
