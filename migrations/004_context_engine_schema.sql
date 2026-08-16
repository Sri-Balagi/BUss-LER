-- =============================================================================
-- Migration: 004_context_engine_schema
-- Description: Creates the tables for Milestone 4 (Context Engine, Conversations).
-- =============================================================================

-- =============================================================================
-- 1. ENUMS
-- =============================================================================

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'context_status_enum') THEN
        CREATE TYPE context_status_enum AS ENUM (
            'building', 'assembled', 'optimized', 'consumed', 'expired', 'archived'
        );
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'conversation_status_enum') THEN
        CREATE TYPE conversation_status_enum AS ENUM (
            'active', 'archived'
        );
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'conversation_role_enum') THEN
        CREATE TYPE conversation_role_enum AS ENUM (
            'user', 'assistant', 'system', 'tool'
        );
    END IF;
END$$;

-- =============================================================================
-- 2. ENTERPRISE CONTEXTS TABLE
-- =============================================================================
-- Stores lifecycle metadata for assembled EnterpriseContexts.
-- The full assembled context is computed at runtime; only metadata is persisted.

CREATE TABLE IF NOT EXISTS enterprise_contexts (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    twin_id             UUID NOT NULL REFERENCES digital_twins(id) ON DELETE CASCADE,
    policy_id           TEXT NOT NULL,
    schema_version      TEXT NOT NULL DEFAULT '1.0',
    status              context_status_enum NOT NULL DEFAULT 'building',
    is_partial          BOOLEAN NOT NULL DEFAULT FALSE,
    assembled_at        TIMESTAMPTZ,
    expires_at          TIMESTAMPTZ,
    consumed_at         TIMESTAMPTZ,
    archived_at         TIMESTAMPTZ,
    deleted_at          TIMESTAMPTZ,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_enterprise_contexts_twin_id
    ON enterprise_contexts(twin_id)
    WHERE deleted_at IS NULL;

CREATE INDEX IF NOT EXISTS idx_enterprise_contexts_twin_status
    ON enterprise_contexts(twin_id, status)
    WHERE deleted_at IS NULL;

CREATE INDEX IF NOT EXISTS idx_enterprise_contexts_expires_at
    ON enterprise_contexts(expires_at)
    WHERE deleted_at IS NULL AND status NOT IN ('expired', 'archived');

-- updated_at trigger
CREATE OR REPLACE TRIGGER set_enterprise_contexts_updated_at
    BEFORE UPDATE ON enterprise_contexts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- Row-Level Security
ALTER TABLE enterprise_contexts ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can access their own contexts"
    ON enterprise_contexts
    FOR ALL
    USING (
        twin_id IN (
            SELECT id FROM digital_twins
            WHERE entity_id IN (
                SELECT id FROM entities WHERE user_id = auth.uid()
            )
        )
    );

-- =============================================================================
-- 3. CONVERSATION THREADS TABLE
-- =============================================================================

CREATE TABLE IF NOT EXISTS conversation_threads (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    twin_id         UUID NOT NULL REFERENCES digital_twins(id) ON DELETE CASCADE,
    title           TEXT,
    status          conversation_status_enum NOT NULL DEFAULT 'active',
    summary         TEXT,
    turn_count      INTEGER NOT NULL DEFAULT 0 CHECK (turn_count >= 0),
    metadata        JSONB NOT NULL DEFAULT '{}',
    archived_at     TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_conversation_threads_twin_id
    ON conversation_threads(twin_id)
    WHERE archived_at IS NULL;

CREATE INDEX IF NOT EXISTS idx_conversation_threads_twin_status
    ON conversation_threads(twin_id, status)
    WHERE archived_at IS NULL;

-- updated_at trigger
CREATE OR REPLACE TRIGGER set_conversation_threads_updated_at
    BEFORE UPDATE ON conversation_threads
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- Row-Level Security
ALTER TABLE conversation_threads ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can access their own conversation threads"
    ON conversation_threads
    FOR ALL
    USING (
        twin_id IN (
            SELECT id FROM digital_twins
            WHERE entity_id IN (
                SELECT id FROM entities WHERE user_id = auth.uid()
            )
        )
    );

-- =============================================================================
-- 4. CONVERSATION TURNS TABLE
-- =============================================================================

CREATE TABLE IF NOT EXISTS conversation_turns (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    thread_id           UUID NOT NULL REFERENCES conversation_threads(id) ON DELETE CASCADE,
    role                conversation_role_enum NOT NULL,
    content             TEXT NOT NULL,
    agent_id            UUID,
    tokens_used         INTEGER NOT NULL DEFAULT 0 CHECK (tokens_used >= 0),
    tool_calls          JSONB NOT NULL DEFAULT '[]',
    turn_index          INTEGER NOT NULL CHECK (turn_index >= 0),
    metadata            JSONB NOT NULL DEFAULT '{}',
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (thread_id, turn_index)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_conversation_turns_thread_id
    ON conversation_turns(thread_id);

CREATE INDEX IF NOT EXISTS idx_conversation_turns_thread_index
    ON conversation_turns(thread_id, turn_index);

-- Row-Level Security
ALTER TABLE conversation_turns ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can access turns via thread ownership"
    ON conversation_turns
    FOR ALL
    USING (
        thread_id IN (
            SELECT id FROM conversation_threads
            WHERE twin_id IN (
                SELECT id FROM digital_twins
                WHERE entity_id IN (
                    SELECT id FROM entities WHERE user_id = auth.uid()
                )
            )
        )
    );

-- =============================================================================
-- 5. COGNITIVE TRACE EXTENSIONS (M4 fields)
-- =============================================================================
-- Add optional M4 context fields to the existing cognitive_traces table.

ALTER TABLE cognitive_traces
    ADD COLUMN IF NOT EXISTS context_id               UUID REFERENCES enterprise_contexts(id),
    ADD COLUMN IF NOT EXISTS context_sources_used     TEXT[],
    ADD COLUMN IF NOT EXISTS compression_ratio        FLOAT CHECK (compression_ratio IS NULL OR (compression_ratio >= 0 AND compression_ratio <= 1)),
    ADD COLUMN IF NOT EXISTS ranking_latency_ms       FLOAT,
    ADD COLUMN IF NOT EXISTS compression_latency_ms   FLOAT,
    ADD COLUMN IF NOT EXISTS window_latency_ms        FLOAT,
    ADD COLUMN IF NOT EXISTS token_estimate           INTEGER;

CREATE INDEX IF NOT EXISTS idx_cognitive_traces_context_id
    ON cognitive_traces(context_id)
    WHERE context_id IS NOT NULL;
