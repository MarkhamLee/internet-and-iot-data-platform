from __future__ import annotations

import psycopg
from datetime import UTC, datetime
from psycopg.rows import dict_row
from schemas import ResearchQueueItem
from typing import Any


class ResearchQueueStore:
    def __init__(self, dsn: str):
        self.dsn = dsn

    def get_pending_by_page_and_hash(
        self,
        *,
        page_key: str,
        content_hash: str,
    ) -> ResearchQueueItem | None:
        sql = """
        select *
        from site_monitor_research_queue
        where page_key = %s
          and content_hash = %s
          and status in ('pending', 'in_progress')
        order by requested_at desc
        limit 1
        """

        with psycopg.connect(self.dsn,
                             autocommit=True,
                             row_factory=dict_row) as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (page_key, content_hash))
                row = cur.fetchone()
                if row is None:
                    return None
                return ResearchQueueItem(**row)

    def enqueue_research(
        self,
        *,
        page_key: str,
        url: str,
        request_reason: str,
        content_hash: str,
        final_url: str | None,
        http_etag: str | None,
        http_last_modified: str | None,
        pending_reconfirmation: bool,
        payload: dict[str, Any],
        available_at: datetime | None = None,
        priority: int = 100,
    ) -> int:
        existing = self.get_pending_by_page_and_hash(
            page_key=page_key,
            content_hash=content_hash,
        )
        if existing is not None:
            return existing.id

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
            payload
        )
        values (
            %(page_key)s,
            %(url)s,
            %(requested_at)s,
            %(available_at)s,
            'pending',
            %(request_reason)s,
            %(priority)s,
            %(content_hash)s,
            %(final_url)s,
            %(http_etag)s,
            %(http_last_modified)s,
            %(pending_reconfirmation)s,
            %(payload)s
        )
        returning id
        """

        now = datetime.now(UTC)
        sql_payload = {
            "page_key": page_key,
            "url": url,
            "requested_at": now,
            "available_at": available_at or now,
            "request_reason": request_reason,
            "priority": priority,
            "content_hash": content_hash,
            "final_url": final_url,
            "http_etag": http_etag,
            "http_last_modified": http_last_modified,
            "pending_reconfirmation": pending_reconfirmation,
            "payload": payload,
        }

        with psycopg.connect(self.dsn, autocommit=True) as conn:
            with conn.transaction():
                with conn.cursor() as cur:
                    cur.execute(sql, sql_payload)
                    row = cur.fetchone()
                    return int(row[0])
