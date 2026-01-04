import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { motion } from 'motion/react';
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
    <div className="min-h-screen flex items-center justify-center px-4 py-12">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="max-w-md w-full"
      >
        <div className="text-center mb-8">
          <motion.div
            className="w-16 h-16 bg-gradient-to-br from-echo-500 to-echo-600 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-glow"
            whileHover={{ scale: 1.05, rotate: 5 }}
          >
            <span className="text-white font-bold text-2xl">E</span>
          </motion.div>
          <h1 className="text-2xl font-bold text-gray-100">
            {isSignUp ? 'Create your account' : 'Welcome back'}
          </h1>
          <p className="text-gray-500 mt-2">
            {isSignUp
              ? 'Start learning with Echo'
              : 'Sign in to continue your learning'}
          </p>
        </div>

        <form onSubmit={handleSubmit} className="card p-6 space-y-4">
          {isSignUp && (
            <div>
              <label className="block text-sm font-medium text-gray-400 mb-1">
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
            <label className="block text-sm font-medium text-gray-400 mb-1">
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
            <label className="block text-sm font-medium text-gray-400 mb-1">
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
              <label className="block text-sm font-medium text-gray-400 mb-1">
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
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-red-500/10 border border-red-500/20 rounded-xl p-3"
            >
              <p className="text-sm text-red-400">{error}</p>
            </motion.div>
          )}

          <motion.button
            type="submit"
            disabled={loading}
            className="btn btn-primary w-full py-3"
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            {loading ? (
              <span className="flex items-center justify-center gap-2">
                <motion.span
                  animate={{ rotate: 360 }}
                  transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                >
                  ⟳
                </motion.span>
                {isSignUp ? 'Creating account...' : 'Signing in...'}
              </span>
            ) : isSignUp ? (
              'Create account'
            ) : (
              'Sign in'
            )}
          </motion.button>
        </form>

        <p className="text-center mt-6 text-sm text-gray-500">
          {isSignUp ? (
            <>
              Already have an account?{' '}
              <button
                onClick={() => setIsSignUp(false)}
                className="text-echo-400 hover:text-echo-300 font-medium transition-colors"
              >
                Sign in
              </button>
            </>
          ) : (
            <>
              Don't have an account?{' '}
              <button
                onClick={() => setIsSignUp(true)}
                className="text-echo-400 hover:text-echo-300 font-medium transition-colors"
              >
                Create one
              </button>
            </>
          )}
        </p>

        <div className="text-center mt-6">
          <Link to="/" className="text-sm text-gray-600 hover:text-gray-400 transition-colors">
            Continue without an account
          </Link>
        </div>
      </motion.div>
    </div>
  );
}
