import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
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
      // Error handled by hook
    }
  };

  const handleDescribeCase = () => {
    navigate('/describe');
  };

  return (
    <div className="max-w-md mx-auto px-4 py-16 text-center">
      <h1 className="text-2xl font-semibold text-gray-900 mb-2">
        Ready to run a case?
      </h1>
      
      <p className="text-gray-500 mb-8">
        I'm Echo, your AI attending.
      </p>

      <div className="space-y-4">
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

        <button
          onClick={handleStartCase}
          disabled={loading}
          className="btn btn-primary w-full py-3"
        >
          {loading ? 'Starting...' : 'Start Case'}
        </button>

        <button
          onClick={handleDescribeCase}
          className="btn btn-secondary w-full py-3"
        >
          Describe Your Case
        </button>
      </div>

      {error && (
        <p className="mt-4 text-sm text-red-600">{error}</p>
      )}
    </div>
  );
}
