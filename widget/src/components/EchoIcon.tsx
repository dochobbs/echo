/**
 * Floating icon button to summon Echo
 */

import { GraduationCap, X } from 'lucide-react';
import type { EchoWidgetProps } from '../types';

interface EchoIconProps {
  position: EchoWidgetProps['position'];
  onClick: () => void;
  isOpen: boolean;
}

export function EchoIcon({ position = 'bottom-right', onClick, isOpen }: EchoIconProps) {
  return (
    <button
      className={`echo-icon ${position}`}
      onClick={onClick}
      aria-label={isOpen ? 'Close Echo' : 'Open Echo'}
      title={isOpen ? 'Close Echo' : 'Ask Echo'}
    >
      {isOpen ? (
        <X size={28} color="white" />
      ) : (
        <GraduationCap size={28} color="white" />
      )}
    </button>
  );
}
