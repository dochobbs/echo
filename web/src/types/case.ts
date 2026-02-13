/**
 * Echo Web App - Case Types
 */

export type VisitType = 'sick' | 'well_child';

export type WellChildPhase = 'growth_review' | 'developmental_screening' |
  'anticipatory_guidance' | 'immunizations' | 'parent_questions';

export type CasePhase = 'intro' | 'history' | 'exam' | 'assessment' | 'plan' |
  'debrief' | 'complete' | WellChildPhase;

export interface Message {
  id: string
  role: 'user' | 'echo'
  content: string
  timestamp: Date
  audioUrl?: string
}

export interface CaseState {
  session_id: string
  phase: CasePhase
  patient: GeneratedPatient
  visit_type?: VisitType
  history_gathered: string[]
  exam_performed: string[]
  differential: string[]
  plan_proposed: string[]
  hints_given: number
  teaching_moments: string[]
  started_at: string
  time_constraint?: number
  // Well-child tracking
  growth_reviewed?: boolean
  milestones_assessed?: string[]
  guidance_topics_covered?: string[]
  immunizations_addressed?: boolean
  screening_tools_used?: string[]
  parent_concerns_addressed?: string[]
}

export interface GeneratedPatient {
  id: string
  name: string
  age: number
  age_unit: 'days' | 'weeks' | 'months' | 'years'
  sex: 'male' | 'female'
  chief_complaint?: string  // Optional for well-child
  parent_name?: string
  parent_style?: string
  condition_key: string
  visit_age_months?: number
  growth_data?: Record<string, unknown>
  milestones?: Record<string, string[]>
}

export interface WellChildDomainScore {
  score: number
  feedback: string
}

export interface WellChildScores {
  growth_interpretation: WellChildDomainScore
  milestone_assessment: WellChildDomainScore
  exam_thoroughness: WellChildDomainScore
  anticipatory_guidance: WellChildDomainScore
  immunization_knowledge: WellChildDomainScore
  communication_skill: WellChildDomainScore
}

export interface StartCaseRequest {
  learner_level: 'student' | 'resident' | 'np_student' | 'fellow'
  condition_key?: string  // Optional: request specific condition
  time_constraint?: number  // Minutes available
  visit_type?: VisitType
  visit_age_months?: number
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
