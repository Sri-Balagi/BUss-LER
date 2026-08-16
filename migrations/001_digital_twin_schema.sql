-- =============================================================================
-- BizOS — Milestone 1: Digital Twin Schema Migration
-- =============================================================================
--
-- This migration creates the database schema for the Digital Twin System.
--
-- Tables created:
--   1. entities          — Root objects that BizOS manages
--   2. digital_twins     — Living, versioned state objects (1:1 with entity)
--   3. twin_snapshots    — Immutable point-in-time state captures
--   4. twin_history      — Audit log of all twin changes
--
-- Design decisions:
--   - The Digital Twin uses a domain-agnostic design with a single `state`
--     JSONB field instead of fixed dimension columns. This ensures the
--     schema never needs to change as BizOS expands to new entity types.
--   - A separate `metadata` JSONB field stores system-level information
--     (tags, labels, external IDs) distinct from domain state.
--   - No computed/AI-derived fields (health_score, analytics) — those
--     belong to future engines (Context, Simulation, Agents).
--   - An RPC function guarantees atomic updates (twin + snapshot + history).
--
-- Execution:
--   Run this SQL in the Supabase SQL Editor.
--   This migration is idempotent (uses IF NOT EXISTS where possible).
--
-- =============================================================================


-- =============================================================================
-- 1. TABLES
-- =============================================================================

