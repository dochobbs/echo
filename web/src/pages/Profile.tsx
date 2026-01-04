import { useState, useEffect } from 'react';
import { motion } from 'motion/react';
import { useAuth } from '../hooks/useAuth';
import type { LearnerLevel, UserStats } from '../types';

const LEVELS: { value: LearnerLevel; label: string }[] = [
  { value: 'student', label: 'Medical Student' },
  { value: 'np_student', label: 'NP Student' },
  { value: 'resident', label: 'Resident' },
  { value: 'fellow', label: 'Fellow' },
  { value: 'attending', label: 'Attending' },
];

export function Profile() {
  const { user, updateProfile } = useAuth();
  const [stats, setStats] = useState<UserStats | null>(null);
  const [editing, setEditing] = useState(false);
  const [name, setName] = useState(user?.name || '');
  const [level, setLevel] = useState<LearnerLevel>(user?.level || 'student');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadStats() {
      try {
        const response = await fetch('/api/auth/me/stats', {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('echo_access_token')}`,
          },
        });
        if (response.ok) {
          const data = await response.json();
          setStats(data);
        }
      } catch {
        // Stats not available
      }
    }

    loadStats();
  }, []);

  const handleSave = async () => {
    setLoading(true);
    setError(null);

    try {
      await updateProfile({ name, level });
      setEditing(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update profile');
    } finally {
      setLoading(false);
    }
  };

  if (!user) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-12 text-center">
        <p className="text-gray-500">Please sign in to view your profile.</p>
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
        Profile
      </motion.h1>

      <div className="grid md:grid-cols-2 gap-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="card p-6"
        >
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-semibold text-gray-100">Your Info</h2>
            {!editing && (
              <button
                onClick={() => setEditing(true)}
                className="text-sm text-echo-400 hover:text-echo-300 transition-colors"
              >
                Edit
              </button>
            )}
          </div>

          {editing ? (
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-1">
                  Name
                </label>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="input"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-400 mb-1">
                  Level
                </label>
                <select
                  value={level}
                  onChange={(e) => setLevel(e.target.value as LearnerLevel)}
                  className="input"
                >
                  {LEVELS.map((l) => (
                    <option key={l.value} value={l.value}>
                      {l.label}
                    </option>
                  ))}
                </select>
              </div>

              {error && (
                <p className="text-sm text-red-400">{error}</p>
              )}

              <div className="flex gap-2">
                <motion.button
                  onClick={handleSave}
                  disabled={loading}
                  className="btn btn-primary"
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  {loading ? 'Saving...' : 'Save'}
                </motion.button>
                <button
                  onClick={() => {
                    setEditing(false);
                    setName(user.name || '');
                    setLevel(user.level);
                  }}
                  className="btn btn-secondary"
                >
                  Cancel
                </button>
              </div>
            </div>
          ) : (
            <div className="space-y-3">
              <div>
                <span className="text-sm text-gray-500">Name</span>
                <p className="text-gray-100">{user.name || '-'}</p>
              </div>
              <div>
                <span className="text-sm text-gray-500">Email</span>
                <p className="text-gray-100">{user.email}</p>
              </div>
              <div>
                <span className="text-sm text-gray-500">Level</span>
                <p className="text-gray-100">
                  {LEVELS.find((l) => l.value === user.level)?.label}
                </p>
              </div>
            </div>
          )}
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="card p-6"
        >
          <h2 className="font-semibold text-gray-100 mb-4">Your Progress</h2>

          {stats ? (
            <div className="grid grid-cols-2 gap-4">
              <div className="text-center p-4 bg-surface-3 rounded-xl border border-surface-4">
                <p className="text-3xl font-bold text-echo-400">
                  {stats.completed_cases}
                </p>
                <p className="text-sm text-gray-500">Cases Completed</p>
              </div>
              <div className="text-center p-4 bg-surface-3 rounded-xl border border-surface-4">
                <p className="text-3xl font-bold text-echo-400">
                  {stats.unique_conditions}
                </p>
                <p className="text-sm text-gray-500">Conditions Seen</p>
              </div>
              {stats.avg_duration_seconds && (
                <div className="text-center p-4 bg-surface-3 rounded-xl border border-surface-4 col-span-2">
                  <p className="text-3xl font-bold text-copper-400">
                    {Math.round(stats.avg_duration_seconds / 60)} min
                  </p>
                  <p className="text-sm text-gray-500">Avg. Case Duration</p>
                </div>
              )}
            </div>
          ) : (
            <p className="text-gray-500 text-center py-8">
              Complete some cases to see your progress!
            </p>
          )}
        </motion.div>
      </div>
    </div>
  );
}
