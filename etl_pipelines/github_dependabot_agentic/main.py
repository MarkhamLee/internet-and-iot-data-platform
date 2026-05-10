# (C) Markham Lee 2023 - 2024
# https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
# Connects to the GitHub API to retrieve dependabot alerts on security
# vulnerabilities, counts the alerts with a status other than "fixed" and
# then writes that data to InfluxDB. In instances when there are unresolved
# security issues, alerts are sent via Slack.

import json 
import os
import requests
import sys

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from etl_library.logging_util import logger  # noqa: E402
from etl_library.general_utilities import EtlUtilities  # noqa: E402
from github_library.github_agent_utilities import GitHubUtilities  # noqa: E402

# Load general utilities
etl_utilities = EtlUtilities()

# load GitHub utilities/shared library
github_utilities = GitHubUtilities()

# load Slack Webhook URL variable for sending pipeline failure alerts
WEBHOOK_URL = os.environ['PIPELINE_FAILURE_WEBHOOK']

# load Slack Webhook for sending dependabot alerts
DEPENDABOT_SLACK_WEBHOOK = os.environ['DEPENDABOT_SLACK_WEBHOOK']

# retrieve GitHub token
GITHUB_TOKEN = os.environ['GITHUB_DEPENDABOT_TOKEN']

# load repo name
REPO_NAME = 'internet-and-iot-data-platform'
REPO_BASE = 'repos/markhamlee/'
ALERTS_ENDPOINT = '/dependabot/alerts'
GITHUB_BASE_URL = os.environ['GITHUB_API_BASE_URL']
PIPELINE_NAME = 'Dependabot Agent Pipeline'


OLLAMA_URL = 'https://ollama.local.markhamslab.com'
MODEL_URL = (f"{OLLAMA_URL}/api/tags")
TIMEOUT = (3, 10)  # connect, read
APPROVED_MODELS = {"qwen3.5:9b", "llama3.2:3b"}


def fetch_models_response():
    try:
        response = requests.get(MODEL_URL, timeout=TIMEOUT)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as exc:
        raise RuntimeError(f"Ollama URL is not available: {exc}") from exc


def get_model_list(response):
    try:
        data = response.json()
    except ValueError as exc:
        raise RuntimeError("Ollama returned invalid JSON") from exc

    approved_available = [
        model["name"]
        for model in data.get("models", [])
        if model.get("name") in APPROVED_MODELS
    ]

    if not approved_available:
        raise RuntimeError("No approved models available")

    return approved_available

# this ensures that the URL only returns open dependabot alerts
def build_url(endpoint: str):
    separator = "&" if "?" in endpoint else "?"
    full_url = (
        GITHUB_BASE_URL
        + REPO_BASE
        + REPO_NAME
        + endpoint
        + f"{separator}state=open"
    )
    logger.info(f"Github URL created: {full_url}")
    return full_url


def get_dependabot_data(full_url: str, token: str) -> dict:

    github_utilities = GitHubUtilities()

    data = github_utilities.get_github_data(token,
                                            full_url,
                                            PIPELINE_NAME,
                                            REPO_NAME)
    return data






def main():

    logger.info('Verifying Ollama is online and has the required models available')

    try:
        response = fetch_models_response()
        model_list = get_model_list(response)
        logger.info(f'Ollama is online, the available models are: {model_list}')

    except RuntimeError as exc:
        logger.debug(exc, file=sys.stderr)
        sys.exit(1)


    # build URL
    full_url = build_url(ALERTS_ENDPOINT)

    # get GitHub dependabot alerts data
    data = get_dependabot_data(full_url, GITHUB_TOKEN)

    



if __name__ == "__main__":
    main()
