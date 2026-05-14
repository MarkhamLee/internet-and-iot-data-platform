create table if not exists page_watch_event (
    id bigserial primary key,
    page_key text not null references page_watch_current(page_key) on delete cascade,
    url text not null,
    observed_at timestamptz not null,
    event_type text not null,
    page_status text not null check (
        page_status in ('desired', 'undesired', 'unknown')
    ),
    confidence numeric(4,3) null check (
        confidence is null or (confidence >= 0 and confidence <= 1)
    ),
    summary text null,
    evidence text[] not null default ARRAY[]::text[],
    extracted_price text null,
    extracted_title text null,
    normalized_state_key text null,
    slack_sent boolean not null default false
);

create index if not exists idx_page_watch_event_page_key_observed_at
    on page_watch_event (page_key, observed_at desc);

create index if not exists idx_page_watch_current_last_checked_at
    on page_watch_current (last_checked_at);