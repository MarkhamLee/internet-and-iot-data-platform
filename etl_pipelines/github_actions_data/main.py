# (C) Markham Lee 2023 - 2024
# https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
# Retrieves Github actions data (total minutes used) from the Github API.

import os
import sys
import requests
import json
from jsonschema import validate

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from etl_library.influx_utilities import InfluxClient  # noqa: E402
from etl_library.logging_util import logger  # noqa: E402
from etl_library.general_utilities import EtlUtilities  # noqa: E402

# Load general utilities
etl_utilities = EtlUtilities()

# load Slack Webhook URL variable for sending pipeline failure alerts
WEBHOOK_URL = os.environ.get('ALERT_WEBHOOK')


def build_url(endpoint: str):

    BASE_URL = "https://api.github.com"

    return BASE_URL + endpoint


def get_github_data(token: str, full_url: str) -> dict:

    headers = {
        "Authorization": f"Bearer {token}",
        'X-GitHub-Api-Version': '2022-11-28',
        "Accept": "application/vnd.github+json"
    }

    try:
        response = requests.get(full_url, headers)
        logger.info('Github actions data retrieved')
        return response.json()

    except Exception as e:
        message = (f'Pipeline failure: Github data retrieval error: {e}')
        logger.debug(message)
        response = etl_utilities.send_slack_webhook(WEBHOOK_URL, message)
        logger.debug(f'Slack pipeline failure alert sent with code: {response}')  # noqa: E501


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
        return 1


def parse_data(data: dict) -> dict:

    # validate data
    response = validate_data(data)

    if response == 0:
        parsed_payload = {"total_minutes": data['total_minutes_used'],
                          "total_paid_minutes_used":
                              data['total_paid_minutes_used']}
    else:
        logger.debug("Data validation failed, exiting...")
        sys.exit()

    return parsed_payload


def write_data(payload: dict):

    influx = InfluxClient()

    MEASUREMENT = os.environ['GITHUB_ACTIONS_MEASUREMENT']

    # Influx DB variables
    INFLUX_KEY = os.environ['INFLUX_KEY']
    ORG = os.environ['INFLUX_ORG']
    URL = os.environ['INFLUX_URL']
    BUCKET = os.environ['DEVOPS_BUCKET']

    # get the client for connecting to InfluxDB
    client = influx.create_influx_client(INFLUX_KEY, ORG, URL)

    # base payload
    base_payload = {
        "measurement": MEASUREMENT,
        "tags": {
                "Github_Data": "actions",
        }
    }

    try:
        # write data to InfluxDB
        influx.write_influx_data(client, base_payload, payload, BUCKET)
        logger.info('Github data successfuly written to InfluxDB')

    except Exception as e:
        message = (f'InfluxDB write error for Github Actions data: {e}')
        logger.debug(message)
        response = etl_utilities.send_slack_webhook(WEBHOOK_URL, message)
        logger.debug(f'Slack pipeline failure alert sent with code: {response}')  # noqa: E501


def main():

    ENDPOINT = os.environ['ENDPOINT']

    full_url = build_url(ENDPOINT)

    GITHUB_TOKEN = os.environ['GITHUB_TOKEN']

    data = get_github_data(GITHUB_TOKEN, full_url)

    payload = parse_data(data)
    logger.info(f'payload ready: {payload}')

    write_data(payload)


if __name__ == "__main__":
    main()
