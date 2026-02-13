import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'motion/react';
import { useCase } from '../hooks/useCase';
import type { LearnerLevel } from '../types';
import type { VisitType } from '../types/case';

const WELL_CHILD_AGES = [
  { months: 0, label: 'Newborn', subtitle: 'Metabolic screen, HepB, safe sleep' },
  { months: 2, label: '2 Months', subtitle: 'First big vaccine visit, maternal depression' },
  { months: 4, label: '4 Months', subtitle: 'Vaccine series #2, rolling milestones' },
  { months: 6, label: '6 Months', subtitle: 'Complementary foods, flu vaccine starts' },
  { months: 9, label: '9 Months', subtitle: 'ASQ-3 screening, finger foods' },
  { months: 12, label: '12 Months', subtitle: 'MMR/Varicella, lead/anemia screen' },
  { months: 15, label: '15 Months', subtitle: 'Walking milestone, DTaP #4' },
  { months: 18, label: '18 Months', subtitle: 'M-CHAT autism screen, HepA #2' },
  { months: 24, label: '2 Years', subtitle: 'BMI starts, toilet training' },
  { months: 36, label: '3 Years', subtitle: 'BP screening begins, vision' },
  { months: 48, label: '4 Years', subtitle: 'Pre-K vaccines, school readiness' },
  { months: 60, label: '5 Years', subtitle: 'Kindergarten readiness, catch-up' },
  { months: 144, label: 'Adolescent', subtitle: 'HPV, HEEADSSS, depression screen' },
];

export function Home() {
  const navigate = useNavigate();
  const { startCase, loading, error } = useCase();
  const [level, setLevel] = useState<LearnerLevel>('student');
  const [visitType, setVisitType] = useState<VisitType>('sick');
  const [selectedAge, setSelectedAge] = useState<number | null>(null);

  const handleStartCase = async () => {
    try {
      if (visitType === 'well_child' && selectedAge !== null) {
        await startCase({ level, visitType: 'well_child', visitAgeMonths: selectedAge });
      } else {
        await startCase({ level });
      }
      navigate('/case');
    } catch {
    }
  };

  const canStart = visitType === 'sick' || (visitType === 'well_child' && selectedAge !== null);

  return (
    <div className="max-w-2xl mx-auto px-4 py-12 md:py-20">
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

        <div className="card p-4">
          <label className="block text-sm font-medium text-gray-400 mb-3">
            Visit type
          </label>
          <div className="grid grid-cols-2 gap-2">
            <button
              onClick={() => { setVisitType('sick'); setSelectedAge(null); }}
              className={`px-4 py-3 rounded-xl text-sm font-medium transition-all ${
                visitType === 'sick'
                  ? 'bg-blue-500/20 text-blue-300 border border-blue-500/40'
                  : 'bg-gray-800 text-gray-400 border border-gray-700 hover:border-gray-600'
              }`}
            >
              Sick Visit
            </button>
            <button
              onClick={() => setVisitType('well_child')}
              className={`px-4 py-3 rounded-xl text-sm font-medium transition-all ${
                visitType === 'well_child'
                  ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40'
                  : 'bg-gray-800 text-gray-400 border border-gray-700 hover:border-gray-600'
              }`}
            >
              Well-Child Visit
            </button>
          </div>
        </div>

        {visitType === 'well_child' && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="card p-4"
          >
            <label className="block text-sm font-medium text-gray-400 mb-3">
              Visit age
            </label>
            <div className="grid grid-cols-2 gap-2 max-h-80 overflow-y-auto">
              {WELL_CHILD_AGES.map((age) => (
                <button
                  key={age.months}
                  onClick={() => setSelectedAge(age.months)}
                  className={`text-left px-3 py-2.5 rounded-lg text-sm transition-all ${
                    selectedAge === age.months
                      ? 'bg-emerald-500/20 text-emerald-200 border border-emerald-500/40'
                      : 'bg-gray-800/50 text-gray-300 border border-gray-700/50 hover:border-gray-600'
                  }`}
                >
                  <div className="font-medium">{age.label}</div>
                  <div className="text-xs text-gray-500 mt-0.5 line-clamp-1">{age.subtitle}</div>
                </button>
              ))}
            </div>
          </motion.div>
        )}

        <motion.button
          onClick={handleStartCase}
          disabled={loading || !canStart}
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
          ) : visitType === 'well_child' ? (
            selectedAge !== null
              ? `Start Well-Child Visit`
              : 'Select a visit age'
          ) : (
            'Start Sick Visit'
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
