/**
 * Echo Web App - Case Types
 */

export interface Message {
  id: string
  role: 'user' | 'echo'
  content: string
  timestamp: Date
  audioUrl?: string
}

export interface CaseState {
  session_id: string
  phase: 'intro' | 'history' | 'exam' | 'assessment' | 'plan' | 'debrief' | 'complete'
  patient: GeneratedPatient
  history_gathered: string[]
  exam_performed: string[]
  differential: string[]
  plan_proposed: string[]
  hints_given: number
  teaching_moments: string[]
  started_at: string
  time_constraint?: number
}

export interface GeneratedPatient {
  id: string
  name: string
  age: number
  age_unit: 'days' | 'weeks' | 'months' | 'years'
  sex: 'male' | 'female'
  chief_complaint: string
  parent_name?: string
  parent_style?: string
  condition_key: string
}

export interface StartCaseRequest {
  learner_level: 'student' | 'resident' | 'np_student' | 'fellow'
  condition_key?: string  // Optional: request specific condition
  time_constraint?: number  // Minutes available
}

export interface StartCaseResponse {
  message: string
  case_state: CaseState
}

export interface CaseMessageRequest {
  message: string
  case_state: CaseState
}

export interface CaseMessageResponse {
  message: string
  case_state: CaseState
  teaching_moment?: string
}
