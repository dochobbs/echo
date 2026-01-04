import { motion } from 'motion/react';
import { ClipboardIcon, StethoscopeSimpleIcon, BrainIcon, FileTextIcon, CircleCheckIcon, CheckIcon } from './icons';
import type { ReactNode } from 'react';

interface CaseTimelineProps {
  currentPhase: string;
  compact?: boolean;
}

interface Phase {
  id: string;
  label: string;
  Icon: (props: { className?: string; size?: number; animate?: boolean }) => ReactNode;
}

const phases: Phase[] = [
  { id: 'history', label: 'History', Icon: ClipboardIcon },
  { id: 'examination', label: 'Exam', Icon: StethoscopeSimpleIcon },
  { id: 'differential', label: 'Differential', Icon: BrainIcon },
  { id: 'plan', label: 'Plan', Icon: FileTextIcon },
  { id: 'complete', label: 'Complete', Icon: CircleCheckIcon },
];

export function CaseTimeline({ currentPhase, compact = false }: CaseTimelineProps) {
  const currentIndex = phases.findIndex(p => p.id === currentPhase);

  return (
    <div className={`flex items-center ${compact ? 'gap-2' : 'gap-3'}`}>
      {phases.map((phase, index) => {
        const isComplete = index < currentIndex;
        const isCurrent = index === currentIndex;
        const Icon = phase.Icon;

        return (
          <div key={phase.id} className="flex items-center">
            <motion.div
              className={`relative flex items-center justify-center rounded-full transition-all duration-300 ${
                compact ? 'w-8 h-8' : 'w-10 h-10'
              } ${
                isComplete
                  ? 'bg-echo-500 text-white'
                  : isCurrent
                  ? 'bg-copper-500 text-white'
                  : 'bg-surface-3 text-gray-500 border border-surface-4'
              }`}
              animate={isCurrent ? {
                boxShadow: ['0 0 0px rgba(224, 123, 84, 0)', '0 0 20px rgba(224, 123, 84, 0.5)', '0 0 0px rgba(224, 123, 84, 0)'],
              } : {}}
              transition={isCurrent ? {
                duration: 2,
                repeat: Infinity,
                ease: "easeInOut",
              } : {}}
            >
              {isComplete ? (
                <CheckIcon size={compact ? 14 : 18} animate={false} />
              ) : (
                <Icon size={compact ? 14 : 18} animate={false} />
              )}
              
              {isCurrent && (
                <motion.div
                  className="absolute inset-0 rounded-full border-2 border-copper-400"
                  animate={{ scale: [1, 1.2, 1], opacity: [1, 0, 1] }}
                  transition={{ duration: 2, repeat: Infinity }}
                />
              )}
            </motion.div>

            {!compact && index < phases.length - 1 && (
              <div className="hidden sm:block w-8 h-0.5 mx-1">
                <motion.div
                  className="h-full rounded-full"
                  initial={{ width: 0 }}
                  animate={{ 
                    width: isComplete ? '100%' : '0%',
                    backgroundColor: isComplete ? '#0D9CB8' : '#27272a'
                  }}
                  transition={{ duration: 0.5, delay: index * 0.1 }}
                />
              </div>
            )}

            {index < phases.length - 1 && compact && (
              <div className={`w-3 h-0.5 mx-0.5 rounded-full ${isComplete ? 'bg-echo-500' : 'bg-surface-4'}`} />
            )}
          </div>
        );
      })}
    </div>
  );
}
