# (C) Markham Lee 2023 - 2026
# https://github.com/MarkhamLee/internet-and-iot-data-platform
# PostgreSQL repository for the site monitor research queue
from __future__ import annotations

import os
import psycopg
import sys
from datetime import datetime
from psycopg.rows import dict_row
from schemas import ResearchQueueItem


parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from agent_library.logging_util import console_logging  # noqa: E402

logger = console_logging("postgres_queue_repository")


class PostgresQueueRepository:

    def __init__(self, dsn: str) -> None:
        self.dsn = dsn
        self.conn: psycopg.Connection | None = None

    # ------------------------------------------------------------------
    # Context manager — used when a live conn is needed (e.g. instrumentation)
    # ------------------------------------------------------------------

    def connect(self) -> None:
        if self.conn is None or self.conn.closed:
            self.conn = psycopg.connect(self.dsn, autocommit=True)
            with self.conn.cursor() as cur:
                cur.execute(
                    "SELECT current_database(), current_user, current_schema()"
                )
                db_name, db_user, db_schema = cur.fetchone()
                logger.info(
                    "Postgres connection established database=%s user=%s schema=%s",  # noqa: E501
                    db_name,
                    db_user,
                    db_schema,
                )

    def close(self) -> None:
        if self.conn is not None and not self.conn.closed:
            logger.info("Closing Postgres connection")
            self.conn.close()

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()

    # ------------------------------------------------------------------
    # Queue reads
    # ------------------------------------------------------------------

    def fetch_pending_items(self, limit: int = 10) -> list[ResearchQueueItem]:
        sql = """
            SELECT *
            FROM site_monitor_research_queue
            WHERE status = 'pending' or status = 'failed"
              AND (available_at IS NULL OR available_at <= NOW())
              AND attempt_count < max_attempts
            ORDER BY priority DESC, requested_at ASC
            LIMIT %s
        """

        logger.info("Fetching pending research queue items limit=%s", limit)

        with psycopg.connect(self.dsn, autocommit=True,
                             row_factory=dict_row) as conn:
            with conn.cursor() as cur:
                cur.execute(sql, [limit])
                rows = cur.fetchall()

        logger.info("Fetched %s pending item(s)", len(rows))
        return [ResearchQueueItem.model_validate(row) for row in rows]

    # ------------------------------------------------------------------
    # Queue writes
    # ------------------------------------------------------------------

    def claim_item(self, queue_id: int, now: datetime) -> None:
        sql = """
            UPDATE site_monitor_research_queue
            SET status        = 'in_progress',
                claimed_at    = %(now)s,
                attempt_count = attempt_count + 1
            WHERE id = %(queue_id)s
        """
        with psycopg.connect(self.dsn, autocommit=True) as conn:
            with conn.cursor() as cur:
                cur.execute(sql, {"queue_id": queue_id, "now": now})

        logger.info("Claimed research queue item queue_id=%s", queue_id)

    def complete_item(
        self,
        *,
        queue_id: int,
        now: datetime,
        result_page_status: str,
        result_event_type: str | None,
    ) -> None:
        sql = """
            UPDATE site_monitor_research_queue
            SET status             = 'completed',
                completed_at       = %(now)s,
                result_reviewed_at = %(now)s,
                result_page_status = %(result_page_status)s,
                result_event_type  = %(result_event_type)s
            WHERE id = %(queue_id)s
        """
        with psycopg.connect(self.dsn, autocommit=True) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    sql,
                    {
                        "queue_id": queue_id,
                        "now": now,
                        "result_page_status": result_page_status,
                        "result_event_type": result_event_type,
                    },
                )

        logger.info(
            "Completed research queue item queue_id=%s status=%s",
            queue_id,
            result_page_status,
        )

    def fail_item(
        self,
        *,
        queue_id: int,
        now: datetime,
        error_message: str,
    ) -> None:
        sql = """
            UPDATE site_monitor_research_queue
            SET status       = 'failed',
                completed_at = %(now)s,
                last_error   = %(error_message)s,
                errors       = COALESCE(errors, '[]'::jsonb)
                            || jsonb_build_array(
                                jsonb_build_object(
                                    'at',    %(now)s::text,
                                    'error', %(error_message)s::text
                                )
                            )
            WHERE id = %(queue_id)s
        """
        with psycopg.connect(self.dsn, autocommit=True) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    sql,
                    {
                        "queue_id": queue_id,
                        "now": now,
                        "error_message": error_message,
                    },
                )

        logger.info("Marked research queue item failed queue_id=%s", queue_id)
