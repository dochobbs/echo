import type { LearnerLevel, User } from '../types';

function getApiBase(): string {
  if (import.meta.env.DEV) {
    return '/api';
  }
  return '';
}

export interface BackendStartCaseRequest {
  learner_level: LearnerLevel;
  condition_key?: string;
  time_constraint?: number;
  visit_type?: 'sick' | 'well_child';
  visit_age_months?: number;
}

export interface BackendCaseState {
  session_id: string;
  patient: {
    name: string;
    age: number;
    age_unit: string;
    sex: string;
    weight_kg: number;
    chief_complaint?: string;
    condition_key: string;
    condition_display: string;
    parent_name: string;
    vitals: Record<string, number>;
    visit_age_months?: number;
    growth_data?: Record<string, unknown>;
    milestones?: Record<string, string[]>;
  };
  phase: string;
  learner_level: string;
  visit_type?: string;
  conversation: Array<{ role: string; content: string }>;
  history_gathered: string[];
  exam_performed: string[];
  differential: string[];
  plan_proposed: string[];
  hints_given: number;
  teaching_moments: string[];
  started_at: string;
  // Well-child tracking
  growth_reviewed?: boolean;
  milestones_assessed?: string[];
  guidance_topics_covered?: string[];
  immunizations_addressed?: boolean;
  screening_tools_used?: string[];
  parent_concerns_addressed?: string[];
}

export interface WellChildDomainScore {
  score: number;
  feedback: string;
}

export interface WellChildScores {
  growth_interpretation: WellChildDomainScore;
  milestone_assessment: WellChildDomainScore;
  exam_thoroughness: WellChildDomainScore;
  anticipatory_guidance: WellChildDomainScore;
  immunization_knowledge: WellChildDomainScore;
  communication_skill: WellChildDomainScore;
}

export interface DebriefData {
  summary: string;
  strengths: string[];
  areas_for_improvement: string[];
  missed_items: string[];
  teaching_points: string[];
  follow_up_resources: string[];
  well_child_scores?: WellChildScores;
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

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  name?: string;
  level?: LearnerLevel;
}

export interface LoginRequest {
  email: string;
  password: string;
}

function getStorage(key: string): string | null {
  if (typeof window === 'undefined') return null;
  try {
    return localStorage.getItem(key);
  } catch {
    return null;
  }
}

function setStorage(key: string, value: string | null): void {
  if (typeof window === 'undefined') return;
  try {
    if (value) {
      localStorage.setItem(key, value);
    } else {
      localStorage.removeItem(key);
    }
  } catch {
    // Storage not available
  }
}

class ApiClient {
  private token: string | null = null;
  private initialized = false;

  private ensureInitialized() {
    if (!this.initialized && typeof window !== 'undefined') {
      const stored = getStorage('access_token');
      if (stored) {
        this.token = stored;
      }
      this.initialized = true;
    }
  }

  setToken(token: string | null) {
    this.token = token;
    setStorage('access_token', token);
    if (!token) {
      setStorage('refresh_token', null);
    }
  }

  setRefreshToken(token: string | null) {
    setStorage('refresh_token', token);
  }

  getRefreshToken(): string | null {
    return getStorage('refresh_token');
  }

  hasToken(): boolean {
    this.ensureInitialized();
    return !!this.token;
  }

