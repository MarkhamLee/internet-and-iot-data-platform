create table if not exists site_monitor_target_runs (
    id bigserial primary key,
    run_id bigint not null references site_monitor_runs(id) on delete cascade,

    page_key text not null,
    url text not null,

    started_at timestamptz not null default now(),
    completed_at timestamptz,
    duration_seconds numeric(10,2),

    fetch_duration_seconds numeric(10,2),
    extract_duration_seconds numeric(10,2),
    review_duration_seconds numeric(10,2),
    slack_duration_seconds numeric(10,2),
    persist_duration_seconds numeric(10,2),

    status text not null
        check (status in (
            'running',
            'skipped_disabled',
            'skipped_http_304',
            'skipped_no_review_needed',
            'fetch_failed',
            'extract_failed',
            'decision_failed',
            'review_failed',
            'slack_failed',
            'persist_failed',
            'completed',
            'failed'
        )),

    llm_invoked boolean not null default false,
    slack_attempted boolean not null default false,
    slack_sent boolean not null default false,

    http_status_code integer,
    final_url text,
    http_etag text,
    http_last_modified text,

    content_hash text,
    review_reason text,
    event_type text,

    page_status text,
    confidence numeric(6,5),
    normalized_state_key text,

    error_count integer not null default 0,
    warning_count integer not null default 0,
    errors jsonb not null default '[]'::jsonb,
    metadata jsonb not null default '{}'::jsonb
);

create index if not exists idx_site_monitor_target_runs_run_id
    on site_monitor_target_runs (run_id);

create index if not exists idx_site_monitor_target_runs_page_key_started
    on site_monitor_target_runs (page_key, started_at desc);

create index if not exists idx_site_monitor_target_runs_status_started
    on site_monitor_target_runs (status, started_at desc);
