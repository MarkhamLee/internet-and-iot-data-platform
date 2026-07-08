# (C) Markham Lee 2023 - 2026
# https://github.com/MarkhamLee/internet-and-iot-data-platform
# Orchestrator for retrieving dependabot alert data from the GitHub API
# and then updating each alert's status in Postgres
import os
import sys
import postgres_data_sync
from logging_util import console_logging
from github_client import GitHubClient


parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from etl_library.general_utilities import EtlUtilities  # noqa: E402

# Load general utilities
etl_utilities = EtlUtilities()

# load Slack Webhook URL variable for sending pipeline failure alerts
PIPELINE_FAILURE_WEBHOOK = os.environ['PIPELINE_FAILURE_WEBHOOK']

# load Slack Webhook for sending dependabot alerts
DEPENDABOT_SLACK_WEBHOOK = os.environ['DEPENDABOT_SLACK_WEBHOOK']

# retrieve GitHub token
GITHUB_TOKEN = os.environ['GITHUB_DEPENDABOT_TOKEN']

# Postgres data
ALERT_STATUS_TABLE = os.environ['DEPENDABOT_ALERT_STATUS_TABLE']
POSTGRES_DATABASE = os.environ['POSTGRES_DEPENDABOT_DATABASE']
POSTGRES_SECRET = os.environ['DEPENDABOT_AGENT_POSTGRES']
POSTGRES_USER_NAME = os.environ['POSTGRES_USER_DEPENDABOT']
POSTGRES_HOST = os.environ['POSTGRES_HOST_K3S']
POSTGRES_PORT = 5432


# load repo name
REPO_NAME = os.environ["REPO_NAME"]
REPO_BASE = 'repos/markhamlee/'
ALERTS_ENDPOINT = '/dependabot/alerts'
GITHUB_BASE_URL = os.environ['GITHUB_API_BASE_URL']
PIPELINE_NAME = 'Dependabot Agent Pipeline'
REPO_URL_BASE = 'https://github.com/MarkhamLee/'
REPO_OWNER_NAME = 'markhamlee'

FULL_REPO_URL = (f'{REPO_URL_BASE}/{REPO_NAME}')

logger = console_logging(PIPELINE_NAME)

logger.info('Intantiating GitHub Client')
github_client = GitHubClient(
    GITHUB_TOKEN,
    GITHUB_BASE_URL,
    REPO_BASE,
    REPO_NAME,
    REPO_OWNER_NAME,
    ALERTS_ENDPOINT,
    'open',
    PIPELINE_FAILURE_WEBHOOK
)


def main():

    logger.info('Retrieving GitHub dependabot data')
    github_alert_records, repo_web_url, api_url, \
        repo_full_name = github_client.get_github_data(PIPELINE_NAME)

    logger.info('Connecting to Postgres')
    conn = postgres_data_sync.postgres_connection(
        POSTGRES_HOST,
        POSTGRES_PORT,
        POSTGRES_DATABASE,
        POSTGRES_USER_NAME,
        POSTGRES_SECRET
    )

    logger.info('Updating Dependabot alert status data in Postgres')

    postgres_data_sync.sync_open_alerts(
        conn=conn,
        repo_full_name=repo_full_name,
        prepared_alerts=github_alert_records
    )

    logger.info('Dependabot alert data sync complete')


if __name__ == "__main__":
    main()
