import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { motion } from 'motion/react';
import { api } from '../api/client';
import { ChevronLeftIcon } from '../components/icons';

interface CaseExport {
  session_id: string;
  condition_key: string;
  condition_display: string;
  patient_name: string;
  patient_age: string;
  learner_level: string;
  started_at: string;
  completed_at?: string;
  duration_minutes?: number;
  status: string;
  phase: string;
  history_gathered: string[];
  exam_performed: string[];
  differential: string[];
  plan_proposed: string[];
  hints_given: number;
  teaching_moments: string[];
  debrief_summary?: string;
  conversation?: Array<{
    role: string;
    content: string;
    timestamp?: string;
  }>;
}

export function CaseReview() {
  const { sessionId } = useParams<{ sessionId: string }>();
  const [caseData, setCaseData] = useState<CaseExport | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadCase() {
      if (!sessionId) {
        setError('No case ID provided');
        setLoading(false);
        return;
      }
      
      try {
        const data = await api.getCaseExport(sessionId);
        setCaseData(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load case');
      } finally {
        setLoading(false);
      }
    }

    loadCase();
  }, [sessionId]);

  const formatDate = (dateStr?: string) => {
    if (!dateStr) return '-';
    const date = new Date(dateStr);
    if (isNaN(date.getTime())) return '-';
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
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

  if (error || !caseData) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-12">
        <Link
          to="/history"
          className="flex items-center gap-2 text-gray-400 hover:text-gray-200 mb-6 transition-colors"
        >
          <ChevronLeftIcon size={20} />
          <span>Back to History</span>
        </Link>
        <div className="card p-8 text-center">
          <p className="text-red-400">{error || 'Case not found'}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <Link
        to="/history"
        className="flex items-center gap-2 text-gray-400 hover:text-gray-200 mb-6 transition-colors"
      >
        <ChevronLeftIcon size={20} />
        <span>Back to History</span>
      </Link>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8"
      >
        <h1 className="text-2xl font-semibold text-gray-100 mb-2">
          {caseData.condition_display}
        </h1>
        <p className="text-gray-400">
          {caseData.patient_name}, {caseData.patient_age}
        </p>
      </motion.div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <div className="card p-4">
          <p className="text-sm text-gray-500 mb-1">Status</p>
          <p className="text-lg font-semibold text-gray-100">{caseData.status}</p>
        </div>
        <div className="card p-4">
          <p className="text-sm text-gray-500 mb-1">Duration</p>
          <p className="text-lg font-semibold text-gray-100">
            {caseData.duration_minutes ? `${caseData.duration_minutes} min` : '-'}
          </p>
        </div>
        <div className="card p-4">
          <p className="text-sm text-gray-500 mb-1">Hints Used</p>
          <p className="text-lg font-semibold text-gray-100">{caseData.hints_given}</p>
        </div>
        <div className="card p-4">
          <p className="text-sm text-gray-500 mb-1">Completed</p>
          <p className="text-lg font-semibold text-gray-100">{formatDate(caseData.completed_at)}</p>
        </div>
      </div>

      {caseData.debrief_summary && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="card p-6 mb-8"
        >
          <h2 className="text-lg font-semibold text-gray-100 mb-4">Debrief Summary</h2>
          <p className="text-gray-300 whitespace-pre-wrap">{caseData.debrief_summary}</p>
        </motion.div>
      )}

      {((caseData.history_gathered ?? []).length > 0 || 
        (caseData.exam_performed ?? []).length > 0 ||
        (caseData.differential ?? []).length > 0 ||
        (caseData.plan_proposed ?? []).length > 0) && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8"
        >
          {(caseData.history_gathered ?? []).length > 0 && (
            <div className="card p-4">
              <h3 className="text-sm font-medium text-gray-400 mb-3">History Gathered</h3>
              <ul className="text-sm text-gray-300 space-y-1">
                {(caseData.history_gathered ?? []).map((h, i) => (
                  <li key={i}>• {h}</li>
                ))}
              </ul>
            </div>
          )}
          {(caseData.exam_performed ?? []).length > 0 && (
            <div className="card p-4">
              <h3 className="text-sm font-medium text-gray-400 mb-3">Exam Performed</h3>
              <ul className="text-sm text-gray-300 space-y-1">
                {(caseData.exam_performed ?? []).map((e, i) => (
                  <li key={i}>• {e}</li>
                ))}
              </ul>
            </div>
          )}
          {(caseData.differential ?? []).length > 0 && (
            <div className="card p-4">
              <h3 className="text-sm font-medium text-gray-400 mb-3">Differential Diagnosis</h3>
              <ul className="text-sm text-gray-300 space-y-1">
                {(caseData.differential ?? []).map((d, i) => (
                  <li key={i}>• {d}</li>
                ))}
              </ul>
            </div>
          )}
          {(caseData.plan_proposed ?? []).length > 0 && (
            <div className="card p-4">
              <h3 className="text-sm font-medium text-gray-400 mb-3">Plan Proposed</h3>
              <ul className="text-sm text-gray-300 space-y-1">
                {(caseData.plan_proposed ?? []).map((p, i) => (
                  <li key={i}>• {p}</li>
                ))}
              </ul>
            </div>
          )}
        </motion.div>
      )}

      {(caseData.teaching_moments ?? []).length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="card p-6 mb-8"
        >
          <h2 className="text-lg font-semibold text-gray-100 mb-4">Teaching Moments</h2>
          <ul className="text-gray-300 space-y-2">
            {(caseData.teaching_moments ?? []).map((t, i) => (
              <li key={i} className="flex gap-2">
                <span className="text-echo-400">•</span>
                <span>{t}</span>
              </li>
            ))}
          </ul>
        </motion.div>
      )}

      {caseData.conversation && caseData.conversation.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
        >
          <h2 className="text-lg font-semibold text-gray-100 mb-4">Conversation</h2>
          <div className="space-y-3">
            {caseData.conversation.map((msg, i) => (
              <div
                key={i}
                className={`p-4 rounded-xl ${
                  msg.role === 'user'
                    ? 'bg-echo-500/10 border border-echo-500/20 ml-8'
                    : msg.role === 'echo'
                    ? 'bg-surface-2 border border-surface-4 mr-8'
                    : 'bg-surface-3 border border-surface-4 text-center text-sm'
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <span className={`text-xs font-medium ${
                    msg.role === 'user' ? 'text-echo-400' : 'text-gray-500'
                  }`}>
                    {msg.role === 'user' ? 'You' : msg.role === 'echo' ? 'Echo' : 'System'}
                  </span>
                </div>
                <p className="text-gray-200 whitespace-pre-wrap">{msg.content}</p>
              </div>
            ))}
          </div>
        </motion.div>
      )}
    </div>
  );
}
