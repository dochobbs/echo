import { motion } from 'motion/react';
import type { Message } from '../types';

interface MessageBubbleProps {
  message: Message;
  index: number;
}

export function MessageBubble({ message, index }: MessageBubbleProps) {
  const isUser = message.role === 'user';

  return (
    <motion.div
      initial={{ opacity: 0, y: 10, x: isUser ? 10 : -10 }}
      animate={{ opacity: 1, y: 0, x: 0 }}
      transition={{ 
        duration: 0.3, 
        delay: index * 0.05,
        ease: "easeOut" 
      }}
      className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}
    >
      <div
        className={`max-w-[80%] rounded-2xl px-4 py-3 ${
          isUser
            ? 'bg-echo-500 text-white'
            : 'bg-surface-3 text-gray-100 border border-surface-4'
        } ${message.failed ? 'opacity-50' : ''}`}
      >
        <p className="whitespace-pre-wrap leading-relaxed">{message.content}</p>
        {message.failed && (
          <p className="text-xs mt-1 text-red-300">Failed to send</p>
        )}
      </div>
    </motion.div>
  );
}
