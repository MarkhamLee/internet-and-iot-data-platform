# (C) Markham Lee 2023 - 2026
# https://github.com/MarkhamLee/internet-and-iot-data-platform
# Orchestrator for Qwen based AI Agent for monitoring GitHub
# dependabot alerts, evaluating risks and then sending a report
# with recommendations
import json 
import os
import requests
import sys
from logging_util import console_logging
from github_client import GitHubClient
from qwen_client import QwenClient


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

logger = console_logging(PIPELINE_NAME)

logger.info('Intantiating GitHub Client')
github_client = GitHubClient(
    GITHUB_TOKEN,
    GITHUB_BASE_URL,
    REPO_BASE,
    REPO_NAME,
    ALERTS_ENDPOINT,
    'open',
    PIPELINE_FAILURE_WEBHOOK
)

logger.info('Instantiating Qwen Client')
qwen_client = QwenClient(
    ollama_url="https://ollama.local.markhamslab.com",
    model="qwen3.5:9b",
    approved_models=APPROVED_MODELS
)

def prepare_llm_payload(alerts):
    
    return {
        "task": "review_dependabot_alerts",
        "repository": REPO_NAME,
        "instructions": {
            "goal": (
                "Review each open Dependabot alert and assess practical remediation "
                "priority, likely impact, and recommended next action."
            ),
            "output_format": "json",
            "per_alert_fields": [
                "alert_number",
                "priority",
                "risk_summary",
                "recommended_action",
                "reasoning",
                "confidence"
            ]
        },
        "alerts": alerts
    }


def main():

    logger.info('Retrieving GitHub dependabot data')
    alert_data = github_client.get_github_data(PIPELINE_NAME)

    logger.info('Preparing LLM payload')    
    
    if len(alert_data) < 1:
        logger.info('No dependabot alerts available')
        sys.exit(1)

    logger.info('Writing dependabot data to Postgres')
    

    
    llm_payload = prepare_llm_payload(alert_data)


    # retrieve research state, i.e., which of these have been
    # researched and if so, how long has it been since they were last
    # research 

    # decision gate send reminder slack or research 


    # IF researching, send payload to Qwen 
    # add call to Quen 

    # Receive data back, update Postgres
    # Send detailed Slack Report  


if __name__ == "__main__":
    main()
