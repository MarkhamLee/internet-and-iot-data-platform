from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from schemas import ResearchQueueItem


class ResearchQueueStore:
    def __init__(self, dsn: str):
        self.dsn = dsn

    def enqueue_research(
        self,
        *,
        page_key: str,
        url: str,
        request_reason: str,
        content_hash: str | None,
        final_url: str | None,
        http_etag: str | None,
        http_last_modified: str | None,
        pending_reconfirmation: bool,
        payload: dict[str, Any],
        priority: int = 100,
        available_at: datetime | None = None,
        max_attempts: int = 5,
    ) -> int:
        sql = """
        insert into site_monitor_research_queue (
            page_key,
            url,
            requested_at,
            available_at,
            status,
            request_reason,
            priority,
            content_hash,
            final_url,
            http_etag,
            http_last_modified,
            pending_reconfirmation,
            max_attempts,
            payload
        )
        values (
            %(page_key)s,
            %(url)s,
            now(),
            %(available_at)s,
            'pending',
            %(request_reason)s,
            %(priority)s,
            %(content_hash)s,
            %(final_url)s,
            %(http_etag)s,
            %(http_last_modified)s,
            %(pending_reconfirmation)s,
            %(max_attempts)s,
            %(payload)s
        )
        returning id
        """
        row = {
            "page_key": page_key,
            "url": url,
            "available_at": available_at or datetime.now(UTC),
            "request_reason": request_reason,
            "priority": priority,
            "content_hash": content_hash,
            "final_url": final_url,
            "http_etag": http_etag,
            "http_last_modified": http_last_modified,
            "pending_reconfirmation": pending_reconfirmation,
            "max_attempts": max_attempts,
            "payload": Jsonb(payload),
        }
        with psycopg.connect(self.dsn, autocommit=True) as conn:
            with conn.cursor() as cur:
                cur.execute(sql, row)
                result = cur.fetchone()
                if result is None:
                    raise RuntimeError("enqueue_research() did not return an id")  # noqa: E501
                return int(result[0])

    def claim_next(self) -> ResearchQueueItem | None:
        sql = """
        with next_item as (
            select id
            from site_monitor_research_queue
            where status = 'pending'
              and available_at <= now()
              and attempt_count < max_attempts
            order by priority asc, requested_at asc
            for update skip locked
            limit 1
        )
        update site_monitor_research_queue q
        set
            status = 'in_progress',
            claimed_at = now(),
            attempt_count = attempt_count + 1
        from next_item
        where q.id = next_item.id
        returning
            q.id,
            q.page_key,
            q.url,
            q.requested_at,
            q.available_at,
            q.claimed_at,
            q.completed_at,
            q.status,
            q.request_reason,
            q.priority,
            q.content_hash,
            q.final_url,
            q.http_etag,
            q.http_last_modified,
            q.pending_reconfirmation,
            q.attempt_count,
            q.max_attempts,
            q.last_error,
            q.errors,
            q.payload,
            q.result_reviewed_at,
            q.result_page_status,
            q.result_event_type
        """
        with psycopg.connect(self.dsn,
                             autocommit=True,
                             row_factory=dict_row) as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
                row = cur.fetchone()
                return ResearchQueueItem(**row) if row else None

    def mark_completed(
        self,
        *,
        queue_id: int,
        reviewed_at: datetime,
        page_status: str,
        event_type: str,
    ) -> None:
        sql = """
        update site_monitor_research_queue
        set
            status = 'completed',
            completed_at = %(completed_at)s,
            result_reviewed_at = %(result_reviewed_at)s,
            result_page_status = %(result_page_status)s,
            result_event_type = %(result_event_type)s,
            last_error = null
        where id = %(id)s
        """
        payload = {
            "id": queue_id,
            "completed_at": reviewed_at,
            "result_reviewed_at": reviewed_at,
            "result_page_status": page_status,
            "result_event_type": event_type,
        }
        with psycopg.connect(self.dsn, autocommit=True) as conn:
            with conn.cursor() as cur:
                cur.execute(sql, payload)

    def mark_failed(
        self,
        *,
        queue_id: int,
        error_message: str,
        details: dict[str, Any] | None = None,
        retry_delay_minutes: int = 15,
    ) -> None:
        sql = """
        update site_monitor_research_queue
        set
            status = case when attempt_count >= max_attempts then 'failed' else 'pending' end,
            available_at = case when attempt_count >= max_attempts then available_at else %(available_at)s end,
            last_error = %(last_error)s,
            errors = errors || jsonb_build_array(
                jsonb_build_object(
                    'message', %(last_error)s,
                    'details', %(details)s,
                    'recorded_at', now()
                )
            )
        where id = %(id)s
        """
        payload = {
            "id": queue_id,
            "available_at": datetime.now(UTC) + timedelta(minutes=retry_delay_minutes),  # noqa: E501
            "last_error": error_message,
            "details": Jsonb(details or {}),
        }
        with psycopg.connect(self.dsn, autocommit=True) as conn:
            with conn.cursor() as cur:
                cur.execute(sql, payload)
