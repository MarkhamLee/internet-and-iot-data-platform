# Markham Lee (C) 2023
# productivity-music-stocks-weather-IoT-dashboard
# https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
# Utility script for connecting to the Slack API to post messages/alerts to a
# Slack channel.
# Current plan is to use this for alerting related to IoT devices,
# monitoring HW and to alert me if an Airflow pipeline fails.
# This file is basically a baseline Slack client, expect the variants used for
# Airflow vs say IoT to drift apart over time.

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

    # generic method to send a slack message, to the specified channel
    def send_slack_message(self, message: str, channel: str) -> dict:

        response = self.client.chat_postMessage(text=message, channel=channel)

        return self.evaluate_response(response.code, 'webhook')

    # the web hook only sends to a specific channel
    def send_slack_webhook(self, url: str, message: dict):

        headers = {
            'Content-type': 'application/json'

        }

        response = requests.post(url, headers=headers, json=message)

        return self.evaluate_response(response.code, 'webhook')

    def evaluate_response(self, code: int, type: str):

        if code == 200:
            logger.info(f'Publishing of alert to Slack {type} was successful')

        else:
            logger.debug(f'Publishing of alert to Slack {type} failed, with error code {code}')  # noqa: E501

        return code
