# (C) Markham Lee 2023 - 2024
# https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
# General utilities for pulling data from the GitHub API

import os
import sys
import requests

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from etl_library.logging_util import logger  # noqa: E402
from etl_library.general_utilities import EtlUtilities  # noqa: E402


class GitHubUtilities():

    def __init__(self):

        # load variables
        self.etl_utilities = EtlUtilities()

    # generic data retrieval method - once the URL is created/you have
    # the right endpoint, the data retrieval process is always the same.
    @staticmethod
    def get_github_data(token: str,
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
            response = GitHubUtilities.etl_utilities.\
                send_slack_webhook(WEBHOOK_URL, message)
            logger.debug(f'Slack pipeline failure alert sent with code: {response}')  # noqa: E501
            return response

        logger.info(f'Data retrieved for Github {pipeline_name} for {repo_name}')  # noqa: E501
        return response.json()
