import os
import requests
import sys


parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from network_monitoring_libraries.\
    logging_utils import console_logging  # noqa: E402

logger = console_logging('Network_utils')


def send_slack_webhook(webhook_url: str, message: str):

    headers = {
        'Content-type': 'application/json'

    }

    payload = {
        "text": message
    }

    response = requests.post(webhook_url, headers=headers, json=payload)

    code = response.status_code

    if code != 200:
        logger.debug(f'Publishing of alert to Slack webhook failed with response code: {code}')  # noqa: E501

    else:

        logger.debug(f'Publishing of alert to Slack webhook succeeded with code: {code}')  # noqa: E501

    return code
