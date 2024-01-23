# Markham Lee (C) 2023
# productivity-music-stocks-weather-IoT-dashboard
# https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
# Utility script for retrieving data from Asana
import requests
from logging_util import logger


class ETLUtilities():

    def __init__(self):

        pass

    @staticmethod
    def send_slack_webhook(payload: str, webhook: str):

        headers = {
            'Content-type': 'application/json'
        }

        payload = {
            "text": payload
               
        }

        response = requests.post(webhook, headers=headers, json=payload)

        if response.status_code != 200:
            logger.info(f'Slack alert send attempt failed with error code: {response.status_code}')  # noqa: E501

        else:
            logger.info(f'Slack alert sent successfully with status code: {response.status_code}')  # noqa: E501

        return response
