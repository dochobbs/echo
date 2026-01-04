import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'motion/react';
import { api } from '../api/client';
import type { CaseSession } from '../types';

export function History() {
  const [cases, setCases] = useState<CaseSession[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadHistory() {
      try {
        const data = await api.getCaseHistory();
        setCases(data.cases as CaseSession[]);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load history');
      } finally {
        setLoading(false);
      }
    }

    loadHistory();
  }, []);

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  const formatDuration = (seconds?: number) => {
    if (!seconds) return '-';
    const mins = Math.floor(seconds / 60);
    return `${mins} min`;
  };

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-12 text-center">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
          className="w-8 h-8 border-2 border-echo-500 border-t-transparent rounded-full mx-auto"
        />
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-12 text-center">
        <p className="text-red-400">{error}</p>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <motion.h1
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-2xl font-bold text-gray-100 mb-6"
      >
        Case History
      </motion.h1>

      {cases.length === 0 ? (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="card p-8 text-center"
        >
          <p className="text-gray-500 mb-4">No cases yet. Start your first one!</p>
          <Link to="/" className="btn btn-primary">
            Start a Case
          </Link>
        </motion.div>
      ) : (
        <div className="space-y-4">
          {cases.map((c, index) => (
            <motion.div
              key={c.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
              className="card p-4 hover:border-surface-3 transition-colors"
            >
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="font-medium text-gray-100">
                    {c.condition_display}
                  </h3>
                  <p className="text-sm text-gray-500">
                    {c.patient_data.name}, {c.patient_data.age}
                  </p>
                </div>
                <span
                  className={`px-2.5 py-1 text-xs font-medium rounded-full ${
                    c.status === 'completed'
                      ? 'bg-echo-500/20 text-echo-400 border border-echo-500/30'
                      : c.status === 'active'
                      ? 'bg-copper-500/20 text-copper-400 border border-copper-500/30'
                      : 'bg-surface-4 text-gray-400'
                  }`}
                >
                  {c.status}
                </span>
              </div>

              <div className="mt-3 flex items-center gap-4 text-sm text-gray-500">
                <span>{formatDate(c.started_at)}</span>
                <span className="w-1 h-1 bg-surface-4 rounded-full" />
                <span>{formatDuration(c.duration_seconds)}</span>
                <span className="w-1 h-1 bg-surface-4 rounded-full" />
                <span>{c.hints_given} hints</span>
              </div>

              {c.status === 'active' && (
                <Link
                  to={`/case/${c.id}`}
                  className="mt-3 inline-block text-sm text-echo-400 hover:text-echo-300 font-medium transition-colors"
                >
                  Continue case →
                </Link>
              )}
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
}