  private async fetch<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    this.ensureInitialized();

    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...((options.headers as Record<string, string>) || {}),
    };

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    const response = await fetch(`${getApiBase()}${endpoint}`, {
      ...options,
      headers,
    });

    if (!response.ok) {
      if (response.status === 401 && this.getRefreshToken()) {
        const refreshed = await this.refreshTokens();
        if (refreshed) {
          headers['Authorization'] = `Bearer ${this.token}`;
          const retryResponse = await fetch(`${getApiBase()}${endpoint}`, {
            ...options,
            headers,
          });
          if (retryResponse.ok) {
            return retryResponse.json();
          }
        }
      }
      const error = await response.json().catch(() => ({}));
      throw new Error(error.detail || `API error: ${response.status}`);
    }

    return response.json();
  }

  async register(data: RegisterRequest): Promise<AuthTokens> {
    const response = await fetch(`${getApiBase()}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.detail || 'Registration failed');
    }

    const tokens: AuthTokens = await response.json();
    this.setToken(tokens.access_token);
    this.setRefreshToken(tokens.refresh_token);
    return tokens;
  }

  async login(data: LoginRequest): Promise<AuthTokens> {
    const response = await fetch(`${getApiBase()}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.detail || 'Login failed');
    }

    const tokens: AuthTokens = await response.json();
    this.setToken(tokens.access_token);
    this.setRefreshToken(tokens.refresh_token);
    return tokens;
  }

  async refreshTokens(): Promise<boolean> {
    const refreshToken = this.getRefreshToken();
    if (!refreshToken) return false;

    try {
      const response = await fetch(`${getApiBase()}/auth/refresh`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: refreshToken }),
      });

      if (!response.ok) {
        this.setToken(null);
        return false;
      }

      const tokens: AuthTokens = await response.json();
      this.setToken(tokens.access_token);
      this.setRefreshToken(tokens.refresh_token);
      return true;
    } catch {
      this.setToken(null);
      return false;
    }
  }

  async getMe(): Promise<User> {
    return this.fetch('/auth/me');
  }

  async updateMe(updates: Partial<User>): Promise<User> {
    return this.fetch('/auth/me', {
      method: 'PATCH',
      body: JSON.stringify(updates),
    });
  }

  async getMyStats(): Promise<{ total_cases: number; completed_cases: number; total_teaching_moments: number }> {
    return this.fetch('/auth/me/stats');
  }

  logout() {
    this.setToken(null);
  }

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

  async startDescribeCase(learnerLevel: LearnerLevel): Promise<BackendCaseResponse> {
    return this.fetch('/case/describe/start', {
      method: 'POST',
      body: JSON.stringify({ learner_level: learnerLevel }),
    });
  }

  async getCaseHistory(): Promise<{ cases: unknown[]; total_count: number }> {
    return this.fetch('/case/history');
  }

  async getCaseExport(sessionId: string): Promise<CaseExport> {
    return this.fetch(`/case/history/${sessionId}`);
  }

  async getActiveCases(): Promise<{ cases: unknown[] }> {
    return this.fetch('/case/me/active');
  }

  async getCaseById(sessionId: string): Promise<BackendCaseResponse> {
    return this.fetch(`/case/${sessionId}`);
  }

  async getPatients(): Promise<{ patients: ImportedPatient[]; total_count: number }> {
    return this.fetch('/patients');
  }

  async importPatient(file: File): Promise<{ patient: ImportedPatient; parse_warnings: string[] }> {
    const formData = new FormData();
    formData.append('file', file);
    
    const base = getApiBase();
    const response = await fetch(`${base}/patients/import`, {
      method: 'POST',
      headers: {
        ...(this.token ? { Authorization: `Bearer ${this.token}` } : {}),
      },
      body: formData,
    });
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Import failed' }));
      throw new Error(error.detail || 'Import failed');
    }
    
    return response.json();
  }

  async deletePatient(patientId: string): Promise<void> {
    return this.fetch(`/patients/${patientId}`, { method: 'DELETE' });
  }

  async bulkImportPatients(files: File[]): Promise<BulkImportResponse> {
    const formData = new FormData();
    for (const file of files) {
      formData.append('files', file);
    }

    const headers: Record<string, string> = {};
    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    const response = await fetch(`${getApiBase()}/patients/import/bulk`, {
      method: 'POST',
      headers,
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.detail || 'Bulk import failed');
    }

    return response.json();
  }

  async getAdminMetrics(): Promise<AdminMetrics> {
    return this.fetch('/admin/metrics');
  }

  async getAdminUsers(limit = 50, offset = 0): Promise<AdminUser[]> {
    return this.fetch(`/admin/users?limit=${limit}&offset=${offset}`);
  }

  async getAdminCases(limit = 50, offset = 0): Promise<AdminCase[]> {
    return this.fetch(`/admin/cases?limit=${limit}&offset=${offset}`);
  }

  async getStruggleMetrics(): Promise<StruggleMetrics> {
    return this.fetch('/admin/metrics/struggles');
  }

  async getAdminUserCases(userId: string): Promise<AdminCase[]> {
    return this.fetch(`/admin/cases?user_id=${userId}`);
  }

  async getAdminCaseDetail(sessionId: string): Promise<AdminCaseDetail> {
    return this.fetch(`/admin/cases/${sessionId}`);
  }
}

