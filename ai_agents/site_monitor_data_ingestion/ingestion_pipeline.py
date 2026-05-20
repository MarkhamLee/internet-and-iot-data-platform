# (C) Markham Lee 2023 - 2026
# https://github.com/MarkhamLee/internet-and-iot-data-platform
# Primary pipeline script for ingesting page data, computing hashes
# alerting, etc. rom __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from time import perf_counter
from typing import Any

from config import AppConfig, WatchTarget
from content_extractor import extract_review_payload
from hash_helper import compute_content_hash
from page_fetcher import fetch_page
from reminder_service import build_reminder_payload, \
    send_reminder, should_send_reminder
from state_store import StateStore, \
    build_research_queue_payload, should_enqueue_research
from research_queue_store import ResearchQueueStore
from ingestion_instrumentation_store import IngestionInstrumentationStore


@dataclass(slots=True)
class IngestionDependencies:
    state_store: StateStore
    queue_store: ResearchQueueStore
    instrumentation_store: IngestionInstrumentationStore
    logger: Any


@dataclass(slots=True)
class IngestionRunCounters:
    succeeded: int = 0
    failed: int = 0
    skipped: int = 0
    queued: int = 0
    reminder_sent: int = 0
    unchanged: int = 0


def process_target(
    *,
    app: AppConfig,
    target: WatchTarget,
    deps: IngestionDependencies,
    run_id: int,
) -> str:
    target_start = perf_counter()
    now = datetime.now(UTC)
    target_run_id = deps.instrumentation_store.create_target_run(
        run_id=run_id,
        page_key=target.page_key,
        url=str(target.url),
        started_at=now,
        metadata={"pipeline": "site_monitor_data_ingestion"},
    )

    try:
        if not target.enabled:
            deps.instrumentation_store.finalize_target_run(
                target_run_id=target_run_id,
                completed_at=datetime.now(UTC),
                duration_seconds=perf_counter() - target_start,
                status="skipped_disabled",
            )
            return "skipped"

        previous = deps.state_store.get_current_state(target.page_key)
        deps.instrumentation_store.mark_target_stage(
            target_run_id=target_run_id,
            stage="previous_state_loaded",
        )

        fetch_result = fetch_page(
            str(target.url),
            etag=previous.last_http_etag if previous else None,
            last_modified=previous.
            last_http_last_modified if previous else None,
        )
        deps.instrumentation_store.update_target_run(
            target_run_id=target_run_id,
            http_status_code=fetch_result.status_code,
            final_url=fetch_result.final_url,
            http_etag=fetch_result.etag,
            http_last_modified=fetch_result.last_modified,
        )
        deps.instrumentation_store.mark_target_stage(
            target_run_id=target_run_id,
            stage="fetch_completed",
            details={"status_code": fetch_result.status_code},
        )

        if fetch_result.status_code == 304 and previous is not None:
            deps.state_store.record_collection_check(
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
                    deps.state_store.record_reminder_sent(
                        page_key=target.page_key,
                        sent_at=now,
                    )
                    deps.instrumentation_store.finalize_target_run(
                        target_run_id=target_run_id,
                        completed_at=datetime.now(UTC),
                        duration_seconds=perf_counter() - target_start,
                        status="completed",
                        reminder_attempted=True,
                        reminder_sent=True,
                        metadata={"reminder_reason": reminder_reason},
                    )
                    return "reminder_sent"

            deps.instrumentation_store.finalize_target_run(
                target_run_id=target_run_id,
                completed_at=datetime.now(UTC),
                duration_seconds=perf_counter() - target_start,
                status="completed",
                metadata={"reason": "not_modified"},
            )
            return "unchanged"

        review_payload = extract_review_payload(fetch_result, target)
        deps.instrumentation_store.mark_target_stage(
            target_run_id=target_run_id,
            stage="payload_extracted",
        )

        content_hash = compute_content_hash(review_payload)
        deps.instrumentation_store.update_target_run(
            target_run_id=target_run_id,
            content_hash=content_hash,
        )
        deps.instrumentation_store.mark_target_stage(
            target_run_id=target_run_id,
            stage="content_hashed",
        )

        deps.state_store.record_collection_check(
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
        deps.instrumentation_store.update_target_run(
            target_run_id=target_run_id,
            request_reason=request_reason,
        )

        reminder_due = False
        reminder_reason = None
        if not should_queue and previous is not None:
            reminder_due, reminder_reason = should_send_reminder(previous,
                                                                 target, now)

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
            queue_id = deps.queue_store.enqueue_research(
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
            deps.state_store.mark_research_pending(
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
            deps.instrumentation_store.finalize_target_run(
                target_run_id=target_run_id,
                completed_at=datetime.now(UTC),
                duration_seconds=perf_counter() - target_start,
                status="completed",
                queued_for_research=True,
                queue_id=queue_id,
                metadata={"request_reason": request_reason},
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
                deps.state_store.\
                    record_reminder_sent(page_key=target.page_key,
                                         sent_at=now)
                deps.instrumentation_store.finalize_target_run(
                    target_run_id=target_run_id,
                    completed_at=datetime.now(UTC),
                    duration_seconds=perf_counter() - target_start,
                    status="completed",
                    reminder_attempted=True,
                    reminder_sent=True,
                    metadata={"reminder_reason": reminder_reason},
                )
                return "reminder_sent"

        deps.instrumentation_store.finalize_target_run(
            target_run_id=target_run_id,
            completed_at=datetime.now(UTC),
            duration_seconds=perf_counter() - target_start,
            status="completed",
            metadata={"request_reason": request_reason},
        )
        return "unchanged"

    except Exception as exc:
        deps.instrumentation_store.append_target_error(
            target_run_id=target_run_id,
            stage="process_target",
            message=str(exc),
            exception_type=type(exc).__name__,
            details={"page_key": target.page_key, "url": str(target.url)},
        )
        deps.instrumentation_store.finalize_target_run(
            target_run_id=target_run_id,
            completed_at=datetime.now(UTC),
            duration_seconds=perf_counter() - target_start,
            status="persist_failed",
        )
        deps.logger.exception("Collection processing failed page_key=%s",
                              target.page_key)
        return "failed"


def run_ingestion_cycle(
    *,
    app: AppConfig,
    deps: IngestionDependencies,
    started_at: datetime,
) -> None:
    counters = IngestionRunCounters()
    run_id = deps.instrumentation_store.create_run(
        pipeline_name="site_monitor_data_ingestion",
        started_at=started_at,
        target_count=len(app.targets),
        enabled_target_count=sum(1 for target in app.
                                 targets if target.enabled),
        metadata={"force_research_after_hours": app.force_research_after_hours},  # noqa: E501
    )

    overall_start = perf_counter()

    for target in app.targets:
        result = process_target(app=app,
                                target=target,
                                deps=deps,
                                run_id=run_id)
        if result == "failed":
            counters.failed += 1
        elif result == "skipped":
            counters.skipped += 1
        else:
            counters.succeeded += 1
            if result == "queued":
                counters.queued += 1
            elif result == "reminder_sent":
                counters.reminder_sent += 1
            elif result == "unchanged":
                counters.unchanged += 1

    duration_seconds = perf_counter() - overall_start
    run_status = "completed_with_errors" if counters.failed else "completed"

    deps.instrumentation_store.finalize_run(
        run_id=run_id,
        completed_at=datetime.now(UTC),
        duration_seconds=duration_seconds,
        status=run_status,
        succeeded_target_count=counters.succeeded,
        failed_target_count=counters.failed,
        skipped_target_count=counters.skipped,
        queued_target_count=counters.queued,
        reminder_sent_count=counters.reminder_sent,
        unchanged_target_count=counters.unchanged,
        error_count=counters.failed,
        warning_count=0,
        metadata={},
    )
