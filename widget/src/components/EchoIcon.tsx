/**
 * Floating icon button to summon Echo
 */

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
        // X icon when open
        <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path d="M18 6L6 18M6 6l12 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" fill="none"/>
        </svg>
      ) : (
        // Graduation cap / tutor icon when closed
        <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path d="M12 3L1 9l11 6 9-4.91V17h2V9L12 3z"/>
          <path d="M5 13.18v4L12 21l7-3.82v-4L12 17l-7-3.82z"/>
        </svg>
      )}
    </button>
  );
}
