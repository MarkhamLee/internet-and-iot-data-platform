create table if not exists page_watch_event (
    id bigserial primary key,
    page_key text not null,
    url text not null,
    observed_at timestamptz not null,
    event_type text not null,
    page_status text not null check (page_status in ('desired', 'undesired', 'unknown')),
    confidence numeric(4,3) null,
    summary text null,
    evidence text[] not null default '{}',
    extracted_price text null,
    extracted_title text null,
    normalized_state_key text null,
    slack_sent boolean not null default false
);

create index if not exists idx_page_watch_event_page_key_observed_at
    on page_watch_event (page_key, observed_at desc);