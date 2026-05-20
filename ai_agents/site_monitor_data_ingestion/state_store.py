# (C) Markham Lee 2023 - 2026
# https://github.com/MarkhamLee/internet-and-iot-data-platform
# stores results of data ingestion, alert status, etc., in Postgres
from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import psycopg
from psycopg.rows import dict_row

from schemas import PageReviewResult, TrackedPageState


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
            last_http_etag = coalesce(%(last_http_etag)s, last_http_etag),
            last_http_last_modified = coalesce(%(last_http_last_modified)s, last_http_last_modified),
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
            last_checked_at = %(last_checked_at)s,
            research_needed = true,
            research_requested_at = %(research_requested_at)s,
            pending_reconfirmation = %(pending_reconfirmation)s,
            pending_content_hash = %(pending_content_hash)s,
            pending_final_url = %(pending_final_url)s,
            pending_http_etag = %(pending_http_etag)s,
            pending_http_last_modified = %(pending_http_last_modified)s,
            last_research_queue_id = %(last_research_queue_id)s,
            last_content_hash = coalesce(%(pending_content_hash)s, last_content_hash),
            last_http_etag = coalesce(%(pending_http_etag)s, last_http_etag),
            last_http_last_modified = coalesce(%(pending_http_last_modified)s, last_http_last_modified)
        where page_key = %(page_key)s
        """
        payload: dict[str, Any] = {
            "page_key": page_key,
            "url": url,
            "last_checked_at": now,
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

    def save_research_result(
        self,
        *,
        queue_id: int,
        page_key: str,
        url: str,
        review: PageReviewResult,
        observed_at: datetime,
        event_type: str,
        slack_sent: bool,
        send_time: datetime | None,
        previous: TrackedPageState | None,
        http_etag: str | None,
        http_last_modified: str | None,
        content_hash: str | None,
        llm_invoked: bool,
        pipeline_name: str = "site_monitor_research",
        pending_reconfirmation: bool | None = None,
    ) -> None:
        desired_started_at = self._desired_started_at(previous=previous,
                                                      current_status=review.
                                                      page_status,
                                                      now=observed_at)
        undesired_started_at = self._undesired_started_at(previous=previous,
                                                          current_status=review.page_status,  # noqa: E501
                                                          now=observed_at)
        state_changed_at = self._state_changed_at(previous=previous,
                                                  current_status=review.
                                                  page_status,
                                                  now=observed_at)
        last_reminder_sent_at = send_time\
            if send_time is not None else previous.\
            last_reminder_sent_at if previous else None

        upsert_sql = """
        insert into page_watch_current (
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
        )
        values (
            %(page_key)s,
            %(url)s,
            %(current_status)s,
            %(first_seen_at)s,
            %(last_checked_at)s,
            %(state_changed_at)s,
            %(desired_state_started_at)s,
            %(undesired_state_started_at)s,
            %(last_reminder_sent_at)s,
            %(last_slack_message_type)s,
            %(last_review_summary)s,
            %(last_state_key)s,
            %(last_http_etag)s,
            %(last_http_last_modified)s,
            %(last_content_hash)s,
            %(last_llm_reviewed_hash)s,
            false,
            null,
            false,
            null,
            null,
            null,
            null,
            %(last_research_completed_at)s,
            %(last_research_queue_id)s
        )
        on conflict (page_key) do update set
            url = excluded.url,
            current_status = excluded.current_status,
            last_checked_at = excluded.last_checked_at,
            state_changed_at = excluded.state_changed_at,
            desired_state_started_at = excluded.desired_state_started_at,
            undesired_state_started_at = excluded.undesired_state_started_at,
            last_reminder_sent_at = excluded.last_reminder_sent_at,
            last_slack_message_type = excluded.last_slack_message_type,
            last_review_summary = excluded.last_review_summary,
            last_state_key = excluded.last_state_key,
            last_http_etag = excluded.last_http_etag,
            last_http_last_modified = excluded.last_http_last_modified,
            last_content_hash = excluded.last_content_hash,
            last_llm_reviewed_hash = excluded.last_llm_reviewed_hash,
            research_needed = false,
            research_requested_at = null,
            pending_reconfirmation = false,
            pending_content_hash = null,
            pending_final_url = null,
            pending_http_etag = null,
            pending_http_last_modified = null,
            last_research_completed_at = excluded.last_research_completed_at,
            last_research_queue_id = excluded.last_research_queue_id
        """

        event_sql = """
        insert into page_watch_event (
            page_key,
            url,
            observed_at,
            event_type,
            page_status,
            confidence,
            summary,
            evidence,
            extracted_price,
            extracted_title,
            normalized_state_key,
            slack_sent,
            http_etag,
            http_last_modified,
            content_hash,
            llm_invoked,
            pipeline_name,
            research_queue_id,
            pending_reconfirmation
        )
        values (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
        """

        upsert_payload: dict[str, Any] = {
            "page_key": page_key,
            "url": url,
            "current_status": review.page_status,
            "first_seen_at": previous.first_seen_at if previous else observed_at,  # noqa: E501
            "last_checked_at": observed_at,
            "state_changed_at": state_changed_at,
            "desired_state_started_at": desired_started_at,
            "undesired_state_started_at": undesired_started_at,
            "last_reminder_sent_at": last_reminder_sent_at,
            "last_slack_message_type": event_type,
            "last_review_summary": review.summary,
            "last_state_key": review.normalized_state_key,
            "last_http_etag": http_etag if http_etag is not None else previous.last_http_etag if previous else None,  # noqa: E501
            "last_http_last_modified": http_last_modified if http_last_modified is not None else previous.last_http_last_modified if previous else None,  # noqa: E501
            "last_content_hash": content_hash if content_hash is not None else previous.last_content_hash if previous else None,  # noqa: E501
            "last_llm_reviewed_hash": content_hash if llm_invoked else previous.last_llm_reviewed_hash if previous else None,  # noqa: E501
            "last_research_completed_at": observed_at,
            "last_research_queue_id": queue_id,
        }

        event_params = (
            page_key,
            url,
            observed_at,
            event_type,
            review.page_status,
            review.confidence,
            review.summary,
            review.evidence,
            review.extracted_price,
            review.extracted_title,
            review.normalized_state_key,
            slack_sent,
            http_etag,
            http_last_modified,
            content_hash,
            llm_invoked,
            pipeline_name,
            queue_id,
            pending_reconfirmation,
        )

        with psycopg.connect(self.dsn, autocommit=True) as conn:
            with conn.transaction():
                with conn.cursor() as cur:
                    cur.execute(upsert_sql, upsert_payload)
                    cur.execute(event_sql, event_params)

    @staticmethod
    def _desired_started_at(previous: TrackedPageState | None,
                            current_status: str,
                            now: datetime) -> datetime | None:
        if current_status != "desired":
            return None
        if previous and previous.current_status == "desired":
            return previous.desired_state_started_at or previous.\
                state_changed_at
        return now

    @staticmethod
    def _undesired_started_at(previous: TrackedPageState | None,
                              current_status: str,
                              now: datetime) -> datetime | None:
        if current_status != "undesired":
            return None
        if previous and previous.current_status == "undesired":
            return previous.\
                undesired_state_started_at or previous.state_changed_at
        return now

    @staticmethod
    def _state_changed_at(previous: TrackedPageState | None,
                          current_status: str,
                          now: datetime) -> datetime:
        if previous and previous.current_status == current_status:
            return previous.state_changed_at
        return now


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
            "previous_last_llm_reviewed_hash": previous.last_llm_reviewed_hash if previous else None,  # noqa: E501
            "previous_last_content_hash": previous.last_content_hash if previous else None,  # noqa: E501
            "queued_at": datetime.now(UTC).isoformat(),
        },
    }
