-- =============================================================================
-- BizOS — Milestone 5: Connector OAuth Tokens Schema Migration
-- =============================================================================
--
-- connector_oauth_tokens: Encrypted OAuth token persistence for all connectors
CREATE TABLE IF NOT EXISTS connector_oauth_tokens (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       TEXT NOT NULL,
    provider_id     TEXT NOT NULL,           -- "google" | "slack" | "microsoft"
    connector_id    TEXT NOT NULL,           -- "gmail" | "slack" | "outlook" | "teams"
    account_id      TEXT NOT NULL DEFAULT 'default',
    access_token    TEXT NOT NULL,           -- Encrypted token
    refresh_token   TEXT,                    -- Encrypted token
    scopes          TEXT[],
    expires_at      TIMESTAMPTZ,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (tenant_id, provider_id, account_id)
);

-- Row-level security: tenants can only access their own tokens
ALTER TABLE connector_oauth_tokens ENABLE ROW LEVEL SECURITY;

DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies 
        WHERE tablename = 'connector_oauth_tokens' AND policyname = 'tenant_isolation'
    ) THEN
        CREATE POLICY tenant_isolation ON connector_oauth_tokens
            USING (tenant_id = current_setting('app.current_tenant_id', true));
    END IF;
END $$;
