from __future__ import annotations

import requests
from collections.abc import Mapping
from typing import Any
from requests import Response

from platform_utils.platform_logger import configure_logger

logger = configure_logger('alert_utilities_logs')


SLACK_WEBHOOK_TIMEOUT = (5, 20)
SLACK_SUCCESS_RESPONSE = "ok"
SLACK_SEND_FAILURE_STATUS = 400


def send_slack_webhook_basic(webhook_url: str, message: str) -> int:
    """Entry method for sending plain text Slack messages via a webhook."""
    return _send_slack_webhook(
        webhook_url=webhook_url,
        payload={"text": message},
    )


def send_slack_webhook_block(
    webhook_url: str,
    payload: Mapping[str, Any],
) -> int:
    """Entry method for sending a block format Slack message via a webhook."""
    return _send_slack_webhook(
        webhook_url=webhook_url,
        payload=payload,
    )


def _send_slack_webhook(
    webhook_url: str,
    payload: Mapping[str, Any],
) -> int:
    """Sends the Slack webhook payload"""
    try:
        response = requests.post(
            webhook_url,
            json=payload,
            timeout=SLACK_WEBHOOK_TIMEOUT,
        )
        response.raise_for_status()

    except requests.RequestException as exc:
        status_code = (
            exc.response.status_code
            if exc.response is not None
            else 0
        )

        logger.warning(
            "Slack webhook publish failed: status_code=%d error_type=%s",
            status_code,
            type(exc).__name__,
        )
        return status_code

    return evaluate_slack_response(response)


def evaluate_slack_response(response: Response) -> int:
    """
    Slack's API returns 200 for a successful webhook connection,
    even if the message send fail, this "intercept" ensures that a
    200 code is only returned for a successfully sent message.
    """
    response_message = response.text.strip()

    if response_message != SLACK_SUCCESS_RESPONSE:
        logger.warning(
            "Slack webhook returned an unexpected success response: "
            "status_code=%d response=%r",
            response.status_code,
            response_message,
        )
        return SLACK_SEND_FAILURE_STATUS

    logger.info(
        "Slack webhook message sent: status_code=%d",
        response.status_code,
    )
    return response.status_code
