// User types
export type LearnerLevel = 'student' | 'resident' | 'np_student' | 'fellow' | 'attending';

export interface User {
  id: string;
  email: string;
  name?: string;
  level: LearnerLevel;
  specialty_interest?: string;
  institution?: string;
  created_at: string;
  last_active: string;
  preferences: Record<string, unknown>;
}

export interface UserStats {
  total_cases: number;
  completed_cases: number;
  unique_conditions: number;
  avg_duration_seconds?: number;
  last_case_completed?: string;
}

// Case types
export type CaseStatus = 'active' | 'completed' | 'abandoned';
export type CasePhase = 'intro' | 'history' | 'exam' | 'assessment' | 'plan' | 'complete';

export interface CaseSession {
  id: string;
  user_id?: string;
  condition_key: string;
  condition_display: string;
  patient_data: PatientData;
  status: CaseStatus;
  phase: CasePhase;
  started_at: string;
  completed_at?: string;
  duration_seconds?: number;
  history_gathered: string[];
  exam_performed: string[];
  differential: string[];
  plan_proposed: string[];
  hints_given: number;
  teaching_moments: string[];
  learning_materials?: LearningMaterials;
  debrief_summary?: string;
}

export interface PatientData {
  name: string;
  age: string;
  sex: string;
  weight_kg: number;
  chief_complaint: string;
  presentation: string;
  vital_signs?: VitalSigns;
}

export interface VitalSigns {
  temp_c: number;
  hr: number;
  rr: number;
  bp_systolic?: number;
  bp_diastolic?: number;
  spo2: number;
}

export interface LearningMaterials {
  key_takeaways: string[];
  reading_list: ReadingItem[];
  practice_points: string[];
}

export interface ReadingItem {
  title: string;
  source: string;
  url?: string;
  relevance: string;
}

// Message types
export type MessageRole = 'user' | 'echo' | 'system';

export interface Message {
  id: string;
  session_id: string;
  role: MessageRole;
  content: string;
  phase?: CasePhase;
  metadata?: Record<string, unknown>;
  created_at: string;
  failed?: boolean;
}

// API types
export interface StartCaseRequest {
  learner_level: LearnerLevel;
  condition_key?: string;
  time_constraint_minutes?: number;
}

export interface SendMessageRequest {
  message: string;
}

export interface CaseResponse {
  session_id: string;
  patient: PatientData;
  condition_display: string;
  opening_message: string;
  phase: CasePhase;
}

export interface MessageResponse {
  message: string;
  phase: CasePhase;
  hints_given: number;
  is_complete: boolean;
  learning_materials?: LearningMaterials;
  audio_url?: string;
}

export interface EndCaseResponse {
  debrief: string;
  learning_materials: LearningMaterials;
  duration_seconds: number;
  performance_summary: {
    history_items: number;
    exam_items: number;
    differential_items: number;
    plan_items: number;
    hints_used: number;
  };
}
