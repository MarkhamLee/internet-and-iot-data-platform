# (C) Markham Lee 2023 - 2026
# https://github.com/MarkhamLee/internet-and-iot-data-platform
# Slack block format message builder for the site monitor
# agent
from __future__ import annotations

from datetime import datetime
from schemas import PageAnalysisWrite, ResearchCompletion


CONFIDENCE_EMOJI = {
    "high": "🟢",
    "medium": "🟡",
    "low": "🔴",
}


def build_alert_blocks(
    result: PageAnalysisWrite,
    now: datetime,
    completion: ResearchCompletion | None = None,
) -> dict:
    confidence_label = (
        CONFIDENCE_EMOJI.get(result.confidence, "⚪")
        + f" {result.confidence}"
    )
    event_type = completion.\
        event_type if completion is not None else result.result_event_type
    event_labels = {
        "desired_state_confirmed": "Desired state confirmed",
        "became_desired": "Desired state reached",
        "became_undesired": "Desired state no longer met",
    }
    action_label = event_labels.get(event_type, "State notification")
    transition_label = (
        f"{completion.previous_status} -> {completion.current_status}"
        if completion is not None else result.result_page_status
    )

    timestamp = now.strftime("%Y-%m-%d %H:%M UTC")

    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": action_label,
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
                    "text": f"*Notification:*\n{action_label}",
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Page Status:*\n`{result.result_page_status}`",
                },
                {
                    "type": "mrkdwn",
                    "text": (
                        f"*Event Type:*\n`{event_type or 'N/A'}`"
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
                        f"Transition: `{transition_label}` | "
                        f"Desired state found: `{result.desired_state_found}`"
                    ),
                }
            ],
        },
    ]

    fallback_text = (
        f"{action_label}: {result.page_key} — "
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
