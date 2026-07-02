# (C) Markham Lee 2023 - 2026
# https://github.com/MarkhamLee/internet-and-iot-data-platform
# Research pipeline orchestrator for the site monitor agent
from __future__ import annotations

import os
import sys
from datetime import UTC, datetime
from time import perf_counter

from config import AppConfig
from postgres_queue_repository import PostgresQueueRepository
from schemas import PageAnalysisResponse, PageAnalysisWrite, ResearchQueueItem
from slack_messaging import build_alert_blocks

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from agent_library.logging_util import console_logging  # noqa: E402
from agent_library.\
    agent_utilities import send_slack_webhook_block  # noqa: E402
from agent_library.qwen_client import QwenClient  # noqa: E402

logger = console_logging("research_pipeline")

REVIEW_PROMPT = """
You are reviewing a monitored web page for a specific desired state.

Your task:
- Review the page content provided in the payload.
- Determine whether the page has reached the desired state described in
  the watch criteria.
- Return a structured assessment.

Return fields:
- desired_state_found: true or false
- confidence: high, medium, or low
- summary: one sentence describing what you found on the page
- reasoning: brief explanation of your conclusion
- recommended_action: one of alert, monitor, no_action
  - alert: desired state found, or something significant and unexpected changed
  - monitor: content changed but desired state not yet confirmed
  - no_action: page unchanged or change is not meaningful
- result_page_status: your short label for the current page state,
  e.g. "desired", "undesired", "unchanged", "unknown"
- result_event_type: optional short label for the type of change that
  occurred, e.g. "became_desired", "became_undesired", "price_drop",
  "in_stock", or null if no change

Be conservative: only set desired_state_found=true when clearly evident
from the page content.
""".strip()


def build_review_payload(item: ResearchQueueItem) -> dict:
    return {
        "task": "review_page_for_desired_state",
        "page": {
            "page_key": item.page_key,
            "url": item.url,
            "request_reason": item.request_reason,
            "pending_reconfirmation": item.pending_reconfirmation,
            "content": item.payload,
        },
    }


def process_queue_item(
    *,
    item: ResearchQueueItem,
    app: AppConfig,
    client: QwenClient,
) -> tuple[str, PageAnalysisWrite | None]:
    """Process a single research queue item.

    Returns (outcome, result) where outcome is one of:
    'alerted', 'no_action', 'failed'
    """
    item_start = perf_counter()
    now = datetime.now(UTC)
    repo = PostgresQueueRepository(app.postgres_dsn)

    logger.info(
        "Processing research queue item queue_id=%s page_key=%s reason=%s",
        item.id,
        item.page_key,
        item.request_reason,
    )

    try:
        repo.claim_item(queue_id=item.id, now=now)

        payload = build_review_payload(item)

        logger.info(
            "Invoking Qwen for queue_id=%s page_key=%s",
            item.id,
            item.page_key,
        )
        llm_start = perf_counter()
        response: PageAnalysisResponse = client.generate_structured_response(
            prompt=REVIEW_PROMPT,
            payload=payload,
            response_model=PageAnalysisResponse,
        )
        llm_duration = round(perf_counter() - llm_start, 2)

        logger.info(
            "Qwen response received queue_id=%s page_key=%s "
            "desired_state_found=%s confidence=%s action=%s duration=%ss",
            item.id,
            item.page_key,
            response.desired_state_found,
            response.confidence,
            response.recommended_action,
            llm_duration,
        )

        result = PageAnalysisWrite(
            queue_id=item.id,
            page_key=item.page_key,
            url=item.url,
            desired_state_found=response.desired_state_found,
            confidence=response.confidence,
            summary=response.summary,
            reasoning=response.reasoning,
            recommended_action=response.recommended_action,
            result_page_status=response.result_page_status,
            result_event_type=response.result_event_type,
            model_name=client.model,
        )

        alert_sent = False
        should_alert = (
            response.desired_state_found
            or response.recommended_action == "alert"
        )

        if should_alert:
            event_type = response.result_event_type or "alert"
            logger.info(
                "Sending Slack alert queue_id=%s page_key=%s event_type=%s",
                item.id,
                item.page_key,
                event_type,
            )
            slack_payload = build_alert_blocks(
                result=result,
                now=now,
            )
            status_code = send_slack_webhook_block(
                app.slack_webhook_url, slack_payload
            )

            if status_code == 200:
                alert_sent = True
                result.alert_sent = True
                logger.info(
                    "Slack alert sent successfully queue_id=%s page_key=%s "
                    "event_type=%s",
                    item.id,
                    item.page_key,
                    event_type,
                )
            else:
                logger.warning(
                    "Slack alert failed queue_id=%s page_key=%s "
                    "event_type=%s status_code=%s",
                    item.id,
                    item.page_key,
                    event_type,
                    status_code,
                )
        else:
            logger.info(
                "No Slack alert needed queue_id=%s page_key=%s action=%s",
                item.id,
                item.page_key,
                response.recommended_action,
            )

        repo.complete_item(
            queue_id=item.id,
            now=datetime.now(UTC),
            result_page_status=response.result_page_status,
            result_event_type=response.result_event_type,
        )

        item_duration = round(perf_counter() - item_start, 2)
        logger.info(
            "Completed queue_id=%s page_key=%s alert_sent=%s duration=%ss",
            item.id,
            item.page_key,
            alert_sent,
            item_duration,
        )

        return ("alerted" if alert_sent else "no_action"), result

    except Exception as exc:
        logger.exception(
            "Research pipeline failed queue_id=%s page_key=%s",
            item.id,
            item.page_key,
        )
        repo.fail_item(
            queue_id=item.id,
            now=datetime.now(UTC),
            error_message=str(exc),
        )
        return "failed", None


