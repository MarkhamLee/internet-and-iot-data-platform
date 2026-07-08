# (C) Markham Lee 2023 - 2024
# https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
# General utilities for pulling data from the GitHub API

import os
import sys
import requests

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from etl_library.influx_utilities import InfluxClient  # noqa: E402
from etl_library.logging_util import logger  # noqa: E402
from etl_library.general_utilities import EtlUtilities  # noqa: E402


class GitHubUtilities():

    def __init__(self):

        # load variables
        self.etl_utilities = EtlUtilities()

        # load InfluxDB utilities
        self.influx = InfluxClient()

        # load Slack Webhook URL variable for sending pipeline failure alerts
        self.WEBHOOK_URL = os.environ.get('ALERT_WEBHOOK')

    # generic data retrieval method - once the URL is created/you have
    # the right endpoint, the data retrieval process is always the same.
    def get_github_data(self, token: str,
                        full_url: str, pipeline_name: str,
                        repo_name: str) -> dict:

        headers = {
            "Authorization": f"Bearer {token}",
            'X-GitHub-Api-Version': '2022-11-28',
            "Accept": "application/vnd.github+json"
        }

        response = requests.get(full_url, headers=headers)

        try:
            response.raise_for_status()

        except requests.exceptions.RequestException as e:
            message = (f'Pipeline failure for {pipeline_name} for {repo_name}, GitHub data retrieval error: {e}')  # noqa: E501
            logger.debug(message)

            WEBHOOK_URL = os.environ['ALERT_WEBHOOK']
            response = self.etl_utilities.send_slack_webhook(WEBHOOK_URL,
                                                             message)
            logger.debug(f'Slack pipeline failure alert sent with code: {response}')  # noqa: E501
            sys.exit()

        logger.info(f'Data retrieved for Github {pipeline_name} for {repo_name}')  # noqa: E501
        return response.json()

    def get_influx_client(self):

        # Influx DB variables
        INFLUX_KEY = os.environ['INFLUX_KEY']
        ORG = os.environ['INFLUX_ORG']
        URL = os.environ['INFLUX_URL']

        # get the client for connecting to InfluxDB
        client = self.influx.create_influx_client(INFLUX_KEY, ORG, URL)

        return client

    def write_github_data(self, data: float, measurement: str,
                          bucket: str, tag_name: str):

        # get InfluxDB client
        client = self.get_influx_client()

        # base payload
        base_payload = {
            "measurement": measurement,
            "tags": {
                    "GitHub_Data": tag_name,
            }
        }

        try:
            # write data to InfluxDB
            self.influx.write_influx_data(client, base_payload, data, bucket)
            logger.info('GitHub data successfuly written to InfluxDB')
            return 0

        except Exception as e:
            message = (f'InfluxDB write error for Github Actions data: {e}')
            logger.debug(message)
            response = self.etl_utilities.send_slack_webhook(self.WEBHOOK_URL,
                                                             message)
            logger.debug(f'Slack pipeline failure alert sent with code: {response}')  # noqa: E501
            return response