-- -----------------------------------------------------------------------------
-- 1.1 entities — The root object. Represents who/what BizOS manages.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS entities (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL,
    name            TEXT NOT NULL CHECK (char_length(name) BETWEEN 1 AND 200),
    entity_type     TEXT NOT NULL CHECK (entity_type IN (
                        'individual', 'startup', 'small_business',
                        'student', 'organization'
                    )),
    description     TEXT CHECK (description IS NULL OR char_length(description) <= 2000),
    metadata        JSONB NOT NULL DEFAULT '{}',
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

COMMENT ON TABLE entities IS 'Root objects managed by BizOS. Every resource in the system belongs to exactly one entity.';
COMMENT ON COLUMN entities.user_id IS 'The authenticated user who owns this entity.';
COMMENT ON COLUMN entities.metadata IS 'Arbitrary JSON metadata. Domain-agnostic extension point.';
COMMENT ON COLUMN entities.is_active IS 'Soft-delete flag. FALSE = logically deleted.';


-- -----------------------------------------------------------------------------
-- 1.2 digital_twins — Living, versioned state object. 1:1 with entity.
--
-- Uses a domain-agnostic design:
--   - `state`: free-form JSONB for the entity's current state. Keys are
--     determined by the consuming engine/user (e.g. demographics, finances,
--     rooms, courses — whatever fits the entity type).
--   - `metadata`: system-level info (tags, labels, external IDs).
--
-- No computed/AI-derived fields. The Digital Twin in M1 is a pure
-- representation of factual state.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS digital_twins (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_id       UUID UNIQUE NOT NULL
                        REFERENCES entities(id) ON DELETE CASCADE,
    state           JSONB NOT NULL DEFAULT '{}',
    metadata        JSONB NOT NULL DEFAULT '{"schema_version": 1}',
    twin_version    INTEGER NOT NULL DEFAULT 1 CHECK (twin_version >= 1),
    last_snapshot_at TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

COMMENT ON TABLE digital_twins IS 'Living, versioned state object for an entity. Domain-agnostic JSONB state.';
COMMENT ON COLUMN digital_twins.entity_id IS 'One-to-one relationship with entities. UNIQUE constraint enforced.';
COMMENT ON COLUMN digital_twins.state IS 'Free-form JSONB representing the entity current state. Keys are engine/user-defined.';
COMMENT ON COLUMN digital_twins.metadata IS 'System-level metadata: tags, labels, external IDs, integration data.';
COMMENT ON COLUMN digital_twins.twin_version IS 'Monotonically increasing version. Used for optimistic concurrency control.';
COMMENT ON COLUMN digital_twins.last_snapshot_at IS 'Timestamp of the most recent snapshot. NULL until first update.';


-- -----------------------------------------------------------------------------
-- 1.3 twin_snapshots — Immutable point-in-time state captures.
--
-- Created automatically on every twin update inside a transaction.
-- No UPDATE or DELETE operations should ever be performed on this table.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS twin_snapshots (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    twin_id         UUID NOT NULL
                        REFERENCES digital_twins(id) ON DELETE CASCADE,
    twin_version    INTEGER NOT NULL CHECK (twin_version >= 1),
    snapshot_data   JSONB NOT NULL,
    change_reason   TEXT CHECK (change_reason IS NULL OR char_length(change_reason) <= 500),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

COMMENT ON TABLE twin_snapshots IS 'Immutable point-in-time copies of Digital Twin state. Created on every twin update.';
COMMENT ON COLUMN twin_snapshots.snapshot_data IS 'Complete twin state + metadata at snapshot time.';
COMMENT ON COLUMN twin_snapshots.change_reason IS 'Human-readable reason for the change that triggered this snapshot.';


-- -----------------------------------------------------------------------------
-- 1.4 twin_history — Audit log of all twin changes.
--
-- Tracks every create, update, and delete with field-level change details.
-- Separate from snapshots: history records what changed and why;
-- snapshots record the full state after the change.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS twin_history (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    twin_id         UUID NOT NULL
                        REFERENCES digital_twins(id) ON DELETE CASCADE,
    twin_version    INTEGER NOT NULL CHECK (twin_version >= 1),
    change_type     TEXT NOT NULL CHECK (change_type IN ('create', 'update', 'delete')),
    change_summary  TEXT CHECK (change_summary IS NULL OR char_length(change_summary) <= 500),
    changed_fields  TEXT[] NOT NULL DEFAULT '{}',
    changed_by      TEXT CHECK (changed_by IS NULL OR char_length(changed_by) <= 200),
    old_values      JSONB,
    new_values      JSONB,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

COMMENT ON TABLE twin_history IS 'Audit log for Digital Twin changes. Records field-level diffs for every modification.';
COMMENT ON COLUMN twin_history.change_type IS 'One of: create, update, delete. Validated by CHECK constraint and Python ChangeType enum.';
COMMENT ON COLUMN twin_history.changed_fields IS 'Array of top-level state keys that were modified. Includes metadata if it changed.';
COMMENT ON COLUMN twin_history.old_values IS 'Previous values of changed fields. NULL for create operations.';
COMMENT ON COLUMN twin_history.new_values IS 'New values of changed fields. NULL for delete operations.';


-- =============================================================================
-- 2. INDEXES
-- =============================================================================

-- entities: look up by user, filter by type, filter active
CREATE INDEX IF NOT EXISTS idx_entities_user_id
    ON entities(user_id);

CREATE INDEX IF NOT EXISTS idx_entities_type
    ON entities(entity_type);

CREATE INDEX IF NOT EXISTS idx_entities_active
    ON entities(is_active)
    WHERE is_active = TRUE;

-- digital_twins: entity_id has UNIQUE constraint → already indexed
-- digital_twins: GIN index on state for JSONB containment queries
CREATE INDEX IF NOT EXISTS idx_twins_state_gin
    ON digital_twins USING GIN (state);

-- twin_snapshots: query by twin, ordered by time (newest first)
CREATE INDEX IF NOT EXISTS idx_snapshots_twin_created
    ON twin_snapshots(twin_id, created_at DESC);

-- twin_snapshots: look up specific version
CREATE INDEX IF NOT EXISTS idx_snapshots_twin_version
    ON twin_snapshots(twin_id, twin_version);

-- twin_history: query by twin, ordered by time (newest first)
CREATE INDEX IF NOT EXISTS idx_history_twin_created
    ON twin_history(twin_id, created_at DESC);

-- twin_history: look up by version
CREATE INDEX IF NOT EXISTS idx_history_twin_version
    ON twin_history(twin_id, twin_version);


-- =============================================================================
-- 3. TRIGGERS — Automatic updated_at management
-- =============================================================================

CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply to entities
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_trigger WHERE tgname = 'trg_entities_updated_at'
    ) THEN
        CREATE TRIGGER trg_entities_updated_at
            BEFORE UPDATE ON entities
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at();
    END IF;
END $$;

-- Apply to digital_twins
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_trigger WHERE tgname = 'trg_twins_updated_at'
    ) THEN
        CREATE TRIGGER trg_twins_updated_at
            BEFORE UPDATE ON digital_twins
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at();
    END IF;
END $$;


-- =============================================================================
-- 4. RPC FUNCTION — Atomic twin update with snapshot and history
-- =============================================================================
--
-- This function executes a complete twin update in a single transaction:
--   1. Locks the twin row (SELECT ... FOR UPDATE)
--   2. Checks optimistic concurrency (version match)
--   3. Merges state at the top-level key level (partial update)
--   4. Replaces metadata if provided
--   5. Detects which keys actually changed (dynamic, not hardcoded)
--   6. Updates the twin with new version
--   7. Creates an immutable snapshot of the new state
--   8. Creates a history entry with old/new value diffs
--   9. Returns the updated twin as JSONB
--
-- State merging strategy:
--   Top-level keys in p_state are merged into the existing state.
--   Keys present in p_state replace corresponding keys in current state.
--   Keys NOT in p_state are preserved (partial update).
--   Example: state={"a":1,"b":2} + p_state={"b":3,"c":4} → {"a":1,"b":3,"c":4}
--
-- Error codes:
--   P0002 — Twin not found
--   P0001 — Version conflict (optimistic concurrency violation)
--
-- Called from Python via: supabase.rpc('update_twin_with_snapshot', {...})
-- =============================================================================

CREATE OR REPLACE FUNCTION update_twin_with_snapshot(
    p_twin_id UUID,
    p_expected_version INTEGER,
    p_state JSONB DEFAULT NULL,
    p_metadata JSONB DEFAULT NULL,
    p_change_reason TEXT DEFAULT NULL,
    p_changed_by TEXT DEFAULT NULL
)
RETURNS JSONB
LANGUAGE plpgsql
AS $$
DECLARE
    v_twin RECORD;
    v_new_version INTEGER;
    v_new_state JSONB;
    v_new_metadata JSONB;
    v_changed_fields TEXT[] := '{}';
    v_old_values JSONB := '{}';
    v_new_values JSONB := '{}';
    v_key TEXT;
    v_snapshot_data JSONB;
    v_result JSONB;
BEGIN
    -- =========================================================================
    -- Step 1: Lock and fetch current twin state
    -- =========================================================================
    SELECT * INTO v_twin
    FROM digital_twins
    WHERE id = p_twin_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'TWIN_NOT_FOUND:%', p_twin_id
            USING ERRCODE = 'P0002';
    END IF;

    -- =========================================================================
    -- Step 2: Optimistic concurrency check
    -- =========================================================================
    IF v_twin.twin_version != p_expected_version THEN
        RAISE EXCEPTION 'VERSION_CONFLICT:expected=%, actual=%',
            p_expected_version, v_twin.twin_version
            USING ERRCODE = 'P0001';
    END IF;

    v_new_version := v_twin.twin_version + 1;

    -- =========================================================================
    -- Step 3: Merge state (top-level key merge) and metadata (full replace)
    -- =========================================================================
    IF p_state IS NOT NULL THEN
        -- Top-level merge: keys in p_state override, others preserved
        v_new_state := v_twin.state || p_state;
    ELSE
        v_new_state := v_twin.state;
    END IF;

    v_new_metadata := COALESCE(p_metadata, v_twin.metadata);

    -- =========================================================================
    -- Step 4: Detect which state keys actually changed (dynamic)
    -- =========================================================================
    IF p_state IS NOT NULL THEN
        FOR v_key IN SELECT jsonb_object_keys(p_state)
        LOOP
            IF (p_state -> v_key) IS DISTINCT FROM (v_twin.state -> v_key) THEN
                v_changed_fields := array_append(v_changed_fields, v_key);
                v_old_values := v_old_values || jsonb_build_object(v_key, v_twin.state -> v_key);
                v_new_values := v_new_values || jsonb_build_object(v_key, p_state -> v_key);
            END IF;
        END LOOP;
    END IF;

    -- Track metadata changes separately
    IF p_metadata IS NOT NULL AND p_metadata IS DISTINCT FROM v_twin.metadata THEN
        v_changed_fields := array_append(v_changed_fields, 'metadata');
        v_old_values := v_old_values || jsonb_build_object('metadata', v_twin.metadata);
        v_new_values := v_new_values || jsonb_build_object('metadata', p_metadata);
    END IF;

    -- =========================================================================
    -- Step 5: Update the twin
    -- =========================================================================
    UPDATE digital_twins SET
        state            = v_new_state,
        metadata         = v_new_metadata,
        twin_version     = v_new_version,
        last_snapshot_at = now(),
        updated_at       = now()
    WHERE id = p_twin_id;

    -- =========================================================================
    -- Step 6: Create immutable snapshot (full state after update)
    -- =========================================================================
    v_snapshot_data := jsonb_build_object(
        'state',        v_new_state,
        'metadata',     v_new_metadata,
        'twin_version', v_new_version
    );

    INSERT INTO twin_snapshots (twin_id, twin_version, snapshot_data, change_reason)
    VALUES (p_twin_id, v_new_version, v_snapshot_data, p_change_reason);

    -- =========================================================================
    -- Step 7: Create history entry (field-level diff)
    -- =========================================================================
    INSERT INTO twin_history (
        twin_id, twin_version, change_type, change_summary,
        changed_fields, changed_by, old_values, new_values
    )
    VALUES (
        p_twin_id, v_new_version, 'update', p_change_reason,
        v_changed_fields, p_changed_by, v_old_values, v_new_values
    );

    -- =========================================================================
    -- Step 8: Return the updated twin as JSONB
    -- =========================================================================
    SELECT jsonb_build_object(
        'id',               dt.id,
        'entity_id',        dt.entity_id,
        'state',            dt.state,
        'metadata',         dt.metadata,
        'twin_version',     dt.twin_version,
        'last_snapshot_at', dt.last_snapshot_at,
        'created_at',       dt.created_at,
        'updated_at',       dt.updated_at
    ) INTO v_result
    FROM digital_twins dt
    WHERE dt.id = p_twin_id;

    RETURN v_result;
END;
$$;

COMMENT ON FUNCTION update_twin_with_snapshot IS
    'Atomic twin update: merges state, creates snapshot, logs history — all in one transaction. '
    'State merging uses top-level key merge (partial update). '
    'Implements optimistic concurrency via version check. '
    'Raises P0001 on version conflict, P0002 if twin not found.';


-- =============================================================================
-- 5. ROW LEVEL SECURITY (Optional)
-- =============================================================================
--
-- Enable these policies if you want Supabase RLS protection.
-- The service_role key bypasses RLS, so the backend API is unaffected.
-- These policies protect direct client access via the anon key.
--
-- Prerequisites:
--   - Supabase Auth must be configured
--   - auth.uid() must be available
--
-- Uncomment the block below to enable:
-- =============================================================================

/*
ALTER TABLE entities ENABLE ROW LEVEL SECURITY;
ALTER TABLE digital_twins ENABLE ROW LEVEL SECURITY;
ALTER TABLE twin_snapshots ENABLE ROW LEVEL SECURITY;
ALTER TABLE twin_history ENABLE ROW LEVEL SECURITY;

-- Entity owners can access their own entities
CREATE POLICY entity_owner ON entities
    FOR ALL USING (user_id = auth.uid());

-- Twin access through entity ownership
CREATE POLICY twin_owner ON digital_twins
    FOR ALL USING (
        entity_id IN (SELECT id FROM entities WHERE user_id = auth.uid())
    );

-- Snapshot access through entity ownership
CREATE POLICY snapshot_owner ON twin_snapshots
    FOR ALL USING (
        twin_id IN (
            SELECT dt.id FROM digital_twins dt
            JOIN entities e ON e.id = dt.entity_id
            WHERE e.user_id = auth.uid()
        )
    );

-- History access through entity ownership
CREATE POLICY history_owner ON twin_history
    FOR ALL USING (
        twin_id IN (
            SELECT dt.id FROM digital_twins dt
            JOIN entities e ON e.id = dt.entity_id
            WHERE e.user_id = auth.uid()
        )
    );
*/


-- =============================================================================
-- MIGRATION COMPLETE
-- =============================================================================
-- Verify by running:
--   SELECT table_name FROM information_schema.tables
--   WHERE table_schema = 'public'
--   AND table_name IN ('entities', 'digital_twins', 'twin_snapshots', 'twin_history');
--
-- Expected result: 4 rows
-- =============================================================================
