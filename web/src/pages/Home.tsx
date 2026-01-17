import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'motion/react';
import { useCase } from '../hooks/useCase';
import type { LearnerLevel } from '../types';

export function Home() {
  const navigate = useNavigate();
  const { startCase, loading, error } = useCase();
  const [level, setLevel] = useState<LearnerLevel>('student');

  const handleStartCase = async () => {
    try {
      await startCase({ level });
      navigate('/case');
    } catch {
    }
  };

  return (
    <div className="max-w-lg mx-auto px-4 py-12 md:py-20">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="text-center mb-10"
      >
        <h1 className="text-3xl md:text-4xl font-semibold text-gray-100 mb-3 tracking-tight">
          Ready to <span className="text-gradient">run a case</span>?
        </h1>
        
        <p className="text-gray-400 text-lg">
          I'm Echo, your AI attending.
        </p>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.1 }}
        className="space-y-6"
      >
        <div className="card p-4">
          <label className="block text-sm font-medium text-gray-400 mb-2">
            Your level
          </label>
          <select
            value={level}
            onChange={(e) => setLevel(e.target.value as LearnerLevel)}
            className="input text-center"
          >
            <option value="student">Medical Student</option>
            <option value="np_student">NP Student</option>
            <option value="resident">Resident</option>
            <option value="fellow">Fellow</option>
            <option value="attending">Attending</option>
          </select>
        </div>

        <motion.button
          onClick={handleStartCase}
          disabled={loading}
          className="btn btn-primary w-full py-4 text-base"
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
              Starting...
            </span>
          ) : (
            'Start Case'
          )}
        </motion.button>
      </motion.div>

      {error && (
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="mt-6 text-sm text-red-400 text-center bg-red-500/10 rounded-xl py-3 px-4"
        >
          {error}
        </motion.p>
      )}

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5 }}
        className="mt-12 text-center"
      >
        <p className="text-xs text-gray-600">
          Practice with AI-generated cases
        </p>
      </motion.div>
    </div>
  );
}
