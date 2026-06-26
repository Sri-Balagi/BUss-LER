-- =============================================================================
-- Migration: 003_intent_engine_schema
-- Description: Creates the tables for Milestone 3 (Intent, Goal, Plan, Recs, Trace).
-- =============================================================================

-- =============================================================================
-- 1. ENUMS
-- =============================================================================

CREATE TYPE intent_status_enum AS ENUM (
    'pending', 'classified', 'confirmed', 'fulfilled', 'rejected', 'expired'
);

CREATE TYPE intent_type_enum AS ENUM (
    'inventory', 'calendar', 'analytics', 'finance', 'communication',
    'task_management', 'reporting', 'research', 'general'
);

CREATE TYPE goal_status_enum AS ENUM (
    'draft', 'active', 'in_progress', 'paused', 'blocked', 'completed', 'abandoned'
);

CREATE TYPE goal_type_enum AS ENUM (
    'strategic', 'operational', 'tactical'
);

CREATE TYPE plan_status_enum AS ENUM (
    'draft', 'approved', 'executing', 'completed', 'abandoned'
);

CREATE TYPE recommendation_status_enum AS ENUM (
    'generated', 'presented', 'accepted', 'rejected', 'ignored', 'superseded'
);

CREATE TYPE recommendation_confidence_enum AS ENUM (
    'high', 'medium', 'low'
);

-- =============================================================================
-- 2. TABLES
-- =============================================================================

CREATE TABLE IF NOT EXISTS intents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    twin_id UUID NOT NULL REFERENCES digital_twins(id) ON DELETE CASCADE,
    raw_text TEXT NOT NULL,
    title VARCHAR(255),
    intent_type intent_type_enum,
    status intent_status_enum NOT NULL DEFAULT 'pending',
    analysis JSONB,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    classified_at TIMESTAMPTZ,
    fulfilled_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS goals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    twin_id UUID NOT NULL REFERENCES digital_twins(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    goal_type goal_type_enum NOT NULL DEFAULT 'strategic',
    status goal_status_enum NOT NULL DEFAULT 'draft',
    priority INT NOT NULL DEFAULT 5 CHECK (priority >= 1 AND priority <= 10),
    progress NUMERIC(5,2) NOT NULL DEFAULT 0.00 CHECK (progress >= 0.00 AND progress <= 100.00),
    success_criteria JSONB NOT NULL DEFAULT '[]'::jsonb,
    target_date TIMESTAMPTZ,
    parent_goal_id UUID REFERENCES goals(id) ON DELETE SET NULL,
    completed_at TIMESTAMPTZ,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS intent_goal_links (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    intent_id UUID NOT NULL REFERENCES intents(id) ON DELETE CASCADE,
    goal_id UUID NOT NULL REFERENCES goals(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(intent_id, goal_id)
);

CREATE TABLE IF NOT EXISTS plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    twin_id UUID NOT NULL REFERENCES digital_twins(id) ON DELETE CASCADE,
    goal_id UUID REFERENCES goals(id) ON DELETE CASCADE,
    intent_id UUID REFERENCES intents(id) ON DELETE SET NULL,
    rationale TEXT NOT NULL,
    steps JSONB NOT NULL DEFAULT '[]'::jsonb,
    assumptions JSONB NOT NULL DEFAULT '[]'::jsonb,
    risks JSONB NOT NULL DEFAULT '[]'::jsonb,
    dependencies JSONB NOT NULL DEFAULT '[]'::jsonb,
    estimated_effort VARCHAR(255),
    confidence NUMERIC(3,2) NOT NULL DEFAULT 0.00 CHECK (confidence >= 0.00 AND confidence <= 1.00),
    status plan_status_enum NOT NULL DEFAULT 'draft',
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS recommendations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    twin_id UUID NOT NULL REFERENCES digital_twins(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    body TEXT NOT NULL,
    rationale TEXT NOT NULL,
    confidence recommendation_confidence_enum NOT NULL DEFAULT 'medium',
    status recommendation_status_enum NOT NULL DEFAULT 'generated',
    supporting_memory_ids UUID[] NOT NULL DEFAULT '{}',
    supporting_goal_ids UUID[] NOT NULL DEFAULT '{}',
    originating_plan_id UUID REFERENCES plans(id) ON DELETE SET NULL,
    trigger_context JSONB NOT NULL DEFAULT '{}'::jsonb,
    explainability_metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    acknowledged_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS cognitive_traces (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    twin_id UUID NOT NULL REFERENCES digital_twins(id) ON DELETE CASCADE,
    operation_type VARCHAR(100) NOT NULL,
    provider VARCHAR(100) NOT NULL,
    model VARCHAR(100) NOT NULL,
    prompt_version VARCHAR(100) NOT NULL,
    operation_context_id VARCHAR(255) NOT NULL,
    intent_id UUID REFERENCES intents(id) ON DELETE SET NULL,
    goal_id UUID REFERENCES goals(id) ON DELETE SET NULL,
    plan_id UUID REFERENCES plans(id) ON DELETE SET NULL,
    recommendation_id UUID REFERENCES recommendations(id) ON DELETE SET NULL,
    reasoning_summary TEXT NOT NULL,
    confidence NUMERIC(3,2) CHECK (confidence >= 0.00 AND confidence <= 1.00),
    latency_ms NUMERIC(10,2) NOT NULL,
    token_usage JSONB NOT NULL DEFAULT '{}'::jsonb,
    memory_ids_used UUID[] NOT NULL DEFAULT '{}',
    goal_ids_used UUID[] NOT NULL DEFAULT '{}',
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- =============================================================================
-- 3. INDEXES
-- =============================================================================

CREATE INDEX idx_intents_twin_id ON intents(twin_id);
CREATE INDEX idx_goals_twin_id ON goals(twin_id);
CREATE INDEX idx_goals_status ON goals(status);
CREATE INDEX idx_plans_twin_id ON plans(twin_id);
CREATE INDEX idx_recommendations_twin_id ON recommendations(twin_id);
CREATE INDEX idx_recommendations_status ON recommendations(status);
CREATE INDEX idx_cognitive_traces_twin_id ON cognitive_traces(twin_id);
CREATE INDEX idx_cognitive_traces_operation ON cognitive_traces(operation_type);
CREATE INDEX idx_cognitive_traces_context ON cognitive_traces(operation_context_id);

-- =============================================================================
-- 4. TRIGGERS (updated_at)
-- =============================================================================

CREATE TRIGGER update_intents_updated_at
    BEFORE UPDATE ON intents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_goals_updated_at
    BEFORE UPDATE ON goals
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_plans_updated_at
    BEFORE UPDATE ON plans
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_recommendations_updated_at
    BEFORE UPDATE ON recommendations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Note: cognitive_traces is append-only, no update trigger needed.
-- Note: intent_goal_links is relation-only, no update trigger needed.
