import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'motion/react';
import { api, AdminMetrics, AdminUser, AdminCase, AdminCaseDetail } from '../api/client';
import { useAuth } from '../hooks/useAuth';
import { UserIcon, ChevronLeftIcon } from '../components/icons';

type Tab = 'metrics' | 'users' | 'cases';
type View = 'list' | 'user-detail' | 'case-detail';

export function Admin() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [tab, setTab] = useState<Tab>('metrics');
  const [view, setView] = useState<View>('list');
  const [metrics, setMetrics] = useState<AdminMetrics | null>(null);
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [cases, setCases] = useState<AdminCase[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [selectedUser, setSelectedUser] = useState<AdminUser | null>(null);
  const [userCases, setUserCases] = useState<AdminCase[]>([]);
  const [selectedCase, setSelectedCase] = useState<AdminCaseDetail | null>(null);

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

  const handleUserClick = async (u: AdminUser) => {
    setSelectedUser(u);
    setSelectedCase(null);
    setError(null);
    setView('user-detail');
    setLoading(true);
    try {
      const cases = await api.getAdminUserCases(u.id);
      setUserCases(cases);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load user cases');
    } finally {
      setLoading(false);
    }
  };

  const handleCaseClick = async (sessionId: string) => {
    setError(null);
    setLoading(true);
    try {
      const caseDetail = await api.getAdminCaseDetail(sessionId);
      setSelectedCase(caseDetail);
      setView('case-detail');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load case details');
    } finally {
      setLoading(false);
    }
  };

  const handleBack = () => {
    if (view === 'case-detail' && selectedUser) {
      setView('user-detail');
      setSelectedCase(null);
    } else {
      setView('list');
      setSelectedUser(null);
      setSelectedCase(null);
      setUserCases([]);
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

  const formatDate = (dateStr?: string | null) => {
    if (!dateStr) return '-';
    const date = new Date(dateStr);
    if (isNaN(date.getTime())) return '-';
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const formatSeconds = (seconds?: number) => {
    if (!seconds) return '-';
    const mins = Math.floor(seconds / 60);
    if (mins < 60) return `${mins}m`;
    return `${Math.floor(mins / 60)}h ${mins % 60}m`;
  };

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8"
      >
        {view !== 'list' && (
          <button
            onClick={handleBack}
            className="flex items-center gap-2 text-gray-400 hover:text-gray-200 mb-4 transition-colors"
          >
            <ChevronLeftIcon size={20} />
            <span>Back</span>
          </button>
        )}
        <h1 className="text-2xl font-semibold text-gray-100 mb-2">
          {view === 'list' && 'Admin Dashboard'}
          {view === 'user-detail' && (selectedUser?.name || selectedUser?.email)}
          {view === 'case-detail' && selectedCase?.condition_display}
        </h1>
        <p className="text-gray-400">
          {view === 'list' && 'Platform metrics and user management'}
          {view === 'user-detail' && `${selectedUser?.email} · ${selectedUser?.level}`}
          {view === 'case-detail' && `Case with ${(selectedCase?.patient_data as { name?: string })?.name || 'patient'}`}
        </p>
      </motion.div>

      {view === 'list' && (
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
      )}

      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="mb-6 p-4 bg-red-500/10 border border-red-500/20 rounded-xl text-red-400"
          >
            {error}
          </motion.div>
        )}
      </AnimatePresence>

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
          {view === 'list' && tab === 'metrics' && metrics && (
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

          {view === 'list' && tab === 'users' && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="space-y-3"
            >
              {users.length === 0 ? (
                <p className="text-gray-500 text-center py-8">No users found</p>
              ) : (
                users.map((u) => (
                  <div
                    key={u.id}
                    onClick={() => handleUserClick(u)}
                    className="card p-4 cursor-pointer hover:border-echo-500/30 transition-colors"
                  >
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

          {view === 'list' && tab === 'cases' && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="space-y-3"
            >
              {cases.length === 0 ? (
                <p className="text-gray-500 text-center py-8">No cases found</p>
              ) : (
                cases.map((c) => (
                  <div
                    key={c.session_id}
                    onClick={() => handleCaseClick(c.session_id)}
                    className="card p-4 cursor-pointer hover:border-echo-500/30 transition-colors"
                  >
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

          {view === 'user-detail' && selectedUser && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="space-y-6"
            >
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <MetricCard label="Total Cases" value={selectedUser.total_cases} />
                <MetricCard label="Completed" value={selectedUser.completed_cases} />
                <MetricCard label="Level" value={selectedUser.level} />
                <MetricCard label="Role" value={selectedUser.role} />
              </div>

              <div>
                <h3 className="text-lg font-medium text-gray-200 mb-4">Case History</h3>
                {userCases.length === 0 ? (
                  <p className="text-gray-500 text-center py-8">No cases found for this user</p>
                ) : (
                  <div className="space-y-3">
                    {userCases.map((c) => (
                      <div
                        key={c.session_id}
                        onClick={() => handleCaseClick(c.session_id)}
                        className="card p-4 cursor-pointer hover:border-echo-500/30 transition-colors"
                      >
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
                        <div className="mt-3 pt-3 border-t border-surface-3 grid grid-cols-3 gap-4 text-sm">
                          <div>
                            <p className="text-gray-500">Phase</p>
                            <p className="text-gray-200">{c.phase}</p>
                          </div>
                          <div>
                            <p className="text-gray-500">Hints</p>
                            <p className="text-gray-200">{c.hints_given}</p>
                          </div>
                          <div>
                            <p className="text-gray-500">Date</p>
                            <p className="text-gray-200">{formatDate(c.started_at)}</p>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </motion.div>
          )}

          {view === 'case-detail' && selectedCase && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="space-y-6"
            >
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <MetricCard label="Status" value={selectedCase.status} />
                <MetricCard label="Phase" value={selectedCase.phase} />
                <MetricCard label="Hints Used" value={selectedCase.hints_given} />
                <MetricCard label="Duration" value={formatSeconds(selectedCase.duration_seconds)} />
              </div>

              {selectedCase.user && (
                <div className="card p-4">
                  <h3 className="text-sm font-medium text-gray-400 mb-2">Learner</h3>
                  <p className="text-gray-200">{selectedCase.user.name || selectedCase.user.email}</p>
                  <p className="text-sm text-gray-500">{selectedCase.user.level}</p>
                </div>
              )}

              <div className="card p-4">
                <h3 className="text-sm font-medium text-gray-400 mb-2">Patient</h3>
                <p className="text-gray-200">{(selectedCase.patient_data as { name?: string })?.name}</p>
                <p className="text-sm text-gray-500">
                  {(selectedCase.patient_data as { age?: string })?.age} · {(selectedCase.patient_data as { sex?: string })?.sex}
                </p>
                <p className="text-sm text-gray-400 mt-2">
                  Chief complaint: {(selectedCase.patient_data as { chief_complaint?: string })?.chief_complaint}
                </p>
              </div>

              <div>
                <h3 className="text-lg font-medium text-gray-200 mb-4">Conversation</h3>
                <div className="space-y-3">
                  {selectedCase.conversation.map((msg, i) => (
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
                          {msg.role === 'user' ? 'Learner' : msg.role === 'echo' ? 'Echo' : 'System'}
                        </span>
                        <span className="text-xs text-gray-600">
                          {formatDate(msg.created_at)}
                        </span>
                      </div>
                      <p className="text-gray-200 whitespace-pre-wrap">{msg.content}</p>
                    </div>
                  ))}
                </div>
              </div>

              {selectedCase.debrief_summary && (
                <div className="card p-4">
                  <h3 className="text-lg font-medium text-gray-200 mb-3">Debrief Summary</h3>
                  <p className="text-gray-300 whitespace-pre-wrap">{selectedCase.debrief_summary}</p>
                </div>
              )}

              {(selectedCase.history_gathered.length > 0 || 
                selectedCase.exam_performed.length > 0 ||
                selectedCase.differential.length > 0 ||
                selectedCase.plan_proposed.length > 0) && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {selectedCase.history_gathered.length > 0 && (
                    <div className="card p-4">
                      <h4 className="text-sm font-medium text-gray-400 mb-2">History Gathered</h4>
                      <ul className="text-sm text-gray-300 space-y-1">
                        {selectedCase.history_gathered.map((h, i) => (
                          <li key={i}>• {h}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  {selectedCase.exam_performed.length > 0 && (
                    <div className="card p-4">
                      <h4 className="text-sm font-medium text-gray-400 mb-2">Exam Performed</h4>
                      <ul className="text-sm text-gray-300 space-y-1">
                        {selectedCase.exam_performed.map((e, i) => (
                          <li key={i}>• {e}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  {selectedCase.differential.length > 0 && (
                    <div className="card p-4">
                      <h4 className="text-sm font-medium text-gray-400 mb-2">Differential</h4>
                      <ul className="text-sm text-gray-300 space-y-1">
                        {selectedCase.differential.map((d, i) => (
                          <li key={i}>• {d}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  {selectedCase.plan_proposed.length > 0 && (
                    <div className="card p-4">
                      <h4 className="text-sm font-medium text-gray-400 mb-2">Plan Proposed</h4>
                      <ul className="text-sm text-gray-300 space-y-1">
                        {selectedCase.plan_proposed.map((p, i) => (
                          <li key={i}>• {p}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
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
