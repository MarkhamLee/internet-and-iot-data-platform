# (C) Markham Lee 2023 - 2026
# https://github.com/MarkhamLee/internet-and-iot-data-platform
# Orchestrator / primary script
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from datetime import UTC, datetime
from time import perf_counter
from typing import Any

from config import load_config
from content_extractor import extract_review_payload
from diff_service import determine_event_type, should_invoke_llm
from page_fetcher import fetch_page
from schemas import PageReviewResult
from state_store import StateStore
from slack_messaging import build_slack_message, send_slack_webhook

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from agent_library.logging_util import console_logging  # noqa: E402
from agent_library.qwen_client import QwenClient  # noqa: E402


logger = console_logging("site_monitor_logs")


REVIEW_PROMPT = """
You are reviewing an e-commerce or product page.

Decide whether the page is in the desired state based on the configured goal.
Return only structured data matching the schema.

Guidance:
- desired = the target condition is currently true
- undesired = the target condition is currently false
- unknown = page is ambiguous, broken, blocked, or inconclusive
- Use direct page evidence, not guesses
"""


def normalize_text(value: str) -> str:
    value = value.strip()
    value = re.sub(r"\s+", " ", value)
    return value


def canonicalize_review_payload(payload: dict[str, Any]) -> dict[str, Any]:
    selector_hits = [
        {
            "selector": item.get("selector"),
            "text": normalize_text(item.get("text", "")),
        }
        for item in payload.get("selector_hits", [])
    ]

    selector_hits.sort(key=lambda item: (str(item["selector"]),
                                         str(item["text"])))
    button_texts = sorted(normalize_text(text)
                          for text in payload.get("button_texts", []))

    return {
        "final_url": payload.get("final_url"),
        "pattern_hits": sorted(payload.get("pattern_hits", [])),
        "selector_hits": selector_hits,
        "button_texts": button_texts,
        "page_text_excerpt": normalize_text(payload.
                                            get("page_text_excerpt", "")),
        "desired_state_description": payload.get("desired_state_description"),
        "undesired_state_description": payload.
        get("undesired_state_description"),
        "custom_prompt": payload.get("custom_prompt"),
    }


