import type { LearnerLevel } from '../types';

const API_BASE = '/api';

// Backend API types (match Python models)
export interface BackendStartCaseRequest {
  learner_level: LearnerLevel;
  condition_key?: string;
  time_constraint?: number;
}

export interface BackendCaseState {
  session_id: string;
  patient: {
    name: string;
    age: number;
    age_unit: string;
    sex: string;
    weight_kg: number;
    chief_complaint: string;
    condition_key: string;
    condition_display: string;
    parent_name: string;
    vitals: Record<string, number>;
  };
  phase: string;
  learner_level: string;
  conversation: Array<{ role: string; content: string }>;
  history_gathered: string[];
  exam_performed: string[];
  differential: string[];
  plan_proposed: string[];
  hints_given: number;
  teaching_moments: string[];
  started_at: string;
}

export interface DebriefData {
  summary: string;
  strengths: string[];
  areas_for_improvement: string[];
  missed_items: string[];
  teaching_points: string[];
  follow_up_resources: string[];
}

export interface BackendCaseResponse {
  message: string;
  case_state: BackendCaseState;
  teaching_moment?: string;
  debrief?: DebriefData;
  hint_offered?: boolean;
}

export interface BackendMessageRequest {
  message: string;
  case_state: BackendCaseState;
}

class ApiClient {
  private token: string | null = null;

  setToken(token: string | null) {
    this.token = token;
  }

  private async fetch<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...((options.headers as Record<string, string>) || {}),
    };

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    const response = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.detail || `API error: ${response.status}`);
    }

    return response.json();
  }

  // Case endpoints - match backend API
  async startCase(data: BackendStartCaseRequest): Promise<BackendCaseResponse> {
    return this.fetch('/case/start', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async sendMessage(data: BackendMessageRequest): Promise<BackendCaseResponse> {
    return this.fetch('/case/message', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getDebrief(caseState: BackendCaseState): Promise<BackendCaseResponse> {
    return this.fetch('/case/debrief', {
      method: 'POST',
      body: JSON.stringify(caseState),
    });
  }

  // Describe-a-case mode
  async startDescribeCase(learnerLevel: LearnerLevel): Promise<BackendCaseResponse> {
    return this.fetch('/case/describe/start', {
      method: 'POST',
      body: JSON.stringify({ learner_level: learnerLevel }),
    });
  }

  async getCaseHistory(): Promise<{ cases: unknown[]; total_count: number }> {
    return this.fetch('/case/history');
  }
}

export const api = new ApiClient();
