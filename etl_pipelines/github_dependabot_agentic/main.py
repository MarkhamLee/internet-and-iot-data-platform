# (C) Markham Lee 2023 - 2026
# https://github.com/MarkhamLee/internet-and-iot-data-platform
# Connects to the GitHub API to retrieve dependabot alerts on security
# vulnerabilities, counts the alerts with a status other than "fixed" and
# then writes that data to InfluxDB. In instances when there are unresolved
# security issues, alerts are sent via Slack.

import json 
import os
import requests
import sys
from logging_util import console_logging

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from etl_library.general_utilities import EtlUtilities  # noqa: E402
from github_library.github_agent_utilities import GitHubUtilities  # noqa: E402

# Load general utilities
etl_utilities = EtlUtilities()

# load GitHub utilities/shared library
github_utilities = GitHubUtilities()

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

    data = github_utilities.get_github_data(token,
                                            full_url,
                                            PIPELINE_NAME,
                                            REPO_NAME,
                                            PIPELINE_FAILURE_WEBHOOK)
    return data


def normalize_alert(alert: dict) -> dict:
    
    advisory = alert.get("security_advisory", {}) or {}
    vuln = alert.get("security_vulnerability", {}) or {}
    pkg = vuln.get("package", {}) or {}
    first_patched = vuln.get("first_patched_version", {}) or {}
    dependency = alert.get("dependency", {}) or {}
    manifest = alert.get("manifest") or dependency.get("manifest_path")

    return {
        "alert_number": alert.get("number"),
        "state": alert.get("state"),
        "dependency": {
            "package_name": pkg.get("name"),
            "ecosystem": pkg.get("ecosystem"),
            "manifest_path": manifest,
            "scope": dependency.get("scope"),
            "relationship": dependency.get("relationship"),
            },
            "severity": advisory.get("severity"),
            "summary": advisory.get("summary"),
            "description": advisory.get("description"),
            "cve_id": advisory.get("cve_id"),
            "ghsa_id": advisory.get("ghsa_id"),
            "vulnerable_version_range": vuln.get("vulnerable_version_range"),
            "first_patched_version": first_patched.get("identifier"),
            "created_at": alert.get("created_at"),
            "updated_at": alert.get("updated_at"),
            "html_url": alert.get("html_url"),
        }


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
    data = github_utilities.get_github_data(GITHUB_TOKEN,
                                            full_url,
                                            PIPELINE_NAME,
                                            REPO_NAME,
                                            PIPELINE_FAILURE_WEBHOOK)

    alert_count = len(data)

    if alert_count == 0:
        logger.info('No security alerts, exiting')
        sys.exit()
    
    logger.info(f'{alert_count} dependabot alerts identified')
    # get normalized dependabot data 
    
    logger.info('Normalizing dependabot data')
    normalized_alerts = [normalize_alert(alert) for alert in data]

    logger.info('Preparing LLM payload')
    payload = prepare_llm_payload(normalized_alerts)

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
