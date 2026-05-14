# (C) Markham Lee 2023-2026
# Internet & IoT Data Platform
# https://github.com/MarkhamLee/internet-and-iot-data-platform
import requests
from logging_util import console_logging

logger = console_logging('agent_utilities_logs')


def send_slack_webhook(url: str, message: str):

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
