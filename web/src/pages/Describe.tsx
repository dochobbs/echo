import { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../api/client';
import type { Message, LearnerLevel } from '../types';

export function Describe() {
  const navigate = useNavigate();
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [describeState, setDescribeState] = useState<any>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Start session on mount
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
      <div className="bg-white border-b border-gray-200 px-4 py-3">
        <div className="max-w-4xl mx-auto flex items-center justify-between">
          <div>
            <h2 className="font-medium text-gray-900">Describe Your Case</h2>
            <p className="text-sm text-gray-500">Tell me about a patient you saw</p>
          </div>
          <button onClick={() => navigate('/')} className="btn btn-secondary text-sm">
            Done
          </button>
        </div>
      </div>

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
                }`}
              >
                <p className="whitespace-pre-wrap">{msg.content}</p>
              </div>
            </div>
          ))}

          {loading && (
            <div className="flex justify-start">
              <div className="bg-gray-100 rounded-2xl px-4 py-3">
                <div className="flex items-center gap-1">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border-t border-red-200 px-4 py-2">
          <p className="text-sm text-red-700 text-center">{error}</p>
        </div>
      )}

      <div className="bg-white border-t border-gray-200 px-4 py-4">
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
          <button
            type="submit"
            disabled={!input.trim() || loading}
            className="btn btn-primary"
          >
            Send
          </button>
        </form>
      </div>
    </div>
  );
}
