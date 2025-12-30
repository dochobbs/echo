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

export function EchoWidget({
  apiUrl,
  context,
  defaultVoice = 'eryn',
  // voiceEnabled: initialVoiceEnabled = false,  // TODO: Re-enable when TTS implemented
  position = 'bottom-right',
  theme = 'light',
  onResponse,
  onToggle,
}: EchoWidgetProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<EchoMessage[]>([]);
  // TODO: Re-enable when TTS implemented
  // const [voiceEnabled, setVoiceEnabled] = useState(initialVoiceEnabled);
  const voiceEnabled = false;  // Disabled for now
  const audioRef = useRef<HTMLAudioElement | null>(null);

  const { isLoading, askQuestion, speak } = useEchoApi({ apiUrl, context });
  const {
    memories,
    saveInteraction,
    toggleStar,
    deleteInteraction,
  } = useEchoMemory();

  // Determine theme class
  const themeClass = theme === 'dark' ? 'dark' :
    theme === 'system' && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : '';

  const handleToggle = useCallback(() => {
    const newState = !isOpen;
    setIsOpen(newState);
    onToggle?.(newState);
  }, [isOpen, onToggle]);

  const handleSend = useCallback(async (text: string) => {
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

      // Auto-speak if voice enabled
      if (voiceEnabled) {
        handleSpeak(response.message);
      }
    } catch (err) {
      // Add error message
      const errorMessage: EchoMessage = {
        id: crypto.randomUUID(),
        role: 'echo',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    }
  }, [askQuestion, saveInteraction, context, voiceEnabled, onResponse]);

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
          // voiceEnabled={voiceEnabled}  // TODO: Re-enable when TTS implemented
          // defaultVoice={defaultVoice}  // TODO: Re-enable when TTS implemented
          onSend={handleSend}
          // onSpeak={handleSpeak}  // TODO: Re-enable when TTS implemented
          onClose={handleToggle}
          // onToggleVoice={() => setVoiceEnabled(!voiceEnabled)}  // TODO: Re-enable when TTS implemented
          onMemoryClick={handleMemoryClick}
          onMemoryStar={toggleStar}
          onMemoryDelete={deleteInteraction}
        />
      )}
    </div>
  );
}
