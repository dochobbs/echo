import { motion } from 'motion/react';
import type { DebriefData, WellChildDomainScore } from '../api/client';

interface DebriefCardProps {
  debrief: DebriefData;
  onNewCase: () => void;
}

const DOMAIN_LABELS: Record<string, string> = {
  growth_interpretation: 'Growth Interpretation',
  milestone_assessment: 'Milestone Assessment',
  exam_thoroughness: 'Exam Thoroughness',
  anticipatory_guidance: 'Anticipatory Guidance',
  immunization_knowledge: 'Immunization Knowledge',
  communication_skill: 'Communication Skill',
};

function scoreColor(score: number): string {
  if (score >= 8) return 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30';
  if (score >= 5) return 'text-yellow-400 bg-yellow-500/10 border-yellow-500/30';
  return 'text-red-400 bg-red-500/10 border-red-500/30';
}

function DomainScoreCard({ domain, score }: { domain: string; score: WellChildDomainScore }) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className={`rounded-xl border p-3 ${scoreColor(score.score)}`}
    >
      <div className="flex items-center justify-between mb-1">
        <span className="text-xs font-semibold uppercase tracking-wide opacity-80">
          {DOMAIN_LABELS[domain] || domain}
        </span>
        <span className="text-lg font-bold">{score.score}/10</span>
      </div>
      <p className="text-xs text-gray-400 leading-relaxed">{score.feedback}</p>
    </motion.div>
  );
}

export function DebriefCard({ debrief, onNewCase }: DebriefCardProps) {
  const hasWellChildScores = !!debrief.well_child_scores;

  const avgScore = hasWellChildScores
    ? Math.round(
        Object.values(debrief.well_child_scores!).reduce((sum, d) => sum + d.score, 0) / 6 * 10
      ) / 10
    : null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="card overflow-hidden"
    >
      <div className={`px-6 py-4 border-b border-surface-3 ${
        hasWellChildScores
          ? 'bg-gradient-to-r from-emerald-500/20 to-echo-500/20'
          : 'bg-gradient-to-r from-echo-500/20 to-copper-500/20'
      }`}>
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-100">
            {hasWellChildScores ? 'Well-Child Visit Debrief' : 'Case Debrief'}
          </h3>
          {avgScore !== null && (
            <span className={`text-2xl font-bold ${
              avgScore >= 8 ? 'text-emerald-400' : avgScore >= 5 ? 'text-yellow-400' : 'text-red-400'
            }`}>
              {avgScore}/10
            </span>
          )}
        </div>
        <p className="mt-2 text-gray-300">{debrief.summary}</p>
      </div>

      <div className="p-6 space-y-6">
        {hasWellChildScores && (
          <section>
            <h4 className="text-sm font-semibold text-emerald-400 uppercase tracking-wide mb-3">
              Domain Scores
            </h4>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {Object.entries(debrief.well_child_scores!).map(([domain, score]) => (
                <DomainScoreCard key={domain} domain={domain} score={score as WellChildDomainScore} />
              ))}
            </div>
          </section>
        )}
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
