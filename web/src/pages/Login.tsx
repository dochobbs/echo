import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import type { LearnerLevel } from '../types';

const LEVELS: { value: LearnerLevel; label: string }[] = [
  { value: 'student', label: 'Medical Student' },
  { value: 'np_student', label: 'NP Student' },
  { value: 'resident', label: 'Resident' },
  { value: 'fellow', label: 'Fellow' },
  { value: 'attending', label: 'Attending' },
];

export function Login() {
  const navigate = useNavigate();
  const { signIn, signUp } = useAuth();

  const [isSignUp, setIsSignUp] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [level, setLevel] = useState<LearnerLevel>('student');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      if (isSignUp) {
        await signUp(email, password, name, level);
      } else {
        await signIn(email, password);
      }
      navigate('/');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Authentication failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <div className="max-w-md w-full">
        <div className="text-center mb-8">
          <div className="w-16 h-16 bg-echo-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <svg
              className="w-10 h-10 text-white"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
              />
            </svg>
          </div>
          <h1 className="text-2xl font-bold text-gray-900">
            {isSignUp ? 'Create your account' : 'Welcome back'}
          </h1>
          <p className="text-gray-600 mt-2">
            {isSignUp
              ? 'Start learning with Echo'
              : 'Sign in to continue your learning'}
          </p>
        </div>

        <form onSubmit={handleSubmit} className="card p-6 space-y-4">
          {isSignUp && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Name
              </label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="input"
                placeholder="Dr. Smith"
              />
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Email
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="input"
              placeholder="you@example.com"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Password
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="input"
              placeholder="At least 8 characters"
              minLength={8}
              required
            />
          </div>

          {isSignUp && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Your Level
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
          )}

          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-3">
              <p className="text-sm text-red-700">{error}</p>
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="btn btn-primary w-full"
          >
            {loading ? (
              <span className="flex items-center justify-center gap-2">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white" />
                {isSignUp ? 'Creating account...' : 'Signing in...'}
              </span>
            ) : isSignUp ? (
              'Create account'
            ) : (
              'Sign in'
            )}
          </button>
        </form>

        <p className="text-center mt-4 text-sm text-gray-600">
          {isSignUp ? (
            <>
              Already have an account?{' '}
              <button
                onClick={() => setIsSignUp(false)}
                className="text-echo-600 hover:text-echo-700 font-medium"
              >
                Sign in
              </button>
            </>
          ) : (
            <>
              Don't have an account?{' '}
              <button
                onClick={() => setIsSignUp(true)}
                className="text-echo-600 hover:text-echo-700 font-medium"
              >
                Create one
              </button>
            </>
          )}
        </p>

        <div className="text-center mt-6">
          <Link to="/" className="text-sm text-gray-500 hover:text-gray-700">
            Continue without an account
          </Link>
        </div>
      </div>
    </div>
  );
}
