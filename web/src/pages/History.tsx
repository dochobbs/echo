import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
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
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-echo-600 mx-auto" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-12 text-center">
        <p className="text-red-600">{error}</p>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Case History</h1>

      {cases.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-600 mb-4">No cases yet. Start your first one!</p>
          <Link to="/" className="btn btn-primary">
            Start a Case
          </Link>
        </div>
      ) : (
        <div className="space-y-4">
          {cases.map((c) => (
            <div key={c.id} className="card p-4">
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="font-medium text-gray-900">
                    {c.condition_display}
                  </h3>
                  <p className="text-sm text-gray-500">
                    {c.patient_data.name}, {c.patient_data.age}
                  </p>
                </div>
                <span
                  className={`px-2 py-1 text-xs rounded-full ${
                    c.status === 'completed'
                      ? 'bg-green-100 text-green-700'
                      : c.status === 'active'
                      ? 'bg-yellow-100 text-yellow-700'
                      : 'bg-gray-100 text-gray-700'
                  }`}
                >
                  {c.status}
                </span>
              </div>

              <div className="mt-3 flex items-center gap-4 text-sm text-gray-500">
                <span>{formatDate(c.started_at)}</span>
                <span>{formatDuration(c.duration_seconds)}</span>
                <span>{c.hints_given} hints</span>
              </div>

              {c.status === 'active' && (
                <Link
                  to={`/case/${c.id}`}
                  className="mt-3 inline-block text-sm text-echo-600 hover:text-echo-700 font-medium"
                >
                  Continue case
                </Link>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
