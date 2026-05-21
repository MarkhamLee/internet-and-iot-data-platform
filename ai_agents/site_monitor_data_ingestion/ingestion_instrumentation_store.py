from __future__ import annotations

import psycopg
from datetime import datetime
from psycopg.types.json import Jsonb
from typing import Any


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
            pipeline_name,
            started_at,
            target_count,
            enabled_target_count,
            metadata
        )
        values (%s, %s, %s, %s, %s)
        returning id
        """
        with psycopg.connect(self.dsn, autocommit=True) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    sql,
                    (
                        pipeline_name,
                        started_at,
                        target_count,
                        enabled_target_count,
                        Jsonb(metadata or {}),
                    ),
                )
                result = cur.fetchone()
                if result is None:
                    raise RuntimeError("create_run() did not return an id")
                return int(result[0])

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
            metadata = coalesce(metadata, '{}'::jsonb) || %s
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
                        Jsonb(metadata or {}),
                        run_id,
                    ),
                )

    def append_run_error(
        self,
        *,
        run_id: int,
        stage: str,
        message: str,
        exception_type: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        entry = {
            "stage": stage,
            "message": message,
            "exception_type": exception_type,
            "details": details or {},
        }
        sql = """
        update site_monitor_ingestion_runs
        set
            error_count = error_count + 1,
            errors = errors || jsonb_build_array(
                %s || jsonb_build_object('recorded_at', now())
            )
        where id = %s
        """
        with psycopg.connect(self.dsn, autocommit=True) as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (Jsonb(entry), run_id))

    def append_run_warning(
        self,
        *,
        run_id: int,
        stage: str,
        message: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        entry = {
            "stage": stage,
            "message": message,
            "details": details or {},
        }
        sql = """
        update site_monitor_ingestion_runs
        set
            warning_count = warning_count + 1,
            warnings = warnings || jsonb_build_array(
                %s || jsonb_build_object('recorded_at', now())
            )
        where id = %s
        """
        with psycopg.connect(self.dsn, autocommit=True) as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (Jsonb(entry), run_id))

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
                cur.execute(sql, (run_id,
                                  page_key,
                                  url,
                                  started_at,
                                  Jsonb(metadata or {})))
                result = cur.fetchone()
                if result is None:
                    raise RuntimeError("create_target_run() did not return an id")  # noqa: E501
                return int(result[0])

    def update_target_run(self, *, target_run_id: int, **fields: Any) -> None:
        if not fields:
            return
        assignments = []
        values: list[Any] = []
        jsonb_fields = {"metadata"}
        for key, value in fields.items():
            assignments.append(f"{key} = %s")
            if key in jsonb_fields:
                values.append(Jsonb(value or {}))
            else:
                values.append(value)
        values.append(target_run_id)
        sql = f"update site_monitor_ingestion_target_runs set {', '.join(assignments)} where id = %s"  # noqa: E501
        with psycopg.connect(self.dsn, autocommit=True) as conn:
            with conn.cursor() as cur:
                cur.execute(sql, values)

    def mark_target_stage(self,
                          *,
                          target_run_id: int,
                          stage: str,
                          details: dict[str, Any] | None = None) -> None:
        stage_metadata = {
            "last_stage": stage,
            "last_stage_details": details or {},
        }
        sql = """
        update site_monitor_ingestion_target_runs
        set
            metadata = coalesce(metadata, '{}'::jsonb)
                || %s
                || jsonb_build_object('last_stage_recorded_at', now())
        where id = %s
        """
        with psycopg.connect(self.dsn, autocommit=True) as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (Jsonb(stage_metadata), target_run_id))

    def append_target_error(
        self,
        *,
        target_run_id: int,
        stage: str,
        message: str,
        exception_type: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        entry = {
            "stage": stage,
            "message": message,
            "exception_type": exception_type,
            "details": details or {},
        }
        sql = """
        update site_monitor_ingestion_target_runs
        set
            error_count = error_count + 1,
            errors = errors || jsonb_build_array(
                %s || jsonb_build_object('recorded_at', now())
            )
        where id = %s
        """
        with psycopg.connect(self.dsn, autocommit=True) as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (Jsonb(entry), target_run_id))

    def append_target_warning(
        self,
        *,
        target_run_id: int,
        stage: str,
        message: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        entry = {
            "stage": stage,
            "message": message,
            "details": details or {},
        }
        sql = """
        update site_monitor_ingestion_target_runs
        set
            warning_count = warning_count + 1,
            warnings = warnings || jsonb_build_array(
                %s || jsonb_build_object('recorded_at', now())
            )
        where id = %s
        """
        with psycopg.connect(self.dsn, autocommit=True) as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (Jsonb(entry), target_run_id))

    def finalize_target_run(
        self,
        *,
        target_run_id: int,
        completed_at: datetime,
        duration_seconds: float,
        status: str,
        queued_for_research: bool | None = None,
        reminder_attempted: bool | None = None,
        reminder_sent: bool | None = None,
        queue_id: int | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        assignments = [
            "completed_at = %s",
            "duration_seconds = %s",
            "status = %s",
        ]
        values: list[Any] = [completed_at, round(duration_seconds, 2), status]

        if queued_for_research is not None:
            assignments.append("queued_for_research = %s")
            values.append(queued_for_research)
        if reminder_attempted is not None:
            assignments.append("reminder_attempted = %s")
            values.append(reminder_attempted)
        if reminder_sent is not None:
            assignments.append("reminder_sent = %s")
            values.append(reminder_sent)
        if queue_id is not None:
            assignments.append("queue_id = %s")
            values.append(queue_id)
        if metadata is not None:
            assignments.append("metadata = coalesce(metadata, '{}'::jsonb) || %s")  # noqa: E501
            values.append(Jsonb(metadata))

        values.append(target_run_id)
        sql = f"update site_monitor_ingestion_target_runs set {', '.join(assignments)} where id = %s"  # noqa: E501
        with psycopg.connect(self.dsn, autocommit=True) as conn:
            with conn.cursor() as cur:
                cur.execute(sql, values)