def run_research_cycle(
    *,
    app: AppConfig,
    client: QwenClient,
    review_limit: int = 25,
) -> dict:
    """Fetch pending queue items and process each one.

    Returns a counters dict suitable for write_instrumentation.
    """
    # started_at = datetime.now(UTC)
    overall_start = perf_counter()

    repo = PostgresQueueRepository(app.postgres_dsn)

    logger.info("Querying research queue for pending items")
    items = repo.fetch_pending_items(limit=review_limit)

    if not items:
        logger.info("No pending items in research queue")
        return {
            "items_fetched": 0,
            "llm_invoked": 0,
            "alerted": 0,
            "slack_attempted": 0,
            "slack_sent": 0,
            "failed": 0,
            "status": "success",
            "errors": None,
        }

    logger.info("Found %s pending item(s) in research queue", len(items))

    llm_invoked = 0
    alerted = 0
    slack_attempted = 0
    slack_sent = 0
    failed = 0
    errors: list[str] = []
    llm_durations: list[float] = []

    for item_index, item in enumerate(items, start=1):
        logger.info(
            "Processing item %s of %s queue_id=%s page_key=%s",
            item_index,
            len(items),
            item.id,
            item.page_key,
        )

        t = perf_counter()
        outcome, result = process_queue_item(
            item=item,
            app=app,
            client=client,
        )
        llm_durations.append(perf_counter() - t)
        llm_invoked += 1

        if outcome == "failed":
            failed += 1
            errors.append(f"queue_id={item.id} page_key={item.page_key}")
        elif outcome == "alerted":
            alerted += 1
            slack_attempted += 1
            if result and result.alert_sent:
                slack_sent += 1
        else:
            # no_action — Slack was not attempted
            pass

    total_duration = round(perf_counter() - overall_start, 2)
    avg_llm = (
        round(sum(llm_durations) / len(llm_durations), 2)
        if llm_durations else None
    )
    status = "partial" if failed else "success"

    logger.info(
        "Research cycle complete llm_invoked=%s alerted=%s "
        "slack_sent=%s failed=%s duration=%ss avg_llm=%ss",
        llm_invoked,
        alerted,
        slack_sent,
        failed,
        total_duration,
        avg_llm,
    )

    return {
        "items_fetched": len(items),
        "llm_invoked": llm_invoked,
        "alerted": alerted,
        "slack_attempted": slack_attempted,
        "slack_sent": slack_sent,
        "failed": failed,
        "avg_llm_seconds": avg_llm,
        "duration_seconds": total_duration,
        "status": status,
        "errors": errors if errors else None,
    }
