# Markham Lee (C) 2023
# productivity-music-stocks-weather-IoT-dashboard
# https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
# Utility script for connecting to the Slack API to post messages/alerts to a
# Slack channel.
# Current plan is to use this for alerting related to IoT devices,
# monitoring HW and to alert me if an Airflow pipeline fails.
# This file is basically a baseline Slack client, expect the variants used for
# Airflow vs say IoT to drift apart over time.

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import logging
import requests
import os


# setup logging for static methods
logging.basicConfig(filename='slack_alerts.log', level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(name)s %(threadName)s\
                        : %(message)s')


class SlackUtilities():

    def __init__(self):

        # get secret
        self.secret = os.environ.get("SLACK_SECRET")

        # create client
        self.client = WebClient(self.secret)

    # plan is to only use web hooks for now, but putting this here as it allows
    # us to send messages to any channel within my slack account, while the
    # web hooks are directed towards very specific channels.
    @staticmethod
    def send_slack_message(self, message: str, channel: str) -> dict:

        try:
            response = self.client.chat_postMessage(channel=channel,
                                                    text=message)
            logging.debug(f'alert sent successfully, \
                               response code: {response.status_code}')
            return response.status_code

        except SlackApiError as e:
            logging.debug(f'an error occured with error \
                {e} and response code: {e.response.status_code}')
            return e.response.status_code

    # the web hooks only allow posting to one channel, but they're more secure
    # require less effort to send via SSL and don't require additional
    # libraries so this will be the preferred method
    @staticmethod
    def send_slack_webhook(url: str, message: dict):

        headers = {
            'Content-type': 'application/json'

        }

        response = requests.post(url, headers=headers, json=message)

        if response.status_code != 200:
            logging.debug(f'publishing of slack alert failed, \
                status code: {response.status_code}')

        return response
