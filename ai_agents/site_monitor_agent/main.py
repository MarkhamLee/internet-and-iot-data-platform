# WIP
# TODO: add more logging messages so progress can be tracked
# Use perf counter to time page evaluation
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

from config import load_config
from content_extractor import extract_review_payload
from diff_service import determine_event_type
from page_fetcher import fetch_page
from schemas import PageReviewResult
from state_store import StateStore

from ai_agents.site_monitor_agent.slack_messaging import (
    build_slack_message,
    send_slack_webhook,
)

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


def canonicalize_review_payload(payload: dict) -> dict:
    selector_hits = [
        {
            "selector": item.get("selector"),
            "text": normalize_text(item.get("text", "")),
        }
        for item in payload.get("selector_hits", [])
    ]

    return {
        "final_url": payload.get("final_url"),
        "pattern_hits": sorted(payload.get("pattern_hits", [])),
        "selector_hits": selector_hits,
        "page_text_excerpt": normalize_text(payload.get("page_text_excerpt", "")),  # noqa: E501
        "desired_state_description": payload.get("desired_state_description"),
        "undesired_state_description": payload.get("undesired_state_description"),  # noqa: E501
        "custom_prompt": payload.get("custom_prompt"),
    }


def compute_content_hash(payload: dict) -> str:
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
        ollamaurl=app.ollama_url,
        model=app.qwen_model,
        approvedmodels=set(app.approved_models),
        timeout=(10, app.timeout_seconds),
        temperature=0,
    )

    for target in app.targets:
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
            fetch_result = fetch_page(
                str(target.url),
                etag=previous.last_http_etag if previous else None,
                last_modified=previous.
                last_http_last_modified if previous else None,
            )
        except Exception as exc:
            logger.exception(
                "Fetch failed for page_key=%s url=%s error=%s",
                target.page_key,
                target.url,
                exc,
            )
            continue

        if fetch_result.status_code == 304 and previous is not None:
            logger.info(
                "No remote change detected via HTTP validators for page_key=%s; skipping LLM",  # noqa: E501
                target.page_key,
            )
            continue

        review_payload = extract_review_payload(fetch_result, target)
        review_payload["desired_state_description"] = target.\
            desired_state_description
        review_payload["undesired_state_description"] = target.\
            undesired_state_description
        review_payload["custom_prompt"] = target.custom_prompt

        content_hash = compute_content_hash(review_payload)

        if previous and previous.last_content_hash == content_hash:
            logger.info(
                "No meaningful content change detected for page_key=%s; skipping LLM",  # noqa: E501
                target.page_key,
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
            continue

        logger.info(
            "Content change detected for page_key=%s; invoking Qwen",
            target.page_key,
        )

        try:
            review = client.generate_structured_response(
                prompt=REVIEW_PROMPT,
                payload=review_payload,
                response_model=PageReviewResult,
            )
        except Exception as exc:
            logger.exception(
                "Qwen review failed for page_key=%s url=%s error=%s",
                target.page_key,
                target.url,
                exc,
            )
            continue

        event_type, should_send = determine_event_type(
            previous=previous,
            current=review,
            now=now,
            reminder_interval_minutes=target.reminder_interval_minutes,
        )

        slack_sent = False
        sent_at = None

        if should_send:
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
                else:
                    logger.warning(
                        "Slack webhook returned non-200 for page_key=%s code=%s",  # noqa: E501
                        target.page_key,
                        status_code,
                    )
            except Exception as exc:
                logger.exception(
                    "Slack send failed for page_key=%s error=%s",
                    target.page_key,
                    exc,
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
        except Exception as exc:
            logger.exception(
                "Failed to persist result for page_key=%s error=%s",
                target.page_key,
                exc,
            )

    logger.info("Site monitor run completed")


if __name__ == "__main__":
    main()
