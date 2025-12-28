/**
 * Hook for interacting with Echo API
 */

import { useState, useCallback } from 'react';
import type {
  FeedbackRequest,
  FeedbackResponse,
  QuestionRequest,
  SpeakRequest,
  VoiceInfo,
  EchoContext,
} from '../types';

interface UseEchoApiOptions {
  apiUrl: string;
  context?: EchoContext;
}

interface UseEchoApiReturn {
  isLoading: boolean;
  error: string | null;
  askQuestion: (question: string) => Promise<FeedbackResponse>;
  getFeedback: (action: string, actionType: FeedbackRequest['action_type']) => Promise<FeedbackResponse>;
  speak: (text: string, voice?: string) => Promise<Blob>;
  getVoices: () => Promise<VoiceInfo[]>;
  clearError: () => void;
}

export function useEchoApi({ apiUrl, context }: UseEchoApiOptions): UseEchoApiReturn {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const baseUrl = apiUrl.replace(/\/$/, '');

  const askQuestion = useCallback(async (question: string): Promise<FeedbackResponse> => {
    setIsLoading(true);
    setError(null);

    try {
      const request: QuestionRequest = {
        learner_question: question,
        patient: context?.patient,
        encounter_state: context?.encounter?.phase,
      };

      const response = await fetch(`${baseUrl}/question`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      return await response.json();
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Unknown error';
      setError(message);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [baseUrl, context]);

  const getFeedback = useCallback(async (
    action: string,
    actionType: FeedbackRequest['action_type']
  ): Promise<FeedbackResponse> => {
    setIsLoading(true);
    setError(null);

    try {
      const request: FeedbackRequest = {
        learner_action: action,
        action_type: actionType,
        learner_level: context?.learnerLevel || 'student',
        patient: context?.patient,
      };

      const response = await fetch(`${baseUrl}/feedback`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      return await response.json();
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Unknown error';
      setError(message);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [baseUrl, context]);

  const speak = useCallback(async (text: string, voice?: string): Promise<Blob> => {
    const request: SpeakRequest = { text, voice: voice as SpeakRequest['voice'] };

    const response = await fetch(`${baseUrl}/voice/speak`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      throw new Error(`TTS error: ${response.status}`);
    }

    return await response.blob();
  }, [baseUrl]);

  const getVoices = useCallback(async (): Promise<VoiceInfo[]> => {
    const response = await fetch(`${baseUrl}/voice/voices`);
    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }
    return await response.json();
  }, [baseUrl]);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    isLoading,
    error,
    askQuestion,
    getFeedback,
    speak,
    getVoices,
    clearError,
  };
}
