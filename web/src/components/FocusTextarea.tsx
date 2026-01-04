import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'motion/react';

interface FocusTextareaProps {
  value: string;
  onChange: (value: string) => void;
  onSubmit: () => void;
  placeholder?: string;
  disabled?: boolean;
}

export function FocusTextarea({ 
  value, 
  onChange, 
  onSubmit,
  placeholder = "Describe your case...",
  disabled = false 
}: FocusTextareaProps) {
  const [isFocused, setIsFocused] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const isActive = isFocused || value.length > 0;

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 200)}px`;
    }
  }, [value]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      onSubmit();
    }
    if (e.key === 'Escape') {
      textareaRef.current?.blur();
    }
  };

  return (
    <>
      <AnimatePresence>
        {isActive && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="fixed inset-0 bg-surface-0/80 backdrop-blur-sm z-40 pointer-events-none"
          />
        )}
      </AnimatePresence>

      <motion.div
        className={`relative z-50 transition-all duration-300 ${
          isActive ? 'scale-[1.02]' : ''
        }`}
        animate={{
          boxShadow: isActive 
            ? '0 0 40px rgba(13, 156, 184, 0.3)' 
            : '0 0 0px rgba(13, 156, 184, 0)',
        }}
        style={{ borderRadius: '16px' }}
      >
        <textarea
          ref={textareaRef}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          disabled={disabled}
          rows={3}
          className={`w-full px-5 py-4 bg-surface-2 border rounded-2xl text-gray-100 placeholder-gray-500 resize-none transition-all duration-300 focus:outline-none ${
            isActive 
              ? 'border-echo-500 ring-2 ring-echo-500/30' 
              : 'border-surface-4 hover:border-surface-3'
          }`}
        />
        
        <div className="absolute bottom-3 right-3 flex items-center gap-2">
          <span className="text-xs text-gray-500">
            {value.length > 0 ? `${value.length} chars` : 'Shift+Enter for new line'}
          </span>
        </div>
      </motion.div>
    </>
  );
}
