# (C) Markham Lee 2023 - 2026
# https://github.com/MarkhamLee/internet-and-iot-data-platform
# PostgreSQL repository for the site monitor research queue

from __future__ import annotations

from datetime import datetime
import psycopg
from psycopg.rows import dict_row
from schemas import (
    ResearchQueueItem,
    PageAnalysisWrite,
    ResearchCompletion,
    decide_initial_alert,
)
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
        if limit < 1:
            raise ValueError("limit must be positive")
        sql = """
        SELECT q.* FROM site_monitor_research_queue q
        WHERE q.status IN ('pending', 'failed')
          AND (q.available_at IS NULL OR q.available_at <= NOW())
          AND q.attempt_count < q.max_attempts
          AND (q.status = 'pending' OR NOT EXISTS (
              SELECT 1 FROM site_monitor_research_queue active
              WHERE active.id <> q.id AND active.page_key = q.page_key
                AND active.content_hash IS NOT DISTINCT FROM q.content_hash
                AND active.status IN ('pending', 'in_progress')))
        ORDER BY q.priority DESC, q.requested_at ASC LIMIT %s
        """
        logger.info("Fetching eligible research items limit=%s", limit)
        with psycopg.connect(self.dsn, autocommit=True, row_factory=dict_row) as conn:
            with conn.cursor() as cur:
                cur.execute(sql, [limit])
                items = [ResearchQueueItem.model_validate(row) for row in cur.fetchall()]
        logger.info("Fetched eligible research items count=%s", len(items))
        return items

    def claim_item(self, queue_id: int, now: datetime) -> ResearchQueueItem | None:
        """Claim one fresh row; uniqueness remains the final concurrent-insert guard."""
        sql = """
        WITH candidate AS (
            SELECT q.id FROM site_monitor_research_queue q
            WHERE q.id = %(queue_id)s AND q.status IN ('pending', 'failed')
              AND (q.available_at IS NULL OR q.available_at <= %(now)s)
              AND q.attempt_count < q.max_attempts
              AND NOT EXISTS (
                  SELECT 1 FROM site_monitor_research_queue active
                  WHERE active.id <> q.id AND active.page_key = q.page_key
                    AND active.content_hash IS NOT DISTINCT FROM q.content_hash
                    AND active.status IN ('pending', 'in_progress'))
            FOR UPDATE OF q SKIP LOCKED
        )
        UPDATE site_monitor_research_queue q
        SET status = 'in_progress', claimed_at = %(now)s,
            completed_at = NULL, attempt_count = q.attempt_count + 1
        FROM candidate WHERE q.id = candidate.id RETURNING q.*
        """
        logger.info("Claiming queue_id=%s", queue_id)
        try:
            with psycopg.connect(self.dsn, autocommit=True, row_factory=dict_row) as conn:
                with conn.cursor() as cur:
                    cur.execute(sql, {"queue_id": queue_id, "now": now})
                    row = cur.fetchone()
        except psycopg.errors.UniqueViolation as exc:
            if exc.diag.constraint_name != 'uq_site_monitor_research_queue_pending_unique':
                raise
            logger.info("Claim skipped queue_id=%s reason=equivalent_active_work_race", queue_id)
            return None
        if row is None:
            logger.info("Claim skipped queue_id=%s reason=locked_ineligible_or_active_duplicate", queue_id)
            return None
        item = ResearchQueueItem.model_validate(row)
        logger.info("Claimed queue_id=%s page_key=%s attempt=%s/%s",
                    item.id, item.page_key, item.attempt_count, item.max_attempts)
        return item

    def fail_item(self, *, item: ResearchQueueItem, now: datetime,
                  error_message: str, retry_delay_seconds: int = 900) -> bool:
        if retry_delay_seconds < 0:
            raise ValueError("retry_delay_seconds cannot be negative")
        sql = """
        UPDATE site_monitor_research_queue
        SET status = 'failed', completed_at = %(now)s,
            available_at = CASE WHEN attempt_count < max_attempts
                THEN %(now)s + (%(delay)s * INTERVAL '1 second') ELSE available_at END,
            last_error = %(error_message)s,
            errors = COALESCE(errors, '[]'::jsonb) || jsonb_build_array(
                jsonb_build_object('at', %(now)s::text, 'error', %(error_message)s::text))
        WHERE id = %(queue_id)s AND status = 'in_progress'
          AND claimed_at = %(claimed_at)s AND attempt_count = %(attempt_count)s
        """
        params = {"queue_id": item.id, "now": now, "delay": retry_delay_seconds,
                  "error_message": error_message, "claimed_at": item.claimed_at,
                  "attempt_count": item.attempt_count}
        with psycopg.connect(self.dsn, autocommit=True) as conn:
            with conn.cursor() as cur:
                cur.execute(sql, params)
                updated = cur.rowcount == 1
        if not updated:
            logger.warning("Failure not recorded: claim no longer owned queue_id=%s", item.id)
        else:
            logger.warning("Research failed queue_id=%s attempt=%s/%s retry_delay_seconds=%s",
                           item.id, item.attempt_count, item.max_attempts, retry_delay_seconds)
        return updated

    def complete_research(self, *, item: ResearchQueueItem,
                          result: PageAnalysisWrite, now: datetime) -> ResearchCompletion:
        """Commit state and queue completion together;
        never perform Slack I/O here."""

        logger.info("Beginning persistence queue_id=%s page_key=%s", item.id, item.page_key)
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
                    cur.execute("""SELECT page_key, content_hash, status, claimed_at, attempt_count
                        FROM site_monitor_research_queue WHERE id = %s FOR UPDATE""", [item.id])  # noqa: E501
                    row = cur.fetchone()
                    if row != (item.page_key,
                               item.content_hash,
                               'in_progress',
                               item.claimed_at,
                               item.attempt_count):
                        raise RuntimeError(f"Queue item {item.id} is missing, changed, or not claimed")  # noqa: E501
                    cur.execute(
                        "SELECT current_status FROM page_watch_current WHERE page_key = %s FOR UPDATE",
                        [item.page_key],
                    )
                    state_row = cur.fetchone()
                    if state_row is None:
                        raise RuntimeError(f"Missing state row for {item.page_key}; transaction rolled back")
                    previous_status = state_row[0]
                    metadata = item.payload.get("target_metadata", {})
                    missed_it = metadata.get("send_missed_it_message") if isinstance(metadata, dict) else None
                    if type(missed_it) is not bool:
                        logger.warning(
                            "Missing/invalid missed-it flag queue_id=%s; disabling missed-it notification",
                            item.id,
                        )
                        missed_it = False
                    completion = decide_initial_alert(
                        previous_status, result.result_page_status,
                        send_missed_it_message=missed_it,
                    )
                    # Queue history stores the application event, not the model's proposed label.
                    params["event_type"] = completion.event_type
                    cur.execute(state_sql, params)
                    if cur.rowcount != 1:
                        raise RuntimeError(f"Missing state row for {item.page_key}; transaction rolled back")  # noqa: E501
                    cur.execute(queue_sql, params)
                    if cur.rowcount != 1:
                        raise RuntimeError(f"Queue completion failed for {item.id}; transaction rolled back")  # noqa: E501
        logger.info("Research committed queue_id=%s page_key=%s status=%s",
                    item.id, item.page_key, result.result_page_status)

        logger.info(
            "Initial-alert decision queue_id=%s previous=%s current=%s state_changed=%s "
            "should_alert=%s event=%s suppression_reason=%s",
            item.id, completion.previous_status, completion.current_status,
            completion.state_changed, completion.should_alert, completion.event_type,
            completion.suppression_reason,
        )
        return completion
