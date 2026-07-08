# Markham Lee (C) 2023 - 2026
# Internet and IoT Data Platform
# https://github.com/MarkhamLee/internet-and-iot-data-platform
# general utilities to aid ETL pipelines
import requests
from jsonschema import validate
from etl_library.logging_util import console_logging  # noqa: E402

logger = console_logging('ETL_utilities')


class EtlUtilities():

    def __init__(self):

        pass

    # validates a given json vs previously defined schema - i.e., verify that
    # the data is in the desired format.
    @staticmethod
    def validate_json(data: dict,
                      schema: dict,
                      failure_webhook) -> int:

        # validate the data
        try:
            validate(instance=data, schema=schema)
            return 0

        except Exception as e:
            message = (f'Data validation failed for the pipeline for openweather current, with error: {e}')  # noqa: E501
            logger.warning(message)
            response = EtlUtilities.send_slack_webhook(failure_webhook, message)  # noqa: E501
            logger.info('Slack pipeline failure alert sent with code: %s',
                        response)
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
            logger.debug('Publishing of alert to Slack webhook failed with response code: %s',  # noqa: E501
                         code)
        else:
            logger.debug('Publishing of alert to Slack webhook suceeded with code: %s',  # noqa: E501
                         code)

        return code

    # evaluates the response code and writes the appropriate message
    # to the logs
    @staticmethod
    def evaluate_slack_response(code: int, type: str):

        if code == 200:
            logger.info('Publishing of alert to Slack of type %s was successful',  # noqa: E501
                        type)

        else:
            logger.warning('Publishing of alert to Slack of type %s failed, with error code %s',  # noqa: E501
                           type,
                           code)

        return code

    # generic post requuest to a given URL
    @staticmethod
    def generic_post_request(payload: dict, url: str):

        headers = {}
        files = []

        try:

            response = requests.request("POST", url, headers=headers,
                                        data=payload, files=files)
            logger.info('post request sent successfully with response: %s',
                        response.txt)  # noqa: E501

        except Exception as e:
            logger.debug('Post request failed with error: %s',
                         e)
