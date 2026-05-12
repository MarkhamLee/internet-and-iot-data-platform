# Markham Lee (C) 2023 - 2026
# Internet and IoT Data Platform
# https://github.com/MarkhamLee/internet-and-iot-data-platform
# Utilities for AI Agents - will eventually merge this back into the
# ETL utilities
import requests
from logging_util import console_logging

logger = console_logging('Agent Utilities')


class AgentUtilities():

    def __init__(self):

        pass

    @staticmethod
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
