CREATE TABLE IF NOT EXISTS dependabot_alerts (
    alert_id                TEXT PRIMARY KEY,                -- "{owner}/{repo}#{number}"
    repo_owner              TEXT NOT NULL,
    repo_name               TEXT NOT NULL,
    repo_full_name          TEXT NOT NULL,                  -- "{owner}/{repo}"
    repo_html_url           TEXT,
    repo_api_url            TEXT,
    alert_number            INT NOT NULL,
    github_state            TEXT NOT NULL,                  -- open, fixed, dismissed, auto_dismissed, closed_pending_reason
    package_name            TEXT NOT NULL,
    ecosystem               TEXT NOT NULL,
    manifest_path           TEXT,
    scope                   TEXT,
    relationship            TEXT,
    severity                TEXT,
    summary                 TEXT,
    description             TEXT,
    cve_id                  TEXT,
    ghsa_id                 TEXT,
    vulnerable_version_range TEXT,
    first_patched_version   TEXT,
    alert_html_url          TEXT,
    source_fingerprint      TEXT NOT NULL,
    review_group_key        TEXT NOT NULL,                  -- repo/package/manifest grouping key
    needs_review            BOOLEAN NOT NULL DEFAULT TRUE,
    review_reason           TEXT,
    first_seen_at           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_seen_open_at       TIMESTAMPTZ,
    last_state_change_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_synced_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_researched_at      TIMESTAMPTZ,
    latest_research_json    JSONB,
    slack_channel_id        TEXT,
    slack_message_ts        TEXT,
    reminder_count          INT NOT NULL DEFAULT 0,
    resolved_at             TIMESTAMPTZ,
    raw_alert_json          JSONB NOT NULL,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_dependabot_alerts_repo_state
    ON dependabot_alerts (repo_full_name, github_state);

CREATE INDEX IF NOT EXISTS idx_dependabot_alerts_needs_review
    ON dependabot_alerts (needs_review, github_state);

CREATE INDEX IF NOT EXISTS idx_dependabot_alerts_last_researched
    ON dependabot_alerts (last_researched_at);

CREATE INDEX IF NOT EXISTS idx_dependabot_alerts_review_group_key
    ON dependabot_alerts (review_group_key);

CREATE INDEX IF NOT EXISTS idx_dependabot_alerts_ghsa_id
    ON dependabot_alerts (ghsa_id);