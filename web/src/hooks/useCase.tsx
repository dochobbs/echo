import { createContext, useContext, useState, useCallback, ReactNode } from 'react';
import { api, BackendCaseState, BackendCaseResponse, DebriefData } from '../api/client';
import type { LearnerLevel, Message, CasePhase } from '../types';

interface CaseContextType {
  caseState: BackendCaseState | null;
  messages: Message[];
  loading: boolean;
  error: string | null;
  debrief: DebriefData | null;
  startCase: (options?: { level?: LearnerLevel; condition?: string }) => Promise<BackendCaseResponse>;
  sendMessage: (message: string) => Promise<BackendCaseResponse>;
  endCase: () => Promise<BackendCaseResponse>;
  clearError: () => void;
  resetCase: () => void;
}

const CaseContext = createContext<CaseContextType | undefined>(undefined);

export function CaseProvider({ children }: { children: ReactNode }) {
  const [caseState, setCaseState] = useState<BackendCaseState | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [debrief, setDebrief] = useState<DebriefData | null>(null);

  const startCase = useCallback(async (options?: { level?: LearnerLevel; condition?: string }) => {
    setLoading(true);
    setError(null);
    setDebrief(null);  // Clear any previous debrief

    try {
      const response = await api.startCase({
        learner_level: options?.level || 'student',
        condition_key: options?.condition,
      });

      setCaseState(response.case_state);

      const initialMessage: Message = {
        id: crypto.randomUUID(),
        session_id: response.case_state.session_id,
        role: 'echo',
        content: response.message,
        phase: response.case_state.phase as CasePhase,
        created_at: new Date().toISOString(),
      };

      setMessages([initialMessage]);
      return response;
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Failed to start case';
      setError(msg);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const sendMessage = useCallback(async (message: string) => {
    if (!caseState) throw new Error('No active case');

    const userMessage: Message = {
      id: crypto.randomUUID(),
      session_id: caseState.session_id,
      role: 'user',
      content: message,
      phase: caseState.phase as CasePhase,
      created_at: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setLoading(true);
    setError(null);

    try {
      const response = await api.sendMessage({
        message,
        case_state: caseState,
      });

      setCaseState(response.case_state);

      const echoMessage: Message = {
        id: crypto.randomUUID(),
        session_id: response.case_state.session_id,
        role: 'echo',
        content: response.message,
        phase: response.case_state.phase as CasePhase,
        created_at: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, echoMessage]);
      return response;
    } catch (err) {
      setMessages((prev) =>
        prev.map((m) => (m.id === userMessage.id ? { ...m, failed: true } : m))
      );
      const msg = err instanceof Error ? err.message : 'Failed to send message';
      setError(msg);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [caseState]);

  const endCase = useCallback(async () => {
    if (!caseState) throw new Error('No active case');

    setLoading(true);
    setError(null);

    try {
      const response = await api.getDebrief(caseState);
      setCaseState(response.case_state);

      // Save structured debrief data
      if (response.debrief) {
        setDebrief(response.debrief);
      }

      const debriefMessage: Message = {
        id: crypto.randomUUID(),
        session_id: caseState.session_id,
        role: 'echo',
        content: response.message,
        phase: 'complete',
        created_at: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, debriefMessage]);
      return response;
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Failed to end case';
      setError(msg);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [caseState]);

  const clearError = useCallback(() => setError(null), []);

  const resetCase = useCallback(() => {
    setCaseState(null);
    setMessages([]);
    setError(null);
    setDebrief(null);
  }, []);

  return (
    <CaseContext.Provider
      value={{
        caseState,
        messages,
        loading,
        error,
        debrief,
        startCase,
        sendMessage,
        endCase,
        clearError,
        resetCase,
      }}
    >
      {children}
    </CaseContext.Provider>
  );
}

export function useCase() {
  const context = useContext(CaseContext);
  if (context === undefined) {
    throw new Error('useCase must be used within a CaseProvider');
  }
  return context;
}
