# (C) Markham Lee 2023 - 2024
# https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
# Retrieves Github actions data (total minutes used) from the Github API.

import os
import sys
import json
from jsonschema import validate

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from etl_library.influx_utilities import InfluxClient  # noqa: E402
from etl_library.logging_util import logger  # noqa: E402
from etl_library.general_utilities import EtlUtilities  # noqa: E402
from github_library.github_utilities import GitHubUtilities  # noqa: E402

# Load general utilities
etl_utilities = EtlUtilities()

# load InfluxDB utilities
influx = InfluxClient()

# load GitHub utilities/shared library
github_utilities = GitHubUtilities()

# load Slack Webhook URL variable for sending pipeline failure alerts
WEBHOOK_URL = os.environ.get('ALERT_WEBHOOK')

# load repo name - it's for all the repos, but load it regardless
REPO_NAME = os.environ['ACCOUNT_NAME']


def build_url(endpoint: str):

    BASE_URL = "https://api.github.com"

    full_url = BASE_URL + endpoint

    logger.info(f'API URL created: {full_url}')

    return full_url


def get_repo_actions(full_url: str, token: str) -> dict:

    PIPELINE_NAME = os.environ['GITHUB_ACCOUNT_ACTIONS_PIPELINE']

    github_utilities = GitHubUtilities()

    data = github_utilities.get_github_data(token, full_url, PIPELINE_NAME,
                                            REPO_NAME)
    return data


def validate_data(data: dict) -> dict:

    # open data validation file
    with open('github_actions_payload.json') as file:
        SCHEMA = json.load(file)

    try:
        validate(instance=data, schema=SCHEMA)
        logger.info('Data validation successful')
        return 0

    except Exception as e:
        message = (f'Pipeline failure: data validation failed for Github actions with error: {e}')  # noqa: E501
        logger.debug(message)
        response = etl_utilities.send_slack_webhook(WEBHOOK_URL, message)
        logger.debug(f'Slack pipeline failure alert sent with code: {response}')  # noqa: E501
        return response


def parse_data(data: dict) -> dict:

    # validate data
    response = validate_data(data)

    if response == 0:
        parsed_payload = {"total_minutes": data["total_minutes_used"],
                          "total_paid_minutes_used":
                              data["total_paid_minutes_used"]}
    else:
        logger.debug("Data validation failed, exiting...")
        sys.exit()

    return parsed_payload


def main():

    ENDPOINT = os.environ['ACTIONS_ENDPOINT']

    # build URL for API request
    full_url = build_url(ENDPOINT)

    # retrieve GitHub token
    GITHUB_TOKEN = os.environ['GITHUB_TOKEN']

    # get data
    data = get_repo_actions(full_url, GITHUB_TOKEN)

    # parse out data
    payload = parse_data(data)

    # load InfluxDB variables for storing data
    MEASUREMENT = os.environ['GITHUB_ACTIONS_MEASUREMENT']
    BUCKET = os.environ['DEVOPS_BUCKET']

    tag_name = "Github Actions Count"
    field_name = "github_actions"

    # write data
    github_utilities.write_github_data(payload, MEASUREMENT,
                                       BUCKET, tag_name, field_name)


if __name__ == "__main__":
    main()
