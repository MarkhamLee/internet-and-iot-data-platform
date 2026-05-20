from __future__ import annotations

import psycopg
from datetime import UTC, datetime
from psycopg.rows import dict_row
from schemas import TrackedPageState
from typing import Any


class StateStore:
    def __init__(self, dsn: str):
        self.dsn = dsn

    def get_current_state(self, page_key: str) -> TrackedPageState | None:
        sql = """
        select
            page_key,
            url,
            current_status,
            first_seen_at,
            last_checked_at,
            state_changed_at,
            desired_state_started_at,
            undesired_state_started_at,
            last_reminder_sent_at,
            last_slack_message_type,
            last_review_summary,
            last_state_key,
            last_http_etag,
            last_http_last_modified,
            last_content_hash,
            last_llm_reviewed_hash,
            research_needed,
            research_requested_at,
            pending_reconfirmation,
            pending_content_hash,
            pending_final_url,
            pending_http_etag,
            pending_http_last_modified,
            last_research_completed_at,
            last_research_queue_id
        from page_watch_current
        where page_key = %s
        """

        with psycopg.connect(self.dsn,
                             autocommit=True,
                             row_factory=dict_row) as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (page_key,))
                row = cur.fetchone()
                if row is None:
                    return None
                return TrackedPageState(**row)

    def ensure_tracking_row(self,
                            *,
                            page_key: str,
                            url: str,
                            now: datetime) -> None:
        sql = """
        insert into page_watch_current (
            page_key,
            url,
            current_status,
            first_seen_at,
            last_checked_at,
            state_changed_at,
            research_needed,
            pending_reconfirmation
        )
        values (%s, %s, 'unknown', %s, %s, %s, false, false)
        on conflict (page_key) do nothing
        """

        with psycopg.connect(self.dsn, autocommit=True) as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (page_key, url, now, now, now))

    def record_collection_check(
        self,
        *,
        page_key: str,
        url: str,
        now: datetime,
        http_etag: str | None,
        http_last_modified: str | None,
        content_hash: str | None,
        final_url: str | None,
    ) -> None:
        self.ensure_tracking_row(page_key=page_key, url=url, now=now)

        sql = """
        update page_watch_current
        set
            url = %(url)s,
            last_checked_at = %(last_checked_at)s,
            last_http_etag = %(last_http_etag)s,
            last_http_last_modified = %(last_http_last_modified)s,
            last_content_hash = coalesce(%(last_content_hash)s, last_content_hash),
            pending_final_url = coalesce(%(pending_final_url)s, pending_final_url)
        where page_key = %(page_key)s
        """

        payload: dict[str, Any] = {
            "page_key": page_key,
            "url": url,
            "last_checked_at": now,
            "last_http_etag": http_etag,
            "last_http_last_modified": http_last_modified,
            "last_content_hash": content_hash,
            "pending_final_url": final_url,
        }

        with psycopg.connect(self.dsn, autocommit=True) as conn:
            with conn.transaction():
                with conn.cursor() as cur:
                    cur.execute(sql, payload)

    def mark_research_pending(
        self,
        *,
        page_key: str,
        url: str,
        now: datetime,
        content_hash: str,
        queue_id: int,
        pending_reconfirmation: bool,
        final_url: str | None,
        http_etag: str | None,
        http_last_modified: str | None,
    ) -> None:
        self.ensure_tracking_row(page_key=page_key, url=url, now=now)

        sql = """
        update page_watch_current
        set
            url = %(url)s,
            research_needed = true,
            research_requested_at = %(research_requested_at)s,
            pending_reconfirmation = %(pending_reconfirmation)s,
            pending_content_hash = %(pending_content_hash)s,
            pending_final_url = %(pending_final_url)s,
            pending_http_etag = %(pending_http_etag)s,
            pending_http_last_modified = %(pending_http_last_modified)s,
            last_research_queue_id = %(last_research_queue_id)s
        where page_key = %(page_key)s
        """

        payload = {
            "page_key": page_key,
            "url": url,
            "research_requested_at": now,
            "pending_reconfirmation": pending_reconfirmation,
            "pending_content_hash": content_hash,
            "pending_final_url": final_url,
            "pending_http_etag": http_etag,
            "pending_http_last_modified": http_last_modified,
            "last_research_queue_id": queue_id,
        }

        with psycopg.connect(self.dsn, autocommit=True) as conn:
            with conn.transaction():
                with conn.cursor() as cur:
                    cur.execute(sql, payload)

    def record_reminder_sent(
        self,
        *,
        page_key: str,
        sent_at: datetime,
        message_type: str = "desired_reminder",
    ) -> None:
        sql = """
        update page_watch_current
        set
            last_reminder_sent_at = %s,
            last_slack_message_type = %s
        where page_key = %s
        """

        with psycopg.connect(self.dsn, autocommit=True) as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (sent_at, message_type, page_key))


def should_enqueue_research(
    previous: TrackedPageState | None,
    content_hash: str,
    now: datetime,
    force_research_after_hours: int | None = None,
) -> tuple[bool, str]:
    if previous is None:
        return True, "first_observation"

    if previous.current_status == "unknown":
        return True, "previous_unknown"

    if previous.last_llm_reviewed_hash != content_hash:
        return True, "content_changed"

    if force_research_after_hours is not None and previous.last_checked_at:
        elapsed = now - previous.last_checked_at
        if elapsed.total_seconds() >= force_research_after_hours * 3600:
            return True, "forced_refresh"

    return False, "content_unchanged"


def build_research_queue_payload(
    *,
    target,
    review_payload: dict[str, Any],
    content_hash: str,
    request_reason: str,
    previous: TrackedPageState | None,
    pending_reconfirmation: bool,
) -> dict[str, Any]:
    return {
        "review_payload": {
            "url": review_payload.get("url"),
            "final_url": review_payload.get("final_url"),
            "fetched_at": review_payload.get("fetched_at"),
            "selector_hits": review_payload.get("selector_hits", []),
            "pattern_hits": review_payload.get("pattern_hits", []),
            "button_texts": review_payload.get("button_texts", []),
            "page_text_excerpt": review_payload.get("page_text_excerpt", ""),
            "desired_state_description": target.desired_state_description,
            "undesired_state_description": target.undesired_state_description,
            "custom_prompt": target.custom_prompt,
        },
        "target_metadata": {
            "page_key": target.page_key,
            "url": str(target.url),
            "reminder_interval_minutes": target.reminder_interval_minutes,
            "send_missed_it_message": target.send_missed_it_message,
            "slack_channel": target.slack_channel,
        },
        "collection_context": {
            "content_hash": content_hash,
            "request_reason": request_reason,
            "pending_reconfirmation": pending_reconfirmation,
            "previous_last_llm_reviewed_hash": (
                previous.last_llm_reviewed_hash if previous else None
            ),
            "previous_last_content_hash": (
                previous.last_content_hash if previous else None
            ),
            "queued_at": datetime.now(UTC).isoformat(),
        },
    }
