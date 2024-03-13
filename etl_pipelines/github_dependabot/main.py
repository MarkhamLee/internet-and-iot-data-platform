# (C) Markham Lee 2023 - 2024
# https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
# Connects to the GitHub API to retrieve dependabot alerts on security
# vulnerabilities, counts the alerts with a status other than "fixed" and
# then writes that data to InfluxDB. In instances when there are unresolved
# security issues, alerts are sent via Slack.

import os
import sys
import requests

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from etl_library.influx_utilities import InfluxClient  # noqa: E402
from etl_library.logging_util import logger  # noqa: E402
from etl_library.general_utilities import EtlUtilities  # noqa: E402

# Load general utilities
etl_utilities = EtlUtilities()

# load Slack Webhook URL variable for sending pipeline failure alerts
WEBHOOK_URL = os.environ['ALERT_WEBHOOK']

# load Slack Webhook URL for sending dependabot security alerts
DEPENDABOT_WEBHOOK_URL = os.environ['SECURITY_SLACK_WEBHOOK']

# load repo name env vars
REPO_NAME = os.environ['REPO_NAME']


# TODO: move to utilities file
def build_url(endpoint: str):

    BASE_URL = os.environ['GITHUB_BASE_URL']

    return BASE_URL + endpoint


# TODO: move to utilities
def get_github_data(token: str, full_url: str) -> dict:

    headers = {
        "Authorization": f"Bearer {token}",
        'X-GitHub-Api-Version': '2022-11-28',
        "Accept": "application/vnd.github+json"
    }

    response = requests.get(full_url, headers=headers)

    try:
        response.raise_for_status()

    except requests.exceptions.RequestException as e:
        message = (f'Pipeline failure: Github data retrieval error: {e}')
        logger.debug(message)
        logger.debug(f'Slack pipeline failure alert sent with code: {response}')  # noqa: E501
        return etl_utilities.send_slack_webhook(WEBHOOK_URL, message)

    logger.info('Github security alerts data retrieved')
    return response.json()


def count_alerts(data: dict) -> dict:

    # data validation is simple because we're only tracking
    # one field - if the state field isn't available the
    # below will throw an error.

    try:
        # count alerts
        alerts = int(len([i for i in data if i['state'] != 'fixed']))

        if alerts > 0:
            message = (f'Security vulnerability discovered in repo: {REPO_NAME}')  # noqa: E501
            logger.info(message)
            response = etl_utilities.send_slack_webhook(DEPENDABOT_WEBHOOK_URL, message)  # noqa: E501
            logger.message(f'Dependabot security alert sent via Slack with code: {response}')  # noqa: E501

        logger.info(f'{alerts} alerts detected for {REPO_NAME}')
        return alerts

    except Exception as e:
        logger.debug(f"Data validation failed/state field missing with error: {e}")  # noqa: E501
        sys.exit()


def write_data(alert_count: float):

    influx = InfluxClient()

    MEASUREMENT = os.environ['GITHUB_ALERTS_MEASUREMENT']

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
                "GitHub_Data": "alerts",
        }
    }

    payload = {"alerts_count": alert_count}

    try:
        # write data to InfluxDB
        influx.write_influx_data(client, base_payload, payload, BUCKET)
        logger.info('GitHub data successfuly written to InfluxDB')
        return 0

    except Exception as e:
        message = (f'InfluxDB write error for Github Actions data: {e}')
        logger.debug(message)
        response = etl_utilities.send_slack_webhook(WEBHOOK_URL, message)
        logger.debug(f'Slack pipeline failure alert sent with code: {response}')  # noqa: E501
        return 1, response


def main():

    ENDPOINT = os.environ['ALERTS_ENDPOINT']

    full_url = build_url(ENDPOINT)

    GITHUB_TOKEN = os.environ['GITHUB_TOKEN']

    data = get_github_data(GITHUB_TOKEN, full_url)

    count = count_alerts(data)

    write_data(count)


if __name__ == "__main__":
    main()