def compute_content_hash(payload: dict[str, Any]) -> str:
    canonical = canonicalize_review_payload(payload)
    encoded = json.dumps(
        canonical,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def main() -> None:
    app = load_config()
    store = StateStore(app.postgres_dsn)

    client = QwenClient(
        ollama_url=app.ollama_url,
        model=app.qwen_model,
        approved_models=set(app.approved_models),
        timeout=(10, 180),
        temperature=0,
    )

    force_review_after_hours = getattr(app, "force_review_after_hours", None)

    overall_start = perf_counter()
    logger.info(
        "Starting review of web site targets count=%s force_review_after_hours=%s",  # noqa: E501
        len(app.targets),
        force_review_after_hours,
    )

    for target in app.targets:
        target_start = perf_counter()

        if not target.enabled:
            logger.info("Skipping disabled target page_key=%s",
                        target.page_key)
            continue

        now = datetime.now(UTC)
        previous = store.get_current_state(target.page_key)

        logger.info("Checking target page_key=%s url=%s",
                    target.page_key,
                    target.url)

        try:
            logger.info("Fetching page page_key=%s url=%s",
                        target.page_key,
                        target.url)
            fetch_result = fetch_page(
                str(target.url),
                etag=previous.last_http_etag if previous else None,
                last_modified=previous.
                last_http_last_modified if previous else None,
            )
            logger.info(
                "Fetch completed page_key=%s status_code=%s final_url=%s etag_present=%s last_modified_present=%s",  # noqa: E501
                target.page_key,
                fetch_result.status_code,
                fetch_result.final_url,
                bool(fetch_result.etag),
                bool(fetch_result.last_modified),
            )
        except Exception:
            logger.exception(
                "Fetch failed for page_key=%s url=%s",
                target.page_key,
                target.url,
            )
            continue

        if fetch_result.status_code == 304 and previous is not None:
            logger.info(
                "No remote change detected via HTTP validators for page_key=%s; skipping LLM",  # noqa: E501
                target.page_key,
            )
            store.touch_page_check(
                page_key=target.page_key,
                url=str(target.url),
                now=now,
                http_etag=fetch_result.etag,
                http_last_modified=fetch_result.last_modified,
                content_hash=previous.last_content_hash,
                previous=previous,
            )
            target_duration = round(perf_counter() - target_start, 2)
            logger.info(
                "Completed target page_key=%s duration_seconds=%s",
                target.page_key,
                target_duration,
            )
            continue

        review_payload = extract_review_payload(fetch_result, target)
        review_payload["desired_state_description"] = target.\
            desired_state_description
        review_payload["undesired_state_description"] = target.\
            undesired_state_description
        review_payload["custom_prompt"] = target.custom_prompt

        content_hash = compute_content_hash(review_payload)

        should_review, review_reason = should_invoke_llm(
            previous=previous,
            content_hash=content_hash,
            now=now,
            force_review_after_hours=force_review_after_hours,
        )

        if not should_review:
            logger.info(
                "Skipping LLM for page_key=%s reason=%s",
                target.page_key,
                review_reason,
            )
            store.touch_page_check(
                page_key=target.page_key,
                url=str(target.url),
                now=now,
                http_etag=fetch_result.etag,
                http_last_modified=fetch_result.last_modified,
                content_hash=content_hash,
                previous=previous,
            )
            target_duration = round(perf_counter() - target_start, 2)
            logger.info(
                "Completed target page_key=%s duration_seconds=%s",
                target.page_key,
                target_duration,
            )
            continue

        logger.info(
            "Invoking Qwen for page_key=%s reason=%s",
            target.page_key,
            review_reason,
        )

        try:
            review = client.generate_structured_response(
                prompt=REVIEW_PROMPT,
                payload=review_payload,
                response_model=PageReviewResult,
            )
            logger.info(
                "Qwen review completed page_key=%s page_status=%s confidence=%.3f state_key=%s",  # noqa: E501
                target.page_key,
                review.page_status,
                review.confidence,
                review.normalized_state_key,
            )
        except Exception:
            logger.exception(
                "Qwen review failed for page_key=%s url=%s",
                target.page_key,
                target.url,
            )
            continue

        event_type, should_send = determine_event_type(
            previous=previous,
            current=review,
            now=now,
            reminder_interval_minutes=target.reminder_interval_minutes,
        )

        logger.info(
            "Review outcome page_key=%s event_type=%s should_send=%s page_status=%s confidence=%.3f",  # noqa: E501
            target.page_key,
            event_type,
            should_send,
            review.page_status,
            review.confidence,
        )

        slack_sent = False
        sent_at = None

        if should_send:
            logger.info(
                "Sending Slack message page_key=%s event_type=%s",
                target.page_key,
                event_type,
            )
            try:
                slack_payload = build_slack_message(
                    page_key=target.page_key,
                    url=str(target.url),
                    review=review,
                    previous=previous,
                    event_type=event_type,
                    now=now,
                )

                status_code = send_slack_webhook(app.slack_webhook_url,
                                                 slack_payload)

                if status_code == 200:
                    slack_sent = True
                    sent_at = now
                    logger.info(
                        "Slack send succeeded page_key=%s event_type=%s status_code=%s",  # noqa: E501
                        target.page_key,
                        event_type,
                        status_code,
                    )
                else:
                    logger.warning(
                        "Slack webhook returned non-200 page_key=%s event_type=%s code=%s",  # noqa: E501
                        target.page_key,
                        event_type,
                        status_code,
                    )
            except Exception:
                logger.exception(
                    "Slack send failed for page_key=%s event_type=%s",
                    target.page_key,
                    event_type,
                )
        else:
            logger.info(
                "No Slack message needed page_key=%s event_type=%s",
                target.page_key,
                event_type,
            )

        try:
            store.save_result(
                page_key=target.page_key,
                url=str(target.url),
                review=review,
                now=now,
                event_type=event_type,
                slack_sent=slack_sent,
                send_time=sent_at,
                previous=previous,
                http_etag=fetch_result.etag,
                http_last_modified=fetch_result.last_modified,
                content_hash=content_hash,
                llm_invoked=True,
            )
            logger.info(
                "Persisted result page_key=%s event_type=%s slack_sent=%s",
                target.page_key,
                event_type,
                slack_sent,
            )
        except Exception:
            logger.exception(
                "Failed to persist result for page_key=%s event_type=%s",
                target.page_key,
                event_type,
            )

        target_duration = round(perf_counter() - target_start, 2)
        logger.info(
            "Completed target page_key=%s duration_seconds=%s",
            target.page_key,
            target_duration,
        )

    overall_duration = round(perf_counter() - overall_start, 2)
    logger.info("Site monitor run completed in %s seconds", overall_duration)


if __name__ == "__main__":
    main()
