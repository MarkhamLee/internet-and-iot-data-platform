create table if not exists page_watch_current (
    page_key text primary key,
    url text not null,
    current_status text not null check (
        current_status in ('desired', 'undesired', 'unknown')
    ),
    first_seen_at timestamptz not null,
    last_checked_at timestamptz not null,
    state_changed_at timestamptz not null,
    desired_state_started_at timestamptz null,
    undesired_state_started_at timestamptz null,
    last_reminder_sent_at timestamptz null,
    last_slack_message_type text null,
    last_review_summary text null,
    last_state_key text null,
    last_http_etag text null,
    last_http_last_modified text null,
    last_content_hash text null,
    last_llm_reviewed_hash text null,
    check (
        not (
            desired_state_started_at is not null
            and undesired_state_started_at is not null
        )
    )
);