-- Echo Database Schema
-- Run this in Supabase SQL Editor to set up tables

-- ============================================
-- USERS & AUTH
-- ============================================

-- User profiles (extends Supabase auth.users)
CREATE TABLE IF NOT EXISTS profiles (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  email TEXT UNIQUE NOT NULL,
  name TEXT,
  level TEXT NOT NULL DEFAULT 'student' CHECK (level IN ('student', 'resident', 'np_student', 'fellow', 'attending')),
  specialty_interest TEXT,
  institution TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  last_active TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  preferences JSONB DEFAULT '{}'::jsonb
);

-- Enable RLS
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;

-- Users can read/update their own profile
CREATE POLICY "Users can view own profile" ON profiles
  FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON profiles
  FOR UPDATE USING (auth.uid() = id);

-- ============================================
-- CASE SESSIONS
-- ============================================

-- Active and completed case sessions
CREATE TABLE IF NOT EXISTS case_sessions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
  condition_key TEXT NOT NULL,
  condition_display TEXT NOT NULL,
  patient_data JSONB NOT NULL,  -- GeneratedPatient snapshot
  status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'completed', 'abandoned')),
  phase TEXT NOT NULL DEFAULT 'intro',
  started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  completed_at TIMESTAMPTZ,
  duration_seconds INTEGER,

  -- Learning tracking
  history_gathered TEXT[] DEFAULT '{}',
  exam_performed TEXT[] DEFAULT '{}',
  differential TEXT[] DEFAULT '{}',
  plan_proposed TEXT[] DEFAULT '{}',
  hints_given INTEGER DEFAULT 0,
  teaching_moments TEXT[] DEFAULT '{}',

  -- Export data (populated on completion)
  learning_materials JSONB,
  debrief_summary TEXT,

  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Enable RLS
ALTER TABLE case_sessions ENABLE ROW LEVEL SECURITY;

-- Users can only access their own cases
CREATE POLICY "Users can view own cases" ON case_sessions
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own cases" ON case_sessions
  FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own cases" ON case_sessions
  FOR UPDATE USING (auth.uid() = user_id);

-- Index for quick lookups
CREATE INDEX idx_case_sessions_user ON case_sessions(user_id);
CREATE INDEX idx_case_sessions_status ON case_sessions(status);
CREATE INDEX idx_case_sessions_condition ON case_sessions(condition_key);

-- ============================================
-- CONVERSATION MESSAGES
-- ============================================

-- Individual messages within a case session
CREATE TABLE IF NOT EXISTS messages (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id UUID REFERENCES case_sessions(id) ON DELETE CASCADE,
  role TEXT NOT NULL CHECK (role IN ('user', 'echo', 'system')),
  content TEXT NOT NULL,
  phase TEXT,  -- Phase when message was sent
  metadata JSONB DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Enable RLS
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;

-- Users can access messages for their own cases
CREATE POLICY "Users can view own messages" ON messages
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM case_sessions
      WHERE case_sessions.id = messages.session_id
      AND case_sessions.user_id = auth.uid()
    )
  );

CREATE POLICY "Users can insert own messages" ON messages
  FOR INSERT WITH CHECK (
    EXISTS (
      SELECT 1 FROM case_sessions
      WHERE case_sessions.id = messages.session_id
      AND case_sessions.user_id = auth.uid()
    )
  );

-- Index for quick lookups
CREATE INDEX idx_messages_session ON messages(session_id);

-- ============================================
-- COMPETENCY TRACKING
-- ============================================

-- Competency definitions
CREATE TABLE IF NOT EXISTS competencies (
  id TEXT PRIMARY KEY,  -- e.g., 'aom_diagnosis', 'parent_communication'
  name TEXT NOT NULL,
  category TEXT NOT NULL,  -- 'clinical', 'communication', 'procedural'
  description TEXT,
  conditions TEXT[] DEFAULT '{}',  -- Related conditions
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- User competency progress
CREATE TABLE IF NOT EXISTS user_competencies (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
  competency_id TEXT REFERENCES competencies(id) ON DELETE CASCADE,
  exposure_count INTEGER DEFAULT 0,
  last_seen TIMESTAMPTZ,
  proficiency TEXT DEFAULT 'developing' CHECK (proficiency IN ('developing', 'competent', 'proficient')),
  notes TEXT[] DEFAULT '{}',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

  UNIQUE(user_id, competency_id)
);

-- Enable RLS
ALTER TABLE user_competencies ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own competencies" ON user_competencies
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can update own competencies" ON user_competencies
  FOR ALL USING (auth.uid() = user_id);

-- ============================================
-- FUNCTIONS & TRIGGERS
-- ============================================

-- Auto-create profile on signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.profiles (id, email, name)
  VALUES (
    NEW.id,
    NEW.email,
    COALESCE(NEW.raw_user_meta_data->>'name', split_part(NEW.email, '@', 1))
  );
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger for new user signup
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- Update last_active on profile
CREATE OR REPLACE FUNCTION public.update_last_active()
RETURNS TRIGGER AS $$
BEGIN
  UPDATE profiles SET last_active = NOW() WHERE id = auth.uid();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Calculate case duration on completion
CREATE OR REPLACE FUNCTION public.calculate_case_duration()
RETURNS TRIGGER AS $$
BEGIN
  IF NEW.status = 'completed' AND OLD.status != 'completed' THEN
    NEW.completed_at = NOW();
    NEW.duration_seconds = EXTRACT(EPOCH FROM (NOW() - NEW.started_at))::INTEGER;
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS on_case_complete ON case_sessions;
CREATE TRIGGER on_case_complete
  BEFORE UPDATE ON case_sessions
  FOR EACH ROW EXECUTE FUNCTION public.calculate_case_duration();

-- ============================================
-- VIEWS
-- ============================================

-- User case statistics
CREATE OR REPLACE VIEW user_case_stats AS
SELECT
  user_id,
  COUNT(*) AS total_cases,
  COUNT(*) FILTER (WHERE status = 'completed') AS completed_cases,
  COUNT(DISTINCT condition_key) AS unique_conditions,
  AVG(duration_seconds) FILTER (WHERE status = 'completed') AS avg_duration_seconds,
  MAX(completed_at) AS last_case_completed
FROM case_sessions
GROUP BY user_id;

-- Condition popularity
CREATE OR REPLACE VIEW condition_stats AS
SELECT
  condition_key,
  condition_display,
  COUNT(*) AS total_attempts,
  COUNT(*) FILTER (WHERE status = 'completed') AS completions,
  AVG(duration_seconds) FILTER (WHERE status = 'completed') AS avg_duration
FROM case_sessions
GROUP BY condition_key, condition_display;
