/**
 * Types for Its Hover animated icons
 * Source: https://github.com/itshover/itshover
 */

export interface AnimatedIconProps {
  size?: number | string;
  color?: string;
  strokeWidth?: number;
  className?: string;
}

export interface AnimatedIconHandle {
  startAnimation: () => void;
  stopAnimation: () => void;
}
