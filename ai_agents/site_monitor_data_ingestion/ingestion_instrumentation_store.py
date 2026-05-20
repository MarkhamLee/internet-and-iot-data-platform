from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import psycopg
import psycopg.types.json


class IngestionInstrumentationStore:
    def __init__(self, dsn: str):
        self.dsn = dsn

    def create_run(
        self,
        *,
        pipeline_name: str,
        started_at: datetime,
        target_count: int,
        enabled_target_count: int,
        metadata: dict[str, Any] | None = None,
    ) -> int:
        sql = """
        insert into site_monitor_ingestion_runs (
            started_at,
            pipeline_name,
            target_count,
            enabled_target_count,
            status,
            metadata
        )
        values (%s, %s, %s, %s, 'running', %s)
        returning id
        """

        with psycopg.connect(self.dsn, autocommit=True) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    sql,
                    (
                        started_at,
                        pipeline_name,
                        target_count,
                        enabled_target_count,
                        psycopg.types.json.Json(metadata or {}),
                    ),
                )
                row = cur.fetchone()
                return int(row[0])

    def finalize_run(
        self,
        *,
        run_id: int,
        completed_at: datetime,
        duration_seconds: float,
        status: str,
        succeeded_target_count: int,
        failed_target_count: int,
        skipped_target_count: int,
        queued_target_count: int,
        reminder_sent_count: int,
        unchanged_target_count: int,
        error_count: int,
        warning_count: int,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        sql = """
        update site_monitor_ingestion_runs
        set
            completed_at = %s,
            duration_seconds = %s,
            status = %s,
            succeeded_target_count = %s,
            failed_target_count = %s,
            skipped_target_count = %s,
            queued_target_count = %s,
            reminder_sent_count = %s,
            unchanged_target_count = %s,
            error_count = %s,
            warning_count = %s,
            metadata = coalesce(metadata, '{}'::jsonb) || %s::jsonb
        where id = %s
        """

        with psycopg.connect(self.dsn, autocommit=True) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    sql,
                    (
                        completed_at,
                        round(duration_seconds, 2),
                        status,
                        succeeded_target_count,
                        failed_target_count,
                        skipped_target_count,
                        queued_target_count,
                        reminder_sent_count,
                        unchanged_target_count,
                        error_count,
                        warning_count,
                        psycopg.types.json.Json(metadata or {}),
                        run_id,
                    ),
                )

    def create_target_run(
        self,
        *,
        run_id: int,
        page_key: str,
        url: str,
        started_at: datetime,
        metadata: dict[str, Any] | None = None,
    ) -> int:
        sql = """
        insert into site_monitor_ingestion_target_runs (
            run_id,
            page_key,
            url,
            started_at,
            status,
            metadata
        )
        values (%s, %s, %s, %s, 'running', %s)
        returning id
        """

        with psycopg.connect(self.dsn, autocommit=True) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    sql,
                    (
                        run_id,
                        page_key,
                        url,
                        started_at,
                        psycopg.types.json.Json(metadata or {}),
                    ),
                )
                row = cur.fetchone()
                return int(row[0])

    def mark_target_stage(
        self,
        *,
        target_run_id: int,
        stage: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        sql = """
        update site_monitor_ingestion_target_runs
        set metadata = coalesce(metadata, '{}'::jsonb) || %s::jsonb
        where id = %s
        """
        payload = {
            "last_stage": stage,
            "last_stage_at": datetime.now(UTC).isoformat(),
            "last_stage_details": details or {},
        }

        with psycopg.connect(self.dsn, autocommit=True) as conn:
            with conn.cursor() as cur:
                cur.execute(sql,
                            (psycopg.types.json.Json(payload),
                             target_run_id))

    def update_target_run(
        self,
        *,
        target_run_id: int,
        status: str | None = None,
        http_status_code: int | None = None,
        final_url: str | None = None,
        http_etag: str | None = None,
        http_last_modified: str | None = None,
        content_hash: str | None = None,
        request_reason: str | None = None,
        queued_for_research: bool | None = None,
        reminder_attempted: bool | None = None,
        reminder_sent: bool | None = None,
        queue_id: int | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        sql = """
        update site_monitor_ingestion_target_runs
        set
            status = coalesce(%s, status),
            http_status_code = coalesce(%s, http_status_code),
            final_url = coalesce(%s, final_url),
            http_etag = coalesce(%s, http_etag),
            http_last_modified = coalesce(%s, http_last_modified),
            content_hash = coalesce(%s, content_hash),
            request_reason = coalesce(%s, request_reason),
            queued_for_research = coalesce(%s, queued_for_research),
            reminder_attempted = coalesce(%s, reminder_attempted),
            reminder_sent = coalesce(%s, reminder_sent),
            queue_id = coalesce(%s, queue_id),
            metadata = coalesce(metadata, '{}'::jsonb) || %s::jsonb
        where id = %s
        """

        with psycopg.connect(self.dsn, autocommit=True) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    sql,
                    (
                        status,
                        http_status_code,
                        final_url,
                        http_etag,
                        http_last_modified,
                        content_hash,
                        request_reason,
                        queued_for_research,
                        reminder_attempted,
                        reminder_sent,
                        queue_id,
                        psycopg.types.json.Json(metadata or {}),
                        target_run_id,
                    ),
                )

    def append_target_error(
        self,
        *,
        target_run_id: int,
        stage: str,
        message: str,
        exception_type: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        sql = """
        update site_monitor_ingestion_target_runs
        set
            error_count = error_count + 1,
            errors = coalesce(errors, '[]'::jsonb) || jsonb_build_array(
                jsonb_build_object(
                    'stage', %s,
                    'message', %s,
                    'exception_type', %s,
                    'details', %s::jsonb,
                    'recorded_at', %s
                )
            )
        where id = %s
        """

        with psycopg.connect(self.dsn, autocommit=True) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    sql,
                    (
                        stage,
                        message,
                        exception_type,
                        psycopg.types.json.Json(details or {}),
                        datetime.now(UTC).isoformat(),
                        target_run_id,
                    ),
                )

    def finalize_target_run(
        self,
        *,
        target_run_id: int,
        completed_at: datetime,
        duration_seconds: float,
        status: str,
        queued_for_research: bool = False,
        reminder_attempted: bool = False,
        reminder_sent: bool = False,
        queue_id: int | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        sql = """
        update site_monitor_ingestion_target_runs
        set
            completed_at = %s,
            duration_seconds = %s,
            status = %s,
            queued_for_research = %s,
            reminder_attempted = %s,
            reminder_sent = %s,
            queue_id = coalesce(%s, queue_id),
            metadata = coalesce(metadata, '{}'::jsonb) || %s::jsonb
        where id = %s
        """

        with psycopg.connect(self.dsn, autocommit=True) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    sql,
                    (
                        completed_at,
                        round(duration_seconds, 2),
                        status,
                        queued_for_research,
                        reminder_attempted,
                        reminder_sent,
                        queue_id,
                        psycopg.types.json.Json(metadata or {}),
                        target_run_id,
                    ),
                )
