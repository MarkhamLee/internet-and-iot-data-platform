# Markham Lee (C) 2023 - 2024
# productivity-music-stocks-weather-IoT-dashboard
# https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
# general utilities to aid ETL pipelines

import requests
import os
from etl_library.logging_util import logger  # noqa: E402

# load Slack Webhook URL for sending pipeline failure alerts
WEBHOOK_URL = os.environ.get('ALERT_WEBHOOK')


class EtlUtilities():

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

        return EtlUtilities.evaluate_slack_response(response.status_code,
                                                    'webhook')

    @staticmethod
    def evaluate_slack_response(code: int, type: str):

        if code == 200:
            logger.info(f'Publishing of alert to Slack {type} was successful')

        else:
            logger.debug(f'Publishing of alert to Slack {type} failed, with error code {code}')  # noqa: E501

        return code

    @staticmethod
    def generic_post_request(payload: dict, url: str):

        headers = {}
        files = []

        try:

            response = requests.request("POST", url, headers=headers,
                                        data=payload, files=files)
            logger.info(f'post request sent successfully with response: {response.txt}')  # noqa: E501

        except Exception as e:
            message = (f'post request failed with error: {e}')
            logger.debug(message)
            # EtlUtilities.send_slack_webhook(WEBHOOK_URL, message)
