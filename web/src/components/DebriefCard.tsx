import type { DebriefData } from '../api/client';

interface DebriefCardProps {
  debrief: DebriefData;
  onNewCase: () => void;
}

export function DebriefCard({ debrief, onNewCase }: DebriefCardProps) {
  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
      {/* Summary Header */}
      <div className="bg-echo-50 px-6 py-4 border-b border-echo-100">
        <h3 className="text-lg font-semibold text-echo-900">Case Debrief</h3>
        <p className="mt-2 text-gray-700">{debrief.summary}</p>
      </div>

      <div className="p-6 space-y-6">
        {/* Strengths */}
        {debrief.strengths.length > 0 && (
          <section>
            <h4 className="flex items-center gap-2 text-sm font-semibold text-green-700 uppercase tracking-wide mb-3">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              What You Did Well
            </h4>
            <ul className="space-y-2">
              {debrief.strengths.map((item, i) => (
                <li key={i} className="flex items-start gap-2 text-gray-700">
                  <span className="text-green-500 mt-1">+</span>
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          </section>
        )}

        {/* Areas for Improvement */}
        {debrief.areas_for_improvement.length > 0 && (
          <section>
            <h4 className="flex items-center gap-2 text-sm font-semibold text-amber-700 uppercase tracking-wide mb-3">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
              </svg>
              Areas to Grow
            </h4>
            <ul className="space-y-2">
              {debrief.areas_for_improvement.map((item, i) => (
                <li key={i} className="flex items-start gap-2 text-gray-700">
                  <span className="text-amber-500 mt-1">*</span>
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          </section>
        )}

        {/* Missed Items */}
        {debrief.missed_items.length > 0 && (
          <section>
            <h4 className="flex items-center gap-2 text-sm font-semibold text-red-700 uppercase tracking-wide mb-3">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
              Things to Catch Next Time
            </h4>
            <ul className="space-y-2">
              {debrief.missed_items.map((item, i) => (
                <li key={i} className="flex items-start gap-2 text-gray-700">
                  <span className="text-red-500 mt-1">!</span>
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          </section>
        )}

        {/* Teaching Points */}
        {debrief.teaching_points.length > 0 && (
          <section>
            <h4 className="flex items-center gap-2 text-sm font-semibold text-echo-700 uppercase tracking-wide mb-3">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
              Clinical Pearls
            </h4>
            <ul className="space-y-2">
              {debrief.teaching_points.map((item, i) => (
                <li key={i} className="bg-echo-50 rounded-lg p-3 text-gray-700 border-l-4 border-echo-400">
                  {item}
                </li>
              ))}
            </ul>
          </section>
        )}

        {/* Follow-up Resources */}
        {debrief.follow_up_resources.length > 0 && (
          <section>
            <h4 className="flex items-center gap-2 text-sm font-semibold text-gray-600 uppercase tracking-wide mb-3">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
              </svg>
              Resources
            </h4>
            <ul className="space-y-1">
              {debrief.follow_up_resources.map((item, i) => (
                <li key={i} className="text-gray-600 text-sm">
                  {item}
                </li>
              ))}
            </ul>
          </section>
        )}
      </div>

      {/* Action Footer */}
      <div className="bg-gray-50 px-6 py-4 border-t border-gray-200">
        <button
          onClick={onNewCase}
          className="btn btn-primary w-full"
        >
          Start Another Case
        </button>
      </div>
    </div>
  );
}
