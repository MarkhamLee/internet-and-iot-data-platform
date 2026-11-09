# (C) Markham Lee 2023 - 2026
# https://github.com/MarkhamLee/internet-and-iot-data-platform
# PostgreSQL repository for the site monitor research queue
from __future__ import annotations

from datetime import datetime
import psycopg
from psycopg.rows import dict_row
from schemas import ResearchQueueItem, PageAnalysisWrite
from platform_utils.platform_logger import configure_logger

logger = configure_logger("postgres_queue_repository")
ALLOWED_PAGE_STATUSES = frozenset({"desired", "undesired", "unknown"})


def validate_page_status(status: str, desired_state_found: bool) -> None:
    if status not in ALLOWED_PAGE_STATUSES:
        raise ValueError(f"Invalid page status: {status!r}")
    if type(desired_state_found) is not bool:
        raise ValueError("desired_state_found must be a bool")
    if desired_state_found != (status == "desired"):
        raise ValueError("Page status contradicts desired_state_found")


class PostgresQueueRepository:
    def __init__(self, dsn: str) -> None:
        self.dsn = dsn
        self.conn = None

    def connect(self) -> None:
        if self.conn is None or self.conn.closed:
            self.conn = psycopg.connect(self.dsn, autocommit=True)

    def close(self) -> None:
        if self.conn is not None and not self.conn.closed:
            self.conn.close()

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()

    def fetch_pending_items(self, limit: int = 10) -> list[ResearchQueueItem]:
        sql = """
        SELECT * FROM site_monitor_research_queue
        WHERE status IN ('pending', 'failed')
          AND (available_at IS NULL OR available_at <= NOW())
          AND attempt_count < max_attempts
        ORDER BY priority DESC, requested_at ASC LIMIT %s
        """
        with psycopg.connect(self.dsn,
                             autocommit=True,
                             row_factory=dict_row) as conn:
            with conn.cursor() as cur:
                cur.execute(sql, [limit])
                return [ResearchQueueItem.model_validate(row) for row in cur.fetchall()]

    def claim_item(self, queue_id: int, now: datetime) -> bool:
        """Minimal ownership guard; duplicate-active-work 
        retry reconciliation is Phase 2."""

        sql = """
        UPDATE site_monitor_research_queue
        SET status = 'in_progress', claimed_at = %(now)s,
            completed_at = NULL, attempt_count = attempt_count + 1
        WHERE id = %(queue_id)s AND status IN ('pending', 'failed')
          AND (available_at IS NULL OR available_at <= %(now)s)
          AND attempt_count < max_attempts
        RETURNING id
        """
        with psycopg.connect(self.dsn, autocommit=True) as conn:
            with conn.cursor() as cur:
                cur.execute(sql, {"queue_id": queue_id, "now": now})
                return cur.fetchone() is not None

    def fail_item(self,
                  *,
                  queue_id: int,
                  now: datetime,
                  error_message: str) -> None:
        sql = """
        UPDATE site_monitor_research_queue
        SET status = 'failed', completed_at = %(now)s,
            last_error = %(error_message)s,
            errors = COALESCE(errors, '[]'::jsonb) || jsonb_build_array(
                jsonb_build_object('at', %(now)s::text,
                'error',
                %(error_message)s::text))
        WHERE id = %(queue_id)s AND status = 'in_progress'
        """
        with psycopg.connect(self.dsn, autocommit=True) as conn:
            with conn.cursor() as cur:
                cur.execute(sql, {"queue_id": queue_id, "now": now,
                                  "error_message": error_message})
                if cur.rowcount != 1:
                    raise RuntimeError(f"Cannot fail unowned/non-active queue item {queue_id}")  # noqa: E501

    def complete_research(self, *, item: ResearchQueueItem,
                          result: PageAnalysisWrite, now: datetime) -> None:
        """Commit state and queue completion together;
        never perform Slack I/O here."""

        validate_page_status(result.result_page_status,
                             result.desired_state_found)

        if (result.queue_id, result.page_key, result.url) != (item.id,
                                                              item.page_key,
                                                              item.url):
            raise ValueError("Research result identity does not match queue item")  # noqa: E501
        if not item.content_hash:
            raise ValueError("A reviewed content hash is required")
        params = {"queue_id": item.id, "page_key": item.page_key,
                  "current_status": result.result_page_status,
                  "summary": result.summary,
                  "content_hash": item.content_hash, "now": now,
                  "event_type": result.result_event_type}
        state_sql = """
        UPDATE page_watch_current
        SET current_status = %(current_status)s,
            last_review_summary = %(summary)s,
            last_llm_reviewed_hash = %(content_hash)s,
            last_research_completed_at = %(now)s,
            last_research_queue_id = %(queue_id)s,
            research_needed = false, research_requested_at = NULL,
            pending_reconfirmation = false, pending_content_hash = NULL,
            pending_final_url = NULL, pending_http_etag = NULL,
            pending_http_last_modified = NULL,
            state_changed_at = CASE
                WHEN current_status IS DISTINCT FROM %(current_status)s THEN %(now)s
                ELSE state_changed_at END,
            desired_state_started_at = CASE
                WHEN %(current_status)s <> 'desired' THEN NULL
                WHEN current_status = 'desired' THEN
                    COALESCE(desired_state_started_at, state_changed_at, %(now)s)
                ELSE %(now)s END,
            undesired_state_started_at = CASE
                WHEN %(current_status)s <> 'undesired' THEN NULL
                WHEN current_status = 'undesired' THEN
                    COALESCE(undesired_state_started_at, state_changed_at, %(now)s)
                ELSE %(now)s END,
            reminder_count = CASE
                WHEN current_status IS DISTINCT FROM %(current_status)s THEN 0
                ELSE reminder_count END,
            last_reminder_sent_at = CASE
                WHEN current_status IS DISTINCT FROM %(current_status)s THEN NULL
                ELSE last_reminder_sent_at END
        WHERE page_key = %(page_key)s
        """
        queue_sql = """
        UPDATE site_monitor_research_queue
        SET status = 'completed', completed_at = %(now)s,
            result_reviewed_at = %(now)s, result_page_status = %(current_status)s,
            result_event_type = %(event_type)s, last_error = NULL
        WHERE id = %(queue_id)s AND page_key = %(page_key)s AND status = 'in_progress'
        """
        with psycopg.connect(self.dsn) as conn:
            with conn.transaction():
                with conn.cursor() as cur:
                    cur.execute("""SELECT page_key, content_hash, status
                        FROM site_monitor_research_queue WHERE id = %s FOR UPDATE""", [item.id])  # noqa: E501
                    row = cur.fetchone()
                    if row != (item.page_key,
                               item.content_hash,
                               'in_progress'):
                        raise RuntimeError(f"Queue item {item.id} is missing, changed, or not claimed")  # noqa: E501
                    cur.execute(state_sql, params)
                    if cur.rowcount != 1:
                        raise RuntimeError(f"Missing state row for {item.page_key}; transaction rolled back")  # noqa: E501
                    cur.execute(queue_sql, params)
                    if cur.rowcount != 1:
                        raise RuntimeError(f"Queue completion failed for {item.id}; transaction rolled back")  # noqa: E501
        logger.info("Research committed queue_id=%s page_key=%s status=%s",
                    item.id, item.page_key, result.result_page_status)
