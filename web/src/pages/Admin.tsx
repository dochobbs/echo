import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'motion/react';
import { api, AdminMetrics, AdminUser, AdminCase } from '../api/client';
import { useAuth } from '../hooks/useAuth';
import { UserIcon } from '../components/icons';

type Tab = 'metrics' | 'users' | 'cases';

export function Admin() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [tab, setTab] = useState<Tab>('metrics');
  const [metrics, setMetrics] = useState<AdminMetrics | null>(null);
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [cases, setCases] = useState<AdminCase[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (user?.role !== 'admin') {
      navigate('/');
      return;
    }
    loadData();
  }, [user, navigate]);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [metricsData, usersData, casesData] = await Promise.all([
        api.getAdminMetrics(),
        api.getAdminUsers(),
        api.getAdminCases(),
      ]);
      setMetrics(metricsData);
      setUsers(usersData);
      setCases(casesData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load admin data');
    } finally {
      setLoading(false);
    }
  };

  if (user?.role !== 'admin') {
    return null;
  }

  const formatDuration = (minutes?: number) => {
    if (!minutes) return '-';
    if (minutes < 60) return `${Math.round(minutes)}m`;
    return `${Math.floor(minutes / 60)}h ${Math.round(minutes % 60)}m`;
  };

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8"
      >
        <h1 className="text-2xl font-semibold text-gray-100 mb-2">Admin Dashboard</h1>
        <p className="text-gray-400">Platform metrics and user management</p>
      </motion.div>

      <div className="flex gap-2 mb-6">
        {(['metrics', 'users', 'cases'] as Tab[]).map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
              tab === t
                ? 'bg-echo-500/20 text-echo-400 border border-echo-500/30'
                : 'text-gray-400 hover:text-gray-200 hover:bg-surface-3'
            }`}
          >
            {t.charAt(0).toUpperCase() + t.slice(1)}
          </button>
        ))}
      </div>

      {error && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="mb-6 p-4 bg-red-500/10 border border-red-500/20 rounded-xl text-red-400"
        >
          {error}
        </motion.div>
      )}

      {loading ? (
        <div className="flex justify-center py-12">
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
            className="w-8 h-8 border-2 border-echo-500 border-t-transparent rounded-full"
          />
        </div>
      ) : (
        <>
          {tab === 'metrics' && metrics && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="space-y-6"
            >
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <MetricCard label="Total Users" value={metrics.total_users} />
                <MetricCard label="Active (7d)" value={metrics.active_last_7_days} />
                <MetricCard label="Total Cases" value={metrics.total_cases} />
                <MetricCard label="Completed" value={metrics.completed_cases} />
                <MetricCard label="Active Cases" value={metrics.active_cases} />
                <MetricCard 
                  label="Completion Rate" 
                  value={metrics.completion_rate ? `${(metrics.completion_rate * 100).toFixed(0)}%` : '-'} 
                />
                <MetricCard 
                  label="Avg Duration" 
                  value={formatDuration(metrics.avg_case_duration_minutes)} 
                />
                <MetricCard 
                  label="Avg Hints/Case" 
                  value={metrics.avg_hints_per_case?.toFixed(1) || '-'} 
                />
              </div>

              {metrics.most_practiced_conditions.length > 0 && (
                <div className="card p-4">
                  <h3 className="text-sm font-medium text-gray-400 mb-3">Most Practiced Conditions</h3>
                  <div className="space-y-2">
                    {metrics.most_practiced_conditions.slice(0, 5).map((c, i) => (
                      <div key={i} className="flex items-center justify-between">
                        <span className="text-gray-200">{c.condition}</span>
                        <span className="text-gray-500">{c.count} cases</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </motion.div>
          )}

          {tab === 'users' && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="space-y-3"
            >
              {users.length === 0 ? (
                <p className="text-gray-500 text-center py-8">No users found</p>
              ) : (
                users.map((u) => (
                  <div key={u.id} className="card p-4">
                    <div className="flex items-start justify-between">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 bg-surface-3 rounded-full flex items-center justify-center">
                          <UserIcon size={20} className="text-gray-400" />
                        </div>
                        <div>
                          <p className="font-medium text-gray-100">{u.name || u.email}</p>
                          <p className="text-sm text-gray-500">{u.email}</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <span className={`text-xs px-2 py-0.5 rounded-full ${
                          u.role === 'admin' 
                            ? 'bg-copper-500/20 text-copper-400' 
                            : 'bg-surface-3 text-gray-400'
                        }`}>
                          {u.role}
                        </span>
                      </div>
                    </div>
                    <div className="mt-3 pt-3 border-t border-surface-3 grid grid-cols-4 gap-4 text-sm">
                      <div>
                        <p className="text-gray-500">Level</p>
                        <p className="text-gray-200">{u.level}</p>
                      </div>
                      <div>
                        <p className="text-gray-500">Cases</p>
                        <p className="text-gray-200">{u.total_cases}</p>
                      </div>
                      <div>
                        <p className="text-gray-500">Completed</p>
                        <p className="text-gray-200">{u.completed_cases}</p>
                      </div>
                      <div>
                        <p className="text-gray-500">Last Active</p>
                        <p className="text-gray-200">{formatDate(u.last_active)}</p>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </motion.div>
          )}

          {tab === 'cases' && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="space-y-3"
            >
              {cases.length === 0 ? (
                <p className="text-gray-500 text-center py-8">No cases found</p>
              ) : (
                cases.map((c) => (
                  <div key={c.session_id} className="card p-4">
                    <div className="flex items-start justify-between">
                      <div>
                        <p className="font-medium text-gray-100">{c.condition_display}</p>
                        <p className="text-sm text-gray-500">{c.patient_name}</p>
                      </div>
                      <span className={`text-xs px-2 py-0.5 rounded-full ${
                        c.status === 'completed' 
                          ? 'bg-green-500/20 text-green-400' 
                          : c.status === 'active'
                          ? 'bg-echo-500/20 text-echo-400'
                          : 'bg-surface-3 text-gray-400'
                      }`}>
                        {c.status}
                      </span>
                    </div>
                    <div className="mt-3 pt-3 border-t border-surface-3 grid grid-cols-4 gap-4 text-sm">
                      <div>
                        <p className="text-gray-500">User</p>
                        <p className="text-gray-200 truncate">{c.user_email || 'Anonymous'}</p>
                      </div>
                      <div>
                        <p className="text-gray-500">Phase</p>
                        <p className="text-gray-200">{c.phase}</p>
                      </div>
                      <div>
                        <p className="text-gray-500">Hints</p>
                        <p className="text-gray-200">{c.hints_given}</p>
                      </div>
                      <div>
                        <p className="text-gray-500">Duration</p>
                        <p className="text-gray-200">{formatDuration(c.duration_minutes)}</p>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </motion.div>
          )}
        </>
      )}
    </div>
  );
}

function MetricCard({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="card p-4">
      <p className="text-sm text-gray-500 mb-1">{label}</p>
      <p className="text-2xl font-semibold text-gray-100">{value}</p>
    </div>
  );
}
