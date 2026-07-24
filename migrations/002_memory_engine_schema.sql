-- =============================================================================
-- Migration: 002_memory_engine_schema
-- Description: Creates the memories table for Milestone 2.
-- Notes:
--   - Stores structured metadata ONLY.
--   - Qdrant will store the actual embeddings under a matching collection name.
-- =============================================================================

-- =============================================================================
-- 1. ENUMS
-- =============================================================================

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'memory_category_enum') THEN
        CREATE TYPE memory_category_enum AS ENUM (
            'observation',
            'event',
            'interaction',
            'decision',
            'task',
            'reflection',
            'goal_progress',
            'alert',
            'system'
        );
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'memory_source_enum') THEN
        CREATE TYPE memory_source_enum AS ENUM (
            'conversation',
            'document',
            'execution',
            'observation',
            'user_input'
        );
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'embedding_status_enum') THEN
        CREATE TYPE embedding_status_enum AS ENUM (
            'pending',
            'processing',
            'completed',
            'failed'
        );
    END IF;
END$$;

-- =============================================================================
-- 2. TABLES
-- =============================================================================

CREATE TABLE IF NOT EXISTS memories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    twin_id UUID NOT NULL REFERENCES digital_twins(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    summary TEXT,
    memory_category memory_category_enum NOT NULL,
    source memory_source_enum NOT NULL,
    importance NUMERIC(3,2) NOT NULL DEFAULT 0.50 CHECK (importance >= 0.00 AND importance <= 1.00),
    embedding_status embedding_status_enum NOT NULL DEFAULT 'pending',
    embedding_model VARCHAR(255),
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at TIMESTAMPTZ
);

-- =============================================================================
-- 3. INDEXES
-- =============================================================================

-- Fast lookup of memories by twin
CREATE INDEX IF NOT EXISTS idx_memories_twin_id ON memories(twin_id);

-- Filter by category
CREATE INDEX IF NOT EXISTS idx_memories_category ON memories(memory_category);

-- Filter by embedding status (crucial for background workers polling for 'pending')
CREATE INDEX IF NOT EXISTS idx_memories_embedding_status ON memories(embedding_status);

-- JSONB indexing for metadata filtering
CREATE INDEX IF NOT EXISTS idx_memories_metadata ON memories USING GIN (metadata);

-- Filter for soft-deleted memories
CREATE INDEX IF NOT EXISTS idx_memories_deleted_at ON memories(deleted_at) WHERE deleted_at IS NULL;

-- =============================================================================
-- 4. TRIGGERS
-- =============================================================================

CREATE OR REPLACE TRIGGER update_memories_updated_at
    BEFORE UPDATE ON memories
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

-- =============================================================================
-- MIGRATION COMPLETE
-- =============================================================================
