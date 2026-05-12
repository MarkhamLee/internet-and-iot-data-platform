CREATE TABLE IF NOT EXISTS dependabot_alert_reviews (
    review_id               BIGSERIAL PRIMARY KEY,
    alert_id                TEXT NOT NULL REFERENCES dependabot_alerts(alert_id) ON DELETE CASCADE,
    repo_full_name          TEXT NOT NULL,
    review_group_key        TEXT NOT NULL,
    review_reason           TEXT NOT NULL,                  -- new_alert, alert_changed, stale_research, manual_recheck
    model_name              TEXT,
    prompt_version          TEXT,
    recommendation          TEXT,
    priority                TEXT,
    confidence              TEXT,
    risksummary             TEXT,
    reasoning               TEXT,
    research_json           JSONB,
    assessment_json         JSONB,
    reviewed_at             TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_dependabot_alert_reviews_alert_id
    ON dependabot_alert_reviews (alert_id);

CREATE INDEX IF NOT EXISTS idx_dependabot_alert_reviews_group_key
    ON dependabot_alert_reviews (review_group_key);

CREATE INDEX IF NOT EXISTS idx_dependabot_alert_reviews_reviewed_at
    ON dependabot_alert_reviews (reviewed_at);