# (C) Markham Lee 2023 - 2026
# https://github.com/MarkhamLee/internet-and-iot-data-platform
# Entrypoint for the data ingestion side of the
# the site monitoring agent
from __future__ import annotations

import os
import sys
from datetime import UTC, datetime
from time import perf_counter

from config import AppConfig, WatchTarget, load_config
from content_extractor import extract_review_payload
from hash_helper import compute_content_hash
from instrumentation_store import InstrumentationStore
from page_fetcher import fetch_page
from reminder_service import build_reminder_payload, \
    send_reminder, should_send_reminder
from research_queue_store import ResearchQueueStore
from state_store import (
    StateStore,
    build_research_queue_payload,
    should_enqueue_research,
)

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from agent_library.logging_util import console_logging  # noqa: E402

logger = console_logging("site_monitor_data_ingestion_logs")


def process_target(
    *,
    app: AppConfig,
    target: WatchTarget,
    state_store: StateStore,
    queue_store: ResearchQueueStore,
    instrumentation_store: InstrumentationStore,
    run_id: int,
) -> str:
    target_start = perf_counter()
    now = datetime.now(UTC)
    target_run_id = instrumentation_store.create_target_run(
        run_id=run_id,
        page_key=target.page_key,
        url=str(target.url),
        started_at=now,
        metadata={"pipeline": "site_monitor_data_ingestion"},
    )

    try:
        if not target.enabled:
            instrumentation_store.finalize_target_run(
                target_run_id=target_run_id,
                completed_at=datetime.now(UTC),
                duration_seconds=perf_counter() - target_start,
                status="skipped_disabled",
            )
            return "skipped"

        instrumentation_store.mark_target_stage(
            target_run_id=target_run_id,
            stage="previous_state_loaded",
        )
        previous = state_store.get_current_state(target.page_key)

        instrumentation_store.mark_target_stage(
            target_run_id=target_run_id,
            stage="fetch_started",
        )
        fetch_result = fetch_page(
            str(target.url),
            etag=previous.last_http_etag if previous else None,
            last_modified=previous.
            last_http_last_modified if previous else None,
        )

        instrumentation_store.update_target_run(
            target_run_id=target_run_id,
            http_status_code=fetch_result.status_code,
            final_url=fetch_result.final_url,
            http_etag=fetch_result.etag,
            http_last_modified=fetch_result.last_modified,
        )
        instrumentation_store.mark_target_stage(
            target_run_id=target_run_id,
            stage="fetch_completed",
            details={"status_code": fetch_result.status_code},
        )

        if fetch_result.status_code == 304 and previous is not None:
            state_store.record_collection_check(
                page_key=target.page_key,
                url=str(target.url),
                now=now,
                http_etag=fetch_result.etag,
                http_last_modified=fetch_result.last_modified,
                content_hash=previous.last_content_hash,
                final_url=fetch_result.final_url,
            )

            reminder_due, reminder_reason = should_send_reminder(previous,
                                                                 target,
                                                                 now)
            if reminder_due:
                status_code = send_reminder(
                    app.slack_webhook_url,
                    build_reminder_payload(
                        page_key=target.page_key,
                        url=str(target.url),
                        now=now,
                    ),
                )
                if status_code == 200:
                    state_store.record_reminder_sent(page_key=target.page_key,
                                                     sent_at=now)
                    instrumentation_store.finalize_target_run(
                        target_run_id=target_run_id,
                        completed_at=datetime.now(UTC),
                        duration_seconds=perf_counter() - target_start,
                        status="completed",
                        slack_sent=True,
                        metadata={"reminder_reason": reminder_reason},
                    )
                    return "reminder_sent"

            instrumentation_store.finalize_target_run(
                target_run_id=target_run_id,
                completed_at=datetime.now(UTC),
                duration_seconds=perf_counter() - target_start,
                status="completed",
                metadata={"reason": "not_modified"},
            )
            return "unchanged"

        review_payload = extract_review_payload(fetch_result, target)
        instrumentation_store.mark_target_stage(
            target_run_id=target_run_id,
            stage="payload_extracted",
        )
        content_hash = compute_content_hash(review_payload)
        instrumentation_store.update_target_run(
            target_run_id=target_run_id,
            content_hash=content_hash,
        )
        instrumentation_store.mark_target_stage(
            target_run_id=target_run_id,
            stage="content_hashed",
        )

        state_store.record_collection_check(
            page_key=target.page_key,
            url=str(target.url),
            now=now,
            http_etag=fetch_result.etag,
            http_last_modified=fetch_result.last_modified,
            content_hash=content_hash,
            final_url=fetch_result.final_url,
        )

        should_queue, request_reason = should_enqueue_research(
            previous=previous,
            content_hash=content_hash,
            now=now,
            force_research_after_hours=app.force_research_after_hours,
        )

        reminder_due = False
        reminder_reason = None
        if not should_queue and previous is not None:
            reminder_due, reminder_reason = should_send_reminder(previous,
                                                                 target,
                                                                 now)

        if should_queue:
            pending_reconfirmation = bool(
                previous is not None and previous.current_status == "desired"
            )
            queue_payload = build_research_queue_payload(
                target=target,
                review_payload=review_payload,
                content_hash=content_hash,
                request_reason=request_reason,
                previous=previous,
                pending_reconfirmation=pending_reconfirmation,
            )
            queue_id = queue_store.enqueue_research(
                page_key=target.page_key,
                url=str(target.url),
                request_reason=request_reason,
                content_hash=content_hash,
                final_url=fetch_result.final_url,
                http_etag=fetch_result.etag,
                http_last_modified=fetch_result.last_modified,
                pending_reconfirmation=pending_reconfirmation,
                payload=queue_payload,
            )
            state_store.mark_research_pending(
                page_key=target.page_key,
                url=str(target.url),
                now=now,
                content_hash=content_hash,
                queue_id=queue_id,
                pending_reconfirmation=pending_reconfirmation,
                final_url=fetch_result.final_url,
                http_etag=fetch_result.etag,
                http_last_modified=fetch_result.last_modified,
            )
            instrumentation_store.finalize_target_run(
                target_run_id=target_run_id,
                completed_at=datetime.now(UTC),
                duration_seconds=perf_counter() - target_start,
                status="completed",
                metadata={
                    "request_reason": request_reason,
                    "queued_for_research": True,
                    "queue_id": queue_id,
                },
            )
            return "queued"

        if reminder_due:
            status_code = send_reminder(
                app.slack_webhook_url,
                build_reminder_payload(
                    page_key=target.page_key,
                    url=str(target.url),
                    now=now,
                ),
            )
            if status_code == 200:
                state_store.record_reminder_sent(page_key=target.page_key,
                                                 sent_at=now)
                instrumentation_store.finalize_target_run(
                    target_run_id=target_run_id,
                    completed_at=datetime.now(UTC),
                    duration_seconds=perf_counter() - target_start,
                    status="completed",
                    slack_sent=True,
                    metadata={"reminder_reason": reminder_reason},
                )
                return "reminder_sent"

        instrumentation_store.finalize_target_run(
            target_run_id=target_run_id,
            completed_at=datetime.now(UTC),
            duration_seconds=perf_counter() - target_start,
            status="completed",
            metadata={"request_reason": request_reason},
        )
        return "unchanged"

    except Exception as exc:
        instrumentation_store.append_target_error(
            target_run_id=target_run_id,
            stage="process_target",
            message=str(exc),
            exception_type=type(exc).__name__,
            details={"page_key": target.page_key, "url": str(target.url)},
        )
        instrumentation_store.finalize_target_run(
            target_run_id=target_run_id,
            completed_at=datetime.now(UTC),
            duration_seconds=perf_counter() - target_start,
            status="failed",
        )
        logger.exception("Collection processing failed page_key=%s", target.page_key)  # noqa: E501
        return "failed"


def main() -> None:
    app = load_config()
    state_store = StateStore(app.postgres_dsn)
    queue_store = ResearchQueueStore(app.postgres_dsn)
    instrumentation_store = InstrumentationStore(app.postgres_dsn)

    started_at = datetime.now(UTC)
    enabled_target_count = sum(1 for target in app.targets if target.enabled)
    run_id = instrumentation_store.create_run(
        pipeline_name="site_monitor_data_ingestion",
        started_at=started_at,
        target_count=len(app.targets),
        enabled_target_count=enabled_target_count,
        metadata={"force_research_after_hours": app.force_research_after_hours},  # noqa: E501
    )

    overall_start = perf_counter()
    logger.info(
        "Starting site monitor data ingestion count=%s",
        len(app.targets),
    )

    succeeded = 0
    failed = 0
    skipped = 0
    queued = 0
    reminder_sent = 0
    unchanged = 0

    for target in app.targets:
        result = process_target(
            app=app,
            target=target,
            state_store=state_store,
            queue_store=queue_store,
            instrumentation_store=instrumentation_store,
            run_id=run_id,
        )
        if result == "failed":
            failed += 1
        elif result == "skipped":
            skipped += 1
        else:
            succeeded += 1
            if result == "queued":
                queued += 1
            elif result == "reminder_sent":
                reminder_sent += 1
            elif result == "unchanged":
                unchanged += 1

    duration_seconds = perf_counter() - overall_start
    run_status = "completed_with_errors" if failed else "completed"
    instrumentation_store.finalize_run(
        run_id=run_id,
        completed_at=datetime.now(UTC),
        duration_seconds=duration_seconds,
        status=run_status,
        succeeded_target_count=succeeded,
        failed_target_count=failed,
        skipped_target_count=skipped,
        error_count=failed,
        warning_count=0,
        metadata={
            "queued_target_count": queued,
            "reminder_sent_count": reminder_sent,
            "unchanged_target_count": unchanged,
        },
    )
    logger.info(
        "Site monitor ingestion completed duration_seconds=%s queued=%s reminder_sent=%s unchanged=%s failed=%s",  # noqa: E501
        round(duration_seconds, 2),
        queued,
        reminder_sent,
        unchanged,
        failed,
    )


if __name__ == "__main__":
    main()
