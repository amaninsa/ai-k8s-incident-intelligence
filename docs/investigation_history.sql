-- Investigation history table for InsForge PostgreSQL
-- Run this in your InsForge SQL console or via the run-raw-sql MCP tool.

CREATE TABLE IF NOT EXISTS investigation_history (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id TEXT NOT NULL,
  timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  cluster TEXT NOT NULL,
  namespace TEXT,
  root_cause TEXT NOT NULL,
  confidence INTEGER NOT NULL DEFAULT 0,
  status TEXT NOT NULL DEFAULT 'success',
  diagnosis JSONB,
  investigation JSONB,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_investigation_history_user_id
  ON investigation_history(user_id);

CREATE INDEX IF NOT EXISTS idx_investigation_history_timestamp
  ON investigation_history(timestamp DESC);

ALTER TABLE investigation_history ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS investigation_history_select_own ON investigation_history;
CREATE POLICY investigation_history_select_own ON investigation_history
  FOR SELECT USING (auth.uid() = user_id);

DROP POLICY IF EXISTS investigation_history_insert_own ON investigation_history;
CREATE POLICY investigation_history_insert_own ON investigation_history
  FOR INSERT WITH CHECK (auth.uid() = user_id);
