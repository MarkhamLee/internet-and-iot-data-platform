# (C) Markham Lee 2023 - 2026
# https://github.com/MarkhamLee/internet-and-iot-data-platform
# Reminder pipeline for the site monitor agent.
from __future__ import annotations

import os
import sys
import psycopg
from dataclasses import dataclass
from datetime import datetime, timedelta
from psycopg.rows import dict_row
from reminder_slack_messaging import build_reminder_blocks

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from agent_library.logging_util import console_logging  # noqa: E402
from agent_library.\
    agent_utilities import send_slack_webhook_block  # noqa: E402
from site_monitor_data_ingestion.\
    config import AppConfig, WatchTarget  # noqa: E402
from site_monitor_data_ingestion.schemas import TrackedPageState  # noqa: E402

logger = console_logging("reminder_pipeline_logs")


@dataclass(slots=True)
class ReminderRunCounters:
    processed: int = 0
    sent: int = 0
    skipped: int = 0
    failed: int = 0


def fetch_desired_targets(dsn: str) -> list[TrackedPageState]:
    sql = """
        SELECT
            page_key, url, current_status, first_seen_at, last_checked_at,
            state_changed_at, desired_state_started_at,
            undesired_state_started_at, last_reminder_sent_at,
            last_slack_message_type, last_review_summary, last_state_key,
            last_http_etag, last_http_last_modified, last_content_hash,
            last_llm_reviewed_hash, research_needed, research_requested_at,
            pending_reconfirmation, pending_content_hash, pending_final_url,
            pending_http_etag, pending_http_last_modified,
            last_research_completed_at, last_research_queue_id,
            reminder_count
        FROM page_watch_current
        WHERE current_status = 'desired'
    """
    with psycopg.connect(dsn, autocommit=True, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
            rows = cur.fetchall()

    logger.info("Found %s target(s) in desired state", len(rows))
    return [TrackedPageState(**row) for row in rows]


def should_send_reminder(previous, target, now: datetime) -> tuple[bool, str]:
    if previous is None:
        return False, "no_previous_state"

    if previous.current_status != "desired":
        return False, "current_status_not_desired"

    if getattr(previous, "pending_reconfirmation", False):
        return False, "pending_reconfirmation"

    if previous.last_reminder_sent_at is None:
        return True, "first_reminder"

    if now - previous.\
            last_reminder_sent_at >= timedelta(minutes=target.
                                               reminder_interval_minutes):
        return True, "reminder_interval_elapsed"

    return False, "reminder_not_due"


def record_reminder_sent(
    dsn: str,
    *,
    page_key: str,
    sent_at: datetime,
) -> None:
    sql = """
        UPDATE page_watch_current
        SET last_reminder_sent_at = %(sent_at)s,
            last_slack_message_type = 'desired_reminder',
            reminder_count = reminder_count + 1
        WHERE page_key = %(page_key)s
    """
    with psycopg.connect(dsn, autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute(sql, {"sent_at": sent_at, "page_key": page_key})

    logger.info(
        "Recorded reminder sent page_key=%s sent_at=%s", page_key, sent_at
    )


def max_reminders_reached(
    previous: TrackedPageState,
    target: WatchTarget,
) -> bool:
    if target.max_reminders is None:
        return False
    reminder_count = getattr(previous, "reminder_count", 0) or 0
    return reminder_count >= target.max_reminders


def process_reminder(
    *,
    app: AppConfig,
    target: WatchTarget,
    previous: TrackedPageState,
    now: datetime,
) -> str:
    if max_reminders_reached(previous, target):
        logger.info(
            "Max reminders reached page_key=%s count=%s limit=%s",
            target.page_key,
            getattr(previous, "reminder_count", 0),
            target.max_reminders,
        )
        return "skipped"

    reminder_due, reason = should_send_reminder(previous, target, now)

    if not reminder_due:
        logger.info(
            "No reminder due page_key=%s reason=%s", target.page_key, reason
        )
        return "skipped"

    logger.info(
        "Sending reminder page_key=%s reason=%s", target.page_key, reason
    )

    reminder_count = (getattr(previous, "reminder_count", 0) or 0) + 1

    slack_payload = build_reminder_blocks(
        page_key=target.page_key,
        url=str(target.url),
        now=now,
        reminder_count=reminder_count,
        last_review_summary=previous.last_review_summary,
    )

    try:
        status_code = send_slack_webhook_block(
            app.slack_webhook_url, slack_payload
        )
    except Exception:
        logger.exception(
            "Reminder send raised exception page_key=%s", target.page_key
        )
        return "failed"

    if status_code == 200:
        record_reminder_sent(
            app.postgres_dsn,
            page_key=target.page_key,
            sent_at=now,
        )
        logger.info(
            "Reminder sent successfully page_key=%s reminder_count=%s",
            target.page_key,
            reminder_count,
        )
        return "sent"

    logger.warning(
        "Reminder send failed page_key=%s status_code=%s",
        target.page_key,
        status_code,
    )
    return "failed"


def run_reminder_cycle(
    *,
    app: AppConfig,
    started_at: datetime,
) -> None:
    now = started_at
    counters = ReminderRunCounters()

    target_map: dict[str, WatchTarget] = {
        t.page_key: t for t in app.targets if t.enabled
    }

    desired_pages = fetch_desired_targets(app.postgres_dsn)

    if not desired_pages:
        logger.info("No targets currently in desired state, nothing to do")
        return

    for page_state in desired_pages:
        target = target_map.get(page_state.page_key)

        if target is None:
            logger.warning(
                "page_key=%s in desired state but not in config, skipping",
                page_state.page_key,
            )
            counters.skipped += 1
            continue

        counters.processed += 1
        result = process_reminder(
            app=app,
            target=target,
            previous=page_state,
            now=now,
        )

        if result == "sent":
            counters.sent += 1
        elif result == "skipped":
            counters.skipped += 1
        elif result == "failed":
            counters.failed += 1

    logger.info(
        "Reminder cycle complete processed=%s sent=%s skipped=%s failed=%s",
        counters.processed,
        counters.sent,
        counters.skipped,
        counters.failed,
    )
