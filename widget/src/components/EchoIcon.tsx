/**
 * Floating icon button to summon Echo
 */

import { MessageCircleIcon, XIcon } from '../icons';
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
        <XIcon size={28} color="white" />
      ) : (
        <MessageCircleIcon size={28} color="white" />
      )}
    </button>
  );
}
