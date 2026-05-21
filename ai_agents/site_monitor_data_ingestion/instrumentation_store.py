# (C) Markham Lee 2023 - 2026
# https://github.com/MarkhamLee/internet-and-iot-data-platform
# writes instrumentation data to the Postgres DB.
from __future__ import annotations

import psycopg
from datetime import UTC, datetime
import psycopg.types.json
from typing import Any


class InstrumentationStore:
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
        insert into site_monitor_runs (
            started_at,
            agent_name,
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
        error_count: int,
        warning_count: int,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        sql = """
        update site_monitor_runs
        set
            completed_at = %s,
            duration_seconds = %s,
            status = %s,
            succeeded_target_count = %s,
            failed_target_count = %s,
            skipped_target_count = %s,
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
        insert into site_monitor_target_runs (
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
        update site_monitor_target_runs
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
        review_reason: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        sql = """
        update site_monitor_target_runs
        set
            status = coalesce(%s, status),
            http_status_code = coalesce(%s, http_status_code),
            final_url = coalesce(%s, final_url),
            http_etag = coalesce(%s, http_etag),
            http_last_modified = coalesce(%s, http_last_modified),
            content_hash = coalesce(%s, content_hash),
            review_reason = coalesce(%s, review_reason),
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
                        review_reason,
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
        update site_monitor_target_runs
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
        slack_sent: bool = False,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        sql = """
        update site_monitor_target_runs
        set
            completed_at = %s,
            duration_seconds = %s,
            status = %s,
            slack_sent = %s,
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
                        slack_sent,
                        psycopg.types.json.Json(metadata or {}),
                        target_run_id,
                    ),
                )
