# Markham Lee (C) 2023 - 2024
# productivity-music-stocks-weather-IoT-dashboard
# https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
# general utilities to aid ETL pipelines

import requests
import os
from jsonschema import validate
from etl_library.logging_util import logger  # noqa: E402

# load Slack Webhook URL for sending pipeline failure alerts
WEBHOOK_URL = os.environ['ALERT_WEBHOOK']


class EtlUtilities():

    def __init__(self):

        pass

    # validates a given json vs previously defined schema - i.e., verify that
    # the data is in the desired format.
    @staticmethod
    def validate_json(data: dict, schema: dict) -> int:

        # validate the data
        try:
            validate(instance=data, schema=schema)
            return 0

        except Exception as e:
            message = (f'Data validation failed for the pipeline for openweather current, with error: {e}')  # noqa: E501
            logger.debug(message)
            response = EtlUtilities.send_slack_webhook(WEBHOOK_URL, message)
            logger.debug(f'Slack pipeline failure alert sent with code: {response}')  # noqa: E501
            return 1, response

    # send data directly to a Slack incoming webhook
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

    # evaluates the response code and writes the appropriate message
    # to the logs
    @staticmethod
    def evaluate_slack_response(code: int, type: str):

        if code == 200:
            logger.info(f'Publishing of alert to Slack {type} was successful')

        else:
            logger.debug(f'Publishing of alert to Slack {type} failed, with error code {code}')  # noqa: E501

        return code

    # generic post requuest to a given URL
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
