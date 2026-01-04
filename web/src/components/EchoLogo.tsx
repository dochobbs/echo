import { motion } from 'motion/react';

interface EchoLogoProps {
  size?: number;
  className?: string;
}

export function EchoLogo({ size = 36, className = '' }: EchoLogoProps) {
  return (
    <motion.svg
      width={size}
      height={size}
      viewBox="0 0 48 48"
      fill="none"
      className={className}
      whileHover={{ scale: 1.05, rotate: 3 }}
      whileTap={{ scale: 0.95 }}
    >
      <defs>
        <linearGradient id="echoGradient" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#14b8a6" />
          <stop offset="50%" stopColor="#0D9CB8" />
          <stop offset="100%" stopColor="#0891b2" />
        </linearGradient>
        <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
          <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
          <feMerge>
            <feMergeNode in="coloredBlur"/>
            <feMergeNode in="SourceGraphic"/>
          </feMerge>
        </filter>
      </defs>
      
      <motion.rect
        x="2"
        y="2"
        width="44"
        height="44"
        rx="12"
        fill="url(#echoGradient)"
        filter="url(#glow)"
        initial={{ scale: 0, rotate: -180 }}
        animate={{ scale: 1, rotate: 0 }}
        transition={{ type: "spring", stiffness: 200, damping: 15 }}
      />
      
      <motion.g
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2, duration: 0.3 }}
      >
        <motion.path
          d="M16 14H32V18H20V22H30V26H20V30H32V34H16V14Z"
          fill="white"
          initial={{ pathLength: 0 }}
          animate={{ pathLength: 1 }}
          transition={{ delay: 0.3, duration: 0.5 }}
        />
      </motion.g>

      <motion.circle
        cx="38"
        cy="10"
        r="4"
        fill="#E07B54"
        initial={{ scale: 0 }}
        animate={{ scale: [0, 1.2, 1] }}
        transition={{ delay: 0.5, duration: 0.4 }}
      />

      <motion.circle
        cx="38"
        cy="10"
        r="2"
        fill="white"
        opacity="0.6"
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        transition={{ delay: 0.7, duration: 0.2 }}
      />
    </motion.svg>
  );
}