export interface AdminMetrics {
  total_users: number;
  active_last_7_days: number;
  active_last_30_days: number;
  total_cases: number;
  completed_cases: number;
  active_cases: number;
  avg_case_duration_minutes?: number;
  avg_hints_per_case?: number;
  completion_rate?: number;
  most_practiced_conditions: Array<{ condition: string; count: number }>;
  cases_by_day: Array<{ date: string; count: number }>;
}

export interface AdminUser {
  id: string;
  email: string;
  name?: string;
  level: string;
  role: string;
  institution?: string;
  created_at: string;
  last_active: string;
  total_cases: number;
  completed_cases: number;
}

export interface AdminCase {
  session_id: string;
  user_id?: string;
  user_email?: string;
  condition_display: string;
  patient_name: string;
  status: string;
  phase: string;
  started_at: string;
  completed_at?: string;
  duration_minutes?: number;
  hints_given: number;
}

export interface StruggleMetrics {
  common_stuck_phases: Array<{ phase: string; count: number }>;
  high_hint_conditions: Array<{ condition: string; avg_hints: number }>;
  avg_hints_by_level: Array<{ level: string; avg_hints: number }>;
}

export interface AdminCaseDetail {
  session_id: string;
  user?: {
    id: string;
    email: string;
    name?: string;
    level: string;
  };
  condition_key: string;
  condition_display: string;
  patient_data: Record<string, unknown>;
  status: string;
  phase: string;
  started_at?: string;
  completed_at?: string;
  duration_seconds?: number;
  history_gathered: string[];
  exam_performed: string[];
  differential: string[];
  plan_proposed: string[];
  hints_given: number;
  teaching_moments: string[];
  debrief_summary?: string;
  learning_materials?: Record<string, unknown>;
  conversation: Array<{
    role: string;
    content: string;
    created_at: string;
  }>;
}

export interface BulkImportResult {
  filename: string;
  success: boolean;
  patient?: ImportedPatient;
  error?: string;
  warnings: string[];
}

export interface BulkImportResponse {
  results: BulkImportResult[];
  total_files: number;
  successful: number;
  failed: number;
}

export interface ImportedPatient {
  id: string;
  name: string;
  birth_date?: string;
  sex?: string;
  age_months?: number;
  problems: Array<{ display: string; status: string }>;
  medications: Array<{ display: string; dose?: string; status: string }>;
  allergies: Array<{ display: string; reaction?: string; severity?: string }>;
  encounters: Array<{ date?: string; type?: string; reason?: string }>;
  source: string;
  source_file?: string;
  imported_at: string;
}

export interface CaseExport {
  session_id: string;
  condition_key: string;
  condition_display: string;
  patient_name: string;
  patient_age: string;
  learner_level: string;
  started_at: string;
  completed_at?: string;
  duration_minutes?: number;
  status: string;
  phase: string;
  history_gathered: string[];
  exam_performed: string[];
  differential: string[];
  plan_proposed: string[];
  hints_given: number;
  teaching_moments: string[];
  debrief_summary?: string;
  conversation?: Array<{
    role: string;
    content: string;
    timestamp?: string;
  }>;
}

export const api = new ApiClient();
