/**
 * Echo Widget Types
 */

/** Source platform for context */
export type EchoSource = 'oread' | 'syrinx' | 'mneme' | 'unknown';

/** Patient context passed from host app (widget-friendly format) */
export interface PatientContext {
  /** Required patient identifier */
  patientId: string;
  /** Source platform */
  source?: 'oread' | 'syrinx' | 'mneme';
  /** Patient name */
  name?: string;
  /** Age in years */
  age?: number;
  /** Sex */
  sex?: 'male' | 'female' | 'other';
  /** Chief complaint */
  chiefComplaint?: string;
  /** Active problems (simple strings) */
  problemList?: string[];
  /** Current medications (simple strings) */
  medications?: string[];
  /** Known allergies (simple strings) */
  allergies?: string[];
}

/** Encounter context for active sessions */
export interface EncounterContext {
  encounterId?: string;
  encounterType?: string;
  phase?: 'intake' | 'assessment' | 'plan' | 'complete';
}

/** Combined context from host app */
export interface EchoContext {
  source: EchoSource;
  patient?: PatientContext;
  encounter?: EncounterContext;
  learnerLevel?: 'student' | 'resident' | 'np_student' | 'fellow';
}

/** Voice options for TTS */
export type EchoVoice = 'eryn' | 'matilda' | 'clarice' | 'clara' | 'devan' | 'lilly';

/** A single message in the conversation */
export interface EchoMessage {
  id: string;
  role: 'user' | 'echo';
  content: string;
  timestamp: Date;
  audioUrl?: string;  // TTS audio URL if generated
}

/** A saved interaction in memory */
export interface EchoMemoryItem {
  id: string;
  timestamp: Date;
  query: string;
  response: string;
  context?: {
    source: EchoSource;
    patientId?: string;
    patientName?: string;
  };
  tags?: string[];
  starred?: boolean;
}

/** Props for the main EchoWidget component */
export interface EchoWidgetProps {
  /** Echo API base URL */
  apiUrl: string;

  /** Context from host app */
  context?: EchoContext;

  /** Default voice for TTS */
  defaultVoice?: EchoVoice;

  /** Enable voice mode by default */
  voiceEnabled?: boolean;

  /** Position of the widget */
  position?: 'bottom-right' | 'bottom-left' | 'top-right' | 'top-left';

  /** Custom icon/avatar URL */
  iconUrl?: string;

  /** Theme override */
  theme?: 'light' | 'dark' | 'system';

  /** Callback when Echo responds */
  onResponse?: (message: EchoMessage) => void;

  /** Callback when widget opens/closes */
  onToggle?: (isOpen: boolean) => void;
}

/** API request for feedback */
export interface FeedbackRequest {
  patient?: PatientContext;
  learner_action: string;
  action_type: 'question' | 'diagnosis' | 'order' | 'plan' | 'documentation';
  learner_level: string;
  context?: string;
}

/** API response from Echo */
export interface FeedbackResponse {
  message: string;
  mode: 'socratic' | 'feedback' | 'direct';
  follow_up?: string;
  references?: string[];
}

/** API request for Socratic question */
export interface QuestionRequest {
  patient?: PatientContext;
  learner_question: string;
  encounter_state?: string;
}

/** Voice speak request */
export interface SpeakRequest {
  text: string;
  voice?: EchoVoice;
}

/** Available voice info */
export interface VoiceInfo {
  name: string;
  voice_id: string;
  is_default: boolean;
}
