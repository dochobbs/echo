import { motion } from 'motion/react';
import type { DebriefData } from '../api/client';

interface DebriefCardProps {
  debrief: DebriefData;
  onNewCase: () => void;
}

export function DebriefCard({ debrief, onNewCase }: DebriefCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="card overflow-hidden"
    >
      <div className="bg-gradient-to-r from-echo-500/20 to-copper-500/20 px-6 py-4 border-b border-surface-3">
        <h3 className="text-lg font-semibold text-gray-100">Case Debrief 🎉</h3>
        <p className="mt-2 text-gray-300">{debrief.summary}</p>
      </div>

      <div className="p-6 space-y-6">
        {debrief.strengths.length > 0 && (
          <section>
            <h4 className="flex items-center gap-2 text-sm font-semibold text-echo-400 uppercase tracking-wide mb-3">
              <span>✓</span>
              What You Did Well
            </h4>
            <ul className="space-y-2">
              {debrief.strengths.map((item, i) => (
                <motion.li
                  key={i}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.1 }}
                  className="flex items-start gap-2 text-gray-300"
                >
                  <span className="text-echo-400 mt-0.5">+</span>
                  <span>{item}</span>
                </motion.li>
              ))}
            </ul>
          </section>
        )}

        {debrief.areas_for_improvement.length > 0 && (
          <section>
            <h4 className="flex items-center gap-2 text-sm font-semibold text-copper-400 uppercase tracking-wide mb-3">
              <span>↗</span>
              Areas to Grow
            </h4>
            <ul className="space-y-2">
              {debrief.areas_for_improvement.map((item, i) => (
                <motion.li
                  key={i}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.1 + 0.2 }}
                  className="flex items-start gap-2 text-gray-300"
                >
                  <span className="text-copper-400 mt-0.5">*</span>
                  <span>{item}</span>
                </motion.li>
              ))}
            </ul>
          </section>
        )}

        {debrief.missed_items.length > 0 && (
          <section>
            <h4 className="flex items-center gap-2 text-sm font-semibold text-red-400 uppercase tracking-wide mb-3">
              <span>!</span>
              Things to Catch Next Time
            </h4>
            <ul className="space-y-2">
              {debrief.missed_items.map((item, i) => (
                <motion.li
                  key={i}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.1 + 0.4 }}
                  className="flex items-start gap-2 text-gray-300"
                >
                  <span className="text-red-400 mt-0.5">!</span>
                  <span>{item}</span>
                </motion.li>
              ))}
            </ul>
          </section>
        )}

        {debrief.teaching_points.length > 0 && (
          <section>
            <h4 className="flex items-center gap-2 text-sm font-semibold text-echo-400 uppercase tracking-wide mb-3">
              <span>💡</span>
              Clinical Pearls
            </h4>
            <ul className="space-y-2">
              {debrief.teaching_points.map((item, i) => (
                <motion.li
                  key={i}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.1 + 0.6 }}
                  className="bg-surface-3 rounded-xl p-3 text-gray-300 border-l-4 border-echo-500"
                >
                  {item}
                </motion.li>
              ))}
            </ul>
          </section>
        )}

        {debrief.follow_up_resources.length > 0 && (
          <section>
            <h4 className="flex items-center gap-2 text-sm font-semibold text-gray-400 uppercase tracking-wide mb-3">
              <span>📚</span>
              Resources
            </h4>
            <ul className="space-y-1">
              {debrief.follow_up_resources.map((item, i) => (
                <li key={i} className="text-gray-500 text-sm">
                  {item}
                </li>
              ))}
            </ul>
          </section>
        )}
      </div>

      <div className="bg-surface-2 px-6 py-4 border-t border-surface-3">
        <motion.button
          onClick={onNewCase}
          className="btn btn-primary w-full py-3"
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          Start Another Case
        </motion.button>
      </div>
    </motion.div>
  );
}
