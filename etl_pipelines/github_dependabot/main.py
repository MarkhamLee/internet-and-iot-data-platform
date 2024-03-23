# (C) Markham Lee 2023 - 2024
# https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
# Connects to the GitHub API to retrieve dependabot alerts on security
# vulnerabilities, counts the alerts with a status other than "fixed" and
# then writes that data to InfluxDB. In instances when there are unresolved
# security issues, alerts are sent via Slack.

import os
import sys

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
WEBHOOK_URL = os.environ['ALERT_WEBHOOK']

# load repo name
REPO_NAME = os.environ['REPO_NAME']


def build_url(endpoint: str):

    BASE_URL = os.environ['GITHUB_BASE_URL']
    REPO_BASE = os.environ['REPO_BASE']

    full_url = BASE_URL + REPO_BASE + REPO_NAME + endpoint
    logger.info(f'Github URL created: {full_url}')

    return full_url


def get_dependabot_data(full_url: str, token: str) -> dict:

    NAME = os.environ['GITHUB_PIPELINE_NAME']

    github_utilities = GitHubUtilities()

    data = github_utilities.get_github_data(token, full_url, NAME,
                                            REPO_NAME)
    return data


# GitHub returns all alerts past or present, so we count up the
# ones that aren't fixed and only send alerts if there are alerts
# that need to be resolved.
def count_alerts(data: dict) -> dict:

    # data validation is simple because we're only tracking
    # one field - if the state field isn't available the
    # below will throw an error.

    # this env var should be defined in the DAG or Argo config file
    # I.e., basically a command line type parameter
    REPO_SHORT_NAME = os.environ['REPO_SHORT_NAME']

    try:
        # count alerts
        alerts = int(len([i for i in data if i['state'] != 'fixed']))

        if alerts > 0:
            message = (f'Security vulnerability discovered in repo: {REPO_NAME}')  # noqa: E501
            logger.info(message)

            # load Slack Webhook URL for sending dependabot security alerts
            DEPENDABOT_WEBHOOK_URL = os.environ['SECURITY_SLACK_WEBHOOK']

            response = etl_utilities.send_slack_webhook(DEPENDABOT_WEBHOOK_URL, message)  # noqa: E501
            logger.message(f'Dependabot security alert sent via Slack with code: {response}')  # noqa: E501

        logger.info(f'{alerts} alerts detected for {REPO_NAME}')
        field_name = (f'{REPO_SHORT_NAME}_dependabot_alerts')
        payload = {field_name: alerts}

        return payload

    except Exception as e:
        logger.debug(f"Data validation failed/state field missing with error: {e}")  # noqa: E501
        sys.exit()


def main():

    ENDPOINT = os.environ['ALERTS_ENDPOINT']

    # build URL
    full_url = build_url(ENDPOINT)

    # retrieve GitHub token
    GITHUB_TOKEN = os.environ['GITHUB_TOKEN']

    # get GitHub dependabot alerts data
    data = get_dependabot_data(full_url, GITHUB_TOKEN)

    # count the # of active alerts
    count = count_alerts(data)

    # load InfluxDB variables for storing data
    MEASUREMENT = os.environ['GITHUB_ALERTS_MEASUREMENT']
    BUCKET = os.environ['DEVOPS_BUCKET']

    TAG_NAME = "Dependabot Alerts"

    # write data
    github_utilities.write_github_data(count, MEASUREMENT, BUCKET, TAG_NAME)


if __name__ == "__main__":
    main()
