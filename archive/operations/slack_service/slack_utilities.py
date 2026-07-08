# Markham Lee (C) 2023
# productivity-music-stocks-weather-IoT-dashboard
# https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
# Utility script for connecting to the Slack API to post messages/alerts to a
# Slack channel.

import requests
import os
from slack_sdk import WebClient
from logging_util import logger


class SlackUtilities():

    def __init__(self):

        # get secret
        self.secret = os.environ.get("SLACK_SECRET")

        # create client
        self.client = WebClient(self.secret)

    # send a slack message to a specific channel
    def send_slack_message(self, message: str, channel: str) -> dict:

        response = self.client.chat_postMessage(text=message, channel=channel)

        return self.evaluate_response(response.status_code, 'channel')

    # the web hook only sends to a specific channel
    @staticmethod
    def send_slack_webhook(url: str, message: str):

        headers = {
            'Content-type': 'application/json'

        }

        payload = {
            "text": message
        }

        response = requests.post(url, headers=headers, json=payload)

        return SlackUtilities.evaluate_response(response.status_code,
                                                'webhook')

    @staticmethod
    def evaluate_response(code: int, type: str):

        if code == 200:
            logger.info(f'Publishing of alert to Slack {type} was successful')

        else:
            logger.debug(f'Publishing of alert to Slack {type} failed, with error code {code}')  # noqa: E501

        return code
