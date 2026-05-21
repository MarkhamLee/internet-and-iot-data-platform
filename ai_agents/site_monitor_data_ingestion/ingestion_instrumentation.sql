create table if not exists site_monitor_ingestion_runs (
    id bigserial primary key,
    run_uuid uuid not null default gen_random_uuid(),
    started_at timestamptz not null default now(),
    completed_at timestamptz,
    duration_seconds numeric(10,2),
    pipeline_name text not null default 'site_monitor_data_ingestion',
    host_name text,
    process_id integer,
    git_sha text,
    target_count integer not null default 0,
    enabled_target_count integer not null default 0,
    succeeded_target_count integer not null default 0,
    failed_target_count integer not null default 0,
    skipped_target_count integer not null default 0,
    queued_target_count integer not null default 0,
    reminder_sent_count integer not null default 0,
    unchanged_target_count integer not null default 0,
    status text not null default 'running'
        check (status in ('running', 'completed', 'completed_with_errors', 'failed')),
    error_count integer not null default 0,
    warning_count integer not null default 0,
    errors jsonb not null default '[]'::jsonb,
    metadata jsonb not null default '{}'::jsonb
);

create unique index if not exists idx_site_monitor_ingestion_runs_run_uuid
    on site_monitor_ingestion_runs (run_uuid);

create index if not exists idx_site_monitor_ingestion_runs_started_at
    on site_monitor_ingestion_runs (started_at desc);

create table if not exists site_monitor_ingestion_target_runs (
    id bigserial primary key,
    run_id bigint not null references site_monitor_ingestion_runs(id) on delete cascade,
    page_key text not null,
    url text not null,
    started_at timestamptz not null default now(),
    completed_at timestamptz,
    duration_seconds numeric(10,2),
    status text not null
        check (status in (
            'running',
            'skipped_disabled',
            'fetch_failed',
            'extract_failed',
            'hash_failed',
            'queue_failed',
            'reminder_failed',
            'persist_failed',
            'completed'
        )),
    http_status_code integer,
    final_url text,
    http_etag text,
    http_last_modified text,
    content_hash text,
    request_reason text,
    queued_for_research boolean not null default false,
    reminder_attempted boolean not null default false,
    reminder_sent boolean not null default false,
    queue_id bigint,
    error_count integer not null default 0,
    warning_count integer not null default 0,
    errors jsonb not null default '[]'::jsonb,
    metadata jsonb not null default '{}'::jsonb
);

create index if not exists idx_site_monitor_ingestion_target_runs_run_id
    on site_monitor_ingestion_target_runs (run_id);

create index if not exists idx_site_monitor_ingestion_target_runs_page_key_started
    on site_monitor_ingestion_target_runs (page_key, started_at desc);

create index if not exists idx_site_monitor_ingestion_target_runs_status_started
    on site_monitor_ingestion_target_runs (status, started_at desc);
