# (C) Markham Lee 2023 - 2026
# https://github.com/MarkhamLee/internet-and-iot-data-platform
# Client for pulling and normalizing/cleaning up data from
# the GitHub API. 
import os
import sys
import requests
from logging_util import console_logging

logger = console_logging("GitHub client")

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from etl_library.general_utilities import EtlUtilities  # noqa: E402


class GitHubClient():

    def __init__(self,
                 github_token: str,
                 github_base_url: str,
                 github_repo_base_url: str,
                 github_repo_name: str,
                 github_api_endpoint: str,
                 github_dependabot_state: str,
                 pipeline_failure_webhook: str):

        self.github_token = github_token
        self.github_base_url = github_base_url
        self.github_repo_base_url = github_repo_base_url
        self.github_repo_name = github_repo_name
        self.github_api_endpoint = github_api_endpoint
        self.github_dependabot_state = github_dependabot_state
        self.pipeline_failure_webhook = pipeline_failure_webhook
        
        # load basic ETL utilities
        self.etl_utilities = EtlUtilities()

        # build GitHub API URL
        self.github_api_url = self.build_url(
            self.github_base_url,
            self.github_repo_base_url,
            self.github_repo_name,
            self.github_api_endpoint,
            self.github_dependabot_state
        )
       

    def build_url(self,
                  github_base_url: str,
                  github_repo_base_url: str,
                  github_repo_name: str,
                  github_api_endpoint: str,
                  github_dependabot_state):
        separator = "&" if "?" in github_api_endpoint else "?"
        
        full_url = (
            github_base_url
            + github_repo_base_url
            + github_repo_name
            + github_api_endpoint
            + f"{separator}state={github_dependabot_state}" 
        )
        logger.info(f"Github URL created: {full_url}")
        return full_url

    # retrieve github dependabot data
    def get_github_data(self,
                        pipeline_name: str) -> dict:

        headers = {
            "Authorization": f"Bearer {self.github_token}",
            'X-GitHub-Api-Version': '2022-11-28',
            "Accept": "application/vnd.github+json"
        }

        response = requests.get(self.github_api_url, headers=headers)

        try:
            response.raise_for_status()

        except requests.exceptions.RequestException as e:
            message = (f'Pipeline failure for {pipeline_name} for {self.github_repo_name}, GitHub data retrieval error: {e}')  # noqa: E501
            logger.debug(message)

            response = self.etl_utilities.send_slack_webhook(self.pipeline_failure_webhook,
                                                             message)
            logger.debug(f'Slack pipeline failure alert sent with code: {response}')  # noqa: E501
            sys.exit(1)

        logger.info(f'Data retrieved for Github {pipeline_name} for {self.github_repo_name}')  # noqa: E501
        
        # normalize dependabot data
        alert_data = response.json()

        if len(alert_data) > 0:
            [self.normalize_alert_data(alert) for alert in alert_data]
        
        return alert_data      

    def normalize_alert_data(self,
                             alert: dict) -> dict:
        
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
