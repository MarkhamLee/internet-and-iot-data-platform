# (C) Markham Lee 2023 - 2026
# https://github.com/MarkhamLee/internet-and-iot-data-platform
# Slack block format message builder for the site monitor
# agent
from __future__ import annotations

from datetime import datetime
from schemas import PageAnalysisWrite


CONFIDENCE_EMOJI = {
    "high": "🟢",
    "medium": "🟡",
    "low": "🔴",
}

ACTION_LABEL = {
    "alert": "🔔 Alert",
    "monitor": "👁 Monitor",
    "no_action": "✅ No Action",
}


def build_alert_blocks(
    result: PageAnalysisWrite,
    now: datetime,
) -> dict:
    confidence_label = (
        CONFIDENCE_EMOJI.get(result.confidence, "⚪")
        + f" {result.confidence}"
    )
    action_label = ACTION_LABEL.get(
        result.recommended_action,
        f"ℹ️ {result.recommended_action}",
    )
    timestamp = now.strftime("%Y-%m-%d %H:%M UTC")

    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "🔍 Site Monitor Alert",
                "emoji": True,
            },
        },
        {"type": "divider"},
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*Page Key:*\n`{result.page_key}`",
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Detected At:*\n{timestamp}",
                },
            ],
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*URL:*\n<{result.url}|{result.url}>",
            },
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*Confidence:*\n{confidence_label}",
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Action:*\n{action_label}",
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Page Status:*\n`{result.result_page_status}`",
                },
                {
                    "type": "mrkdwn",
                    "text": (
                        f"*Event Type:*\n`{result.result_event_type or 'N/A'}`"
                    ),
                },
            ],
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Summary:*\n{result.summary}",
            },
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Reasoning:*\n{result.reasoning}",
            },
        },
        {"type": "divider"},
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": (
                        f"Model: `{result.model_name}` | "
                        f"Queue ID: `{result.queue_id}` | "
                        f"Desired state found: `{result.desired_state_found}`"
                    ),
                }
            ],
        },
    ]

    fallback_text = (
        f"Site Monitor Alert: {result.page_key} — "
        f"{result.summary} "
        f"[{result.result_page_status or 'unknown'}, "
        f"confidence: {result.confidence}] "
        f"{result.url}"
    )

    return build_slack_payload(blocks, fallback_text)


def build_slack_payload(blocks: list, fallback_text: str) -> dict:
    return {
        "text": fallback_text,
        "blocks": blocks,
    }
