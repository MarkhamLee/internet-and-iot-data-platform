create table if not exists site_monitor_research_queue (
    id bigserial primary key,

    page_key text not null,
    url text not null,

    requested_at timestamptz not null default now(),
    available_at timestamptz not null default now(),
    claimed_at timestamptz,
    completed_at timestamptz,

    status text not null default 'pending'
        check (status in (
            'pending',
            'in_progress',
            'completed',
            'failed',
            'cancelled'
        )),

    request_reason text not null,
    priority smallint not null default 100,

    content_hash text,
    final_url text,
    http_etag text,
    http_last_modified text,

    pending_reconfirmation boolean not null default false,

    attempt_count integer not null default 0,
    max_attempts integer not null default 5,

    last_error text,
    errors jsonb not null default '[]'::jsonb,
    payload jsonb not null default '{}'::jsonb,

    result_reviewed_at timestamptz,
    result_page_status text,
    result_event_type text,

    constraint chk_site_monitor_research_queue_attempts
        check (attempt_count >= 0 and max_attempts > 0)
);

create index if not exists idx_site_monitor_research_queue_status_available
    on site_monitor_research_queue (status, available_at, requested_at);

create index if not exists idx_site_monitor_research_queue_page_key_requested
    on site_monitor_research_queue (page_key, requested_at desc);

create index if not exists idx_site_monitor_research_queue_content_hash
    on site_monitor_research_queue (content_hash);

create unique index if not exists uq_site_monitor_research_queue_pending_unique
    on site_monitor_research_queue (page_key, content_hash)
    where status in ('pending', 'in_progress');