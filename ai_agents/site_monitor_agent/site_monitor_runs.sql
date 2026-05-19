create table if not exists site_monitor_runs (
    id bigserial primary key,
    run_uuid uuid not null default gen_random_uuid(),

    started_at timestamptz not null default now(),
    completed_at timestamptz,
    duration_seconds numeric(10,2),

    agent_name text not null default 'site_monitor',
    host_name text,
    process_id integer,
    git_sha text,

    force_review_after_hours integer,

    target_count integer not null default 0,
    enabled_target_count integer not null default 0,
    disabled_target_count integer not null default 0,

    succeeded_target_count integer not null default 0,
    failed_target_count integer not null default 0,
    skipped_target_count integer not null default 0,

    llm_invoked_target_count integer not null default 0,
    slack_attempted_target_count integer not null default 0,
    slack_sent_target_count integer not null default 0,

    status text not null default 'running'
        check (status in (
            'running',
            'completed',
            'completed_with_errors',
            'failed'
        )),

    error_count integer not null default 0,
    warning_count integer not null default 0,

    errors jsonb not null default '[]'::jsonb,
    metadata jsonb not null default '{}'::jsonb
);

create unique index if not exists idx_site_monitor_runs_run_uuid
    on site_monitor_runs (run_uuid);

create index if not exists idx_site_monitor_runs_started_at
    on site_monitor_runs (started_at desc);

create index if not exists idx_site_monitor_runs_status_started_at
    on site_monitor_runs (status, started_at desc);