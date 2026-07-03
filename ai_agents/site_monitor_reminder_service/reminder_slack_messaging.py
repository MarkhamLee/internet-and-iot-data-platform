# (C) Markham Lee 2023 - 2026
# https://github.com/MarkhamLee/internet-and-iot-data-platform
# Slack block message builder for the site monitor reminder service
from __future__ import annotations

from datetime import datetime


def build_reminder_blocks(
    *,
    page_key: str,
    url: str,
    now: datetime,
    reminder_count: int,
    last_review_summary: str | None,
) -> dict:
    timestamp = now.strftime("%Y-%m-%d %H:%M UTC")

    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "🔔 Site Monitor Reminder",
                "emoji": True,
            },
        },
        {"type": "divider"},
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*Page Key:*\n`{page_key}`",
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Checked At:*\n{timestamp}",
                },
            ],
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*URL:*\n<{url}|{url}>",
            },
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Last Summary:*\n{last_review_summary or 'N/A'}",
            },
        },
        {"type": "divider"},
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"Reminder #{reminder_count} | Still in desired state",  # noqa: E501
                }
            ],
        },
    ]

    fallback_text = (
        f"Site Monitor Reminder: {page_key} is still in desired state "
        f"(reminder #{reminder_count}) | {url}"
    )

    return build_slack_payload(blocks, fallback_text)


def build_slack_payload(blocks: list, fallback_text: str) -> dict:
    return {
        "text": fallback_text,
        "blocks": blocks,
    }
