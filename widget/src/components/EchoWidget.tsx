/**
 * Main Echo Widget Component
 *
 * Drop this into any MedEd platform page to add the Echo tutor.
 *
 * @example
 * import { EchoWidget } from '@meded/echo-widget';
 * import '@meded/echo-widget/styles.css';
 *
 * <EchoWidget
 *   apiUrl="https://echo.meded.app"
 *   context={{ source: 'oread', patient: currentPatient }}
 * />
 */

import { useState, useCallback, useEffect, useRef } from 'react';
import type { EchoWidgetProps, EchoMessage, EchoMemoryItem } from '../types';
import { useEchoApi } from '../hooks/useEchoApi';
import { useEchoMemory } from '../hooks/useEchoMemory';
import { EchoIcon } from './EchoIcon';
import { EchoPanel } from './EchoPanel';
import { parseError } from './EchoError';

export function EchoWidget({
  apiUrl,
  context,
  defaultVoice = 'eryn',
  position = 'bottom-right',
  theme = 'light',
  onResponse,
  onToggle,
}: EchoWidgetProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<EchoMessage[]>([]);
  const [displayError, setDisplayError] = useState<string | null>(null);
  const [lastQuery, setLastQuery] = useState<string | null>(null);
  const voiceEnabled = false;  // Disabled for now
  const audioRef = useRef<HTMLAudioElement | null>(null);

  const { isLoading, error, askQuestion, speak, clearError } = useEchoApi({ apiUrl, context });
  const {
    memories,
    saveInteraction,
    toggleStar,
    deleteInteraction,
  } = useEchoMemory();

  // Sync API error to display error
  useEffect(() => {
    if (error) {
      setDisplayError(parseError(new Error(error)));
    }
  }, [error]);

  // Determine theme class
  const themeClass = theme === 'dark' ? 'dark' :
    theme === 'system' && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : '';

  const handleToggle = useCallback(() => {
    const newState = !isOpen;
    setIsOpen(newState);
    onToggle?.(newState);
  }, [isOpen, onToggle]);

  const handleSend = useCallback(async (text: string) => {
    // Clear any previous error
    setDisplayError(null);
    clearError();

    // Store query for retry
    setLastQuery(text);

    // Add user message
    const userMessage: EchoMessage = {
      id: crypto.randomUUID(),
      role: 'user',
      content: text,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMessage]);

    try {
      // Get response from Echo
      const response = await askQuestion(text);

      // Add Echo's response
      const echoMessage: EchoMessage = {
        id: crypto.randomUUID(),
        role: 'echo',
        content: response.message,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, echoMessage]);

      // Save to memory
      await saveInteraction(text, response.message, {
        source: context?.source,
        patientId: context?.patient?.patientId,
        patientName: context?.patient?.name,
      });

      // Notify parent
      onResponse?.(echoMessage);

      // Clear retry query on success
      setLastQuery(null);

      // Auto-speak if voice enabled
      if (voiceEnabled) {
        handleSpeak(response.message);
      }
    } catch (err) {
      // Mark the user message as failed
      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === userMessage.id ? { ...msg, failed: true } : msg
        )
      );

      // Set user-friendly error
      setDisplayError(parseError(err));
    }
  }, [askQuestion, saveInteraction, context, voiceEnabled, onResponse, clearError]);

  const handleRetry = useCallback(() => {
    if (lastQuery) {
      // Remove the failed message
      setMessages((prev) => prev.filter((msg) => !msg.failed));
      // Retry the last query
      handleSend(lastQuery);
    }
  }, [lastQuery, handleSend]);

  const handleClearError = useCallback(() => {
    setDisplayError(null);
    clearError();
  }, [clearError]);

  const handleSpeak = useCallback(async (text: string) => {
    try {
      const audioBlob = await speak(text, defaultVoice);
      const audioUrl = URL.createObjectURL(audioBlob);

      // Clean up previous audio
      if (audioRef.current) {
        audioRef.current.pause();
        URL.revokeObjectURL(audioRef.current.src);
      }

      // Play new audio
      audioRef.current = new Audio(audioUrl);
      audioRef.current.play();
    } catch (err) {
      console.error('TTS failed:', err);
    }
  }, [speak, defaultVoice]);

  const handleMemoryClick = useCallback((memory: EchoMemoryItem) => {
    // Restore conversation from memory
    const userMessage: EchoMessage = {
      id: crypto.randomUUID(),
      role: 'user',
      content: memory.query,
      timestamp: memory.timestamp,
    };
    const echoMessage: EchoMessage = {
      id: crypto.randomUUID(),
      role: 'echo',
      content: memory.response,
      timestamp: memory.timestamp,
    };
    setMessages([userMessage, echoMessage]);
  }, []);

  // Cleanup audio on unmount
  useEffect(() => {
    return () => {
      if (audioRef.current) {
        audioRef.current.pause();
        URL.revokeObjectURL(audioRef.current.src);
      }
    };
  }, []);

  return (
    <div className={`echo-widget ${themeClass}`}>
      <EchoIcon
        position={position}
        onClick={handleToggle}
        isOpen={isOpen}
      />

      {isOpen && (
        <EchoPanel
          position={position}
          messages={messages}
          memories={memories}
          isLoading={isLoading}
          error={displayError}
          onSend={handleSend}
          onClose={handleToggle}
          onRetry={lastQuery ? handleRetry : undefined}
          onClearError={handleClearError}
          onMemoryClick={handleMemoryClick}
          onMemoryStar={toggleStar}
          onMemoryDelete={deleteInteraction}
        />
      )}
    </div>
  );
}
