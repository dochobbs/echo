import { motion, AnimatePresence } from 'motion/react';
import { useEffect } from 'react';

interface ToastProps {
  message: string;
  type?: 'success' | 'error' | 'info' | 'milestone';
  isVisible: boolean;
  onClose: () => void;
  duration?: number;
}

const toastStyles = {
  success: 'bg-echo-500 text-white border-echo-400',
  error: 'bg-red-500 text-white border-red-400',
  info: 'bg-surface-3 text-gray-100 border-surface-4',
  milestone: 'bg-copper-500 text-white border-copper-400',
};

const toastIcons = {
  success: '✓',
  error: '✕',
  info: 'ℹ',
  milestone: '🎉',
};

export function Toast({ message, type = 'info', isVisible, onClose, duration = 4000 }: ToastProps) {
  useEffect(() => {
    if (isVisible && duration > 0) {
      const timer = setTimeout(onClose, duration);
      return () => clearTimeout(timer);
    }
  }, [isVisible, duration, onClose]);

  return (
    <AnimatePresence>
      {isVisible && (
        <motion.div
          initial={{ opacity: 0, y: -20, scale: 0.95 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={{ opacity: 0, y: -20, scale: 0.95 }}
          transition={{ duration: 0.2, ease: "easeOut" }}
          className={`fixed top-4 left-1/2 -translate-x-1/2 z-[100] flex items-center gap-3 px-4 py-3 rounded-xl border shadow-elevated ${toastStyles[type]}`}
        >
          <span className="text-lg">{toastIcons[type]}</span>
          <span className="font-medium text-sm">{message}</span>
          <button
            onClick={onClose}
            className="ml-2 opacity-70 hover:opacity-100 transition-opacity"
          >
            ✕
          </button>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
