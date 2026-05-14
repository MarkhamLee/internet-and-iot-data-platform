# (C) Markham Lee 2023 - 2026
# https://github.com/MarkhamLee/internet-and-iot-data-platform
# Building and sending Slack messages
from __future__ import annotations
import os
import requests
import sys
from datetime import datetime
from schemas import PageReviewResult, TrackedPageState

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from agent_library.logging_util import console_logging  # noqa: E402


logger = console_logging("slack messaging")


EVENT_META = {
    "became_desired": {
        "emoji": "🟢",
        "label": "Available now",
    },
    "desired_reminder": {
        "emoji": "🔔",
        "label": "Still available",
    },
    "became_undesired": {
        "emoji": "🔴",
        "label": "No longer available",
    },
    "missed_it": {
        "emoji": "⚠️",
        "label": "You missed it",
    },
    "recovered": {
        "emoji": "🔵",
        "label": "Recovered",
    },
    "no_change": {
        "emoji": "⚪",
        "label": "No change",
    },
}


def build_slack_message(
    page_key: str,
    url: str,
    review: PageReviewResult,
    previous: TrackedPageState | None,
    event_type: str,
    now: datetime,
) -> dict:
    meta = EVENT_META.get(
        event_type,
        {"emoji": "ℹ️", "label": "Update"},
    )

    fallback_lines = [
        f"{meta['emoji']} {page_key}",
        f"Event: {meta['label']}",
        f"Status: {review.page_status}",
        f"Summary: {review.summary}",
        f"Confidence: {review.confidence:.2f}",
        f"URL: {url}",
    ]

    if review.extracted_price:
        fallback_lines.append(f"Price: {review.extracted_price}")

    if review.evidence:
        fallback_lines.append("Evidence: " + " | ".join(review.evidence[:3]))

    if previous and previous.desired_state_started_at:
        fallback_lines.append(
            f"Desired since: {previous.desired_state_started_at.isoformat()}"
        )

    fallback_lines.append(f"Checked at: {now.isoformat()}")

    fields = [
        {
            "type": "mrkdwn",
            "text": f"*Event*\n{meta['label']}",
        },
        {
            "type": "mrkdwn",
            "text": f"*Status*\n{review.page_status}",
        },
        {
            "type": "mrkdwn",
            "text": f"*Confidence*\n{review.confidence:.2f}",
        },
        {
            "type": "mrkdwn",
            "text": f"*Checked at*\n{now.isoformat()}",
        },
    ]

    if review.extracted_price:
        fields.append(
            {
                "type": "mrkdwn",
                "text": f"*Price*\n{review.extracted_price}",
            }
        )

    if previous and previous.desired_state_started_at:
        fields.append(
            {
                "type": "mrkdwn",
                "text": f"*Desired since*\n{previous.desired_state_started_at.isoformat()}",  # noqa: E501
            }
        )

    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"{meta['emoji']} {page_key}",
                "emoji": True,
            },
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Summary*\n{review.summary}",
            },
        },
        {
            "type": "section",
            "fields": fields[:10],
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*URL*\n<{url}|Open page>",
            },
        },
    ]

    if review.evidence:
        evidence_text = "\n".join(f"• {item}" for item in review.evidence[:5])
        blocks.append(
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Evidence*\n{evidence_text}",
                },
            }
        )

    return {
        "text": " | ".join(fallback_lines),
        "blocks": blocks,
    }


def send_slack_webhook(webhook_url: str, payload: dict) -> int:
    headers = {
        "Content-Type": "application/json; charset=utf-8",
    }

    try:
        response = requests.post(
            webhook_url,
            headers=headers,
            json=payload,
            timeout=(5, 20),
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        status_code = getattr(exc.response, "status_code", 0)
        logger.debug(
            f"Publishing of alert to Slack webhook failed with response code: {status_code}, error: {exc}"  # noqa: E501
        )
        return status_code

    logger.debug(
        f"Publishing of alert to Slack webhook succeeded with code: {response.status_code}"  # noqa: E501
    )
    return response.status_code
