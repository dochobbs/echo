import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'motion/react';
import { api } from '../api/client';
import { useAuth } from '../hooks/useAuth';

interface CaseSummary {
  session_id: string;
  condition_display: string;
  patient_name: string;
  patient_age: string;
  learner_level: string;
  completed_at: string;
  duration_minutes?: number;
  teaching_moments_count: number;
  status?: string;
  hints_given?: number;
}

export function History() {
  const { user } = useAuth();
  const [cases, setCases] = useState<CaseSummary[]>([]);
  const [activeCases, setActiveCases] = useState<CaseSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadHistory() {
      try {
        const [historyData, activeData] = await Promise.all([
          api.getCaseHistory(),
          user ? api.getActiveCases() : Promise.resolve({ cases: [] }),
        ]);
        setCases((historyData.cases || []) as CaseSummary[]);
        setActiveCases((activeData.cases || []) as CaseSummary[]);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load history');
      } finally {
        setLoading(false);
      }
    }

    loadHistory();
  }, [user]);

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
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

      {activeCases.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <h2 className="text-lg font-semibold text-gray-100 mb-4">Active Cases</h2>
          <div className="space-y-4">
            {activeCases.map((c, index) => (
              <motion.div
                key={c.session_id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.05 }}
                className="card p-4 border-copper-500/30 hover:border-copper-500/50 transition-colors"
              >
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="font-medium text-gray-100">
                      {c.condition_display}
                    </h3>
                    <p className="text-sm text-gray-500">
                      {c.patient_name}, {c.patient_age}
                    </p>
                  </div>
                  <span className="px-2.5 py-1 text-xs font-medium rounded-full bg-copper-500/20 text-copper-400 border border-copper-500/30">
                    active
                  </span>
                </div>
                <div className="mt-3 flex items-center gap-4 text-sm text-gray-500">
                  <span>{formatDate(c.completed_at)}</span>
                  <span className="w-1 h-1 bg-surface-4 rounded-full" />
                  <span>{c.teaching_moments_count || 0} teaching moments</span>
                </div>
                <Link
                  to={`/case/${c.session_id}`}
                  className="mt-3 inline-block text-sm text-copper-400 hover:text-copper-300 font-medium transition-colors"
                >
                  Continue case →
                </Link>
              </motion.div>
            ))}
          </div>
        </motion.div>
      )}

      {cases.length === 0 && activeCases.length === 0 ? (
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
      ) : cases.length > 0 && (
        <>
          {activeCases.length > 0 && (
            <h2 className="text-lg font-semibold text-gray-100 mb-4">Completed Cases</h2>
          )}
          <div className="space-y-4">
            {cases.map((c, index) => (
              <motion.div
                key={c.session_id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.05 }}
                className="card p-4 hover:border-echo-500/30 transition-colors"
              >
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="font-medium text-gray-100">
                      {c.condition_display}
                    </h3>
                    <p className="text-sm text-gray-500">
                      {c.patient_name}, {c.patient_age}
                    </p>
                  </div>
                  <span className="px-2.5 py-1 text-xs font-medium rounded-full bg-echo-500/20 text-echo-400 border border-echo-500/30">
                    completed
                  </span>
                </div>

                <div className="mt-3 flex items-center gap-4 text-sm text-gray-500">
                  <span>{formatDate(c.completed_at)}</span>
                  <span className="w-1 h-1 bg-surface-4 rounded-full" />
                  <span>{c.duration_minutes ? `${c.duration_minutes} min` : '-'}</span>
                  <span className="w-1 h-1 bg-surface-4 rounded-full" />
                  <span>{c.teaching_moments_count} teaching moments</span>
                </div>
                <Link
                  to={`/case/${c.session_id}/review`}
                  className="mt-3 inline-block text-sm text-echo-400 hover:text-echo-300 font-medium transition-colors"
                >
                  Review case →
                </Link>
              </motion.div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
