# (C) Markham Lee 2023-2026
# Internet & IoT Data Platform
# https://github.com/MarkhamLee/internet-and-iot-data-platform
import requests
from agent_library.logging_util import console_logging

logger = console_logging('agent_utilities_logs')


def send_slack_webhook_basic(url: str, message: str):

    headers = {
        'Content-type': 'application/json'

    }

    payload = {
        "text": message
    }

    response = requests.post(url, headers=headers, json=payload)

    code = response.status_code

    if code != 200:
        logger.debug(f'Publishing of alert to Slack webhook failed with response code: {code}')  # noqa: E501
    else:
        logger.debug(f'Publishing of alert to Slack webhook suceeded with code: {code}')  # noqa: E501

    return code


def send_slack_webhook_block(webhook_url: str, payload: dict) -> int:
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
