from __future__ import annotations

import requests
from datetime import datetime, timedelta


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


def build_reminder_payload(*, page_key: str, url: str, now: datetime) -> dict:
    return {
        "text": f"🔔 {page_key} still appears available as of {now.isoformat()} | {url}",  # noqa: E501
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"🔔 {page_key}",
                    "emoji": True,
                },
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Event*\nStill available reminder",
                },
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*URL*\n<{url}|Open page>",
                },
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Checked at*\n{now.isoformat()}",
                },
            },
        ],
    }


def send_reminder(webhook_url: str, payload: dict) -> int:
    response = requests.post(
        webhook_url,
        headers={"Content-Type": "application/json; charset=utf-8"},
        json=payload,
        timeout=(5, 20),
    )
    return response.status_code
