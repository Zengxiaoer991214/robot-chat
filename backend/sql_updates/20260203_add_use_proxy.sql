-- Version: 1.2
-- Date: 2026-02-03
-- Description: Add use_proxy column to agents table.
-- Enable selective proxy usage for agents (e.g. for DashScope/OpenAI).

ALTER TABLE agents ADD COLUMN use_proxy BOOLEAN NOT NULL DEFAULT FALSE;
