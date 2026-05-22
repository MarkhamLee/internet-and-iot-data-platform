# (C) Markham Lee 2023 - 2026
# https://github.com/MarkhamLee/internet-and-iot-data-platform
# Client for pulling and normalizing/cleaning up data from
# the GitHub API.
import hashlib
import json
import os
import requests
import sys
from requests.exceptions import RequestException

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from agent_library.logging_util import console_logging  # noqa: E402
from agent_library.\
    agent_utilities import send_slack_webhook_basic  # noqa: E402

logger = console_logging("GitHub client")


class GitHubClient:

    def __init__(
        self,
        github_token: str,
        github_base_url: str,
        github_repo_base_url: str,
        github_repo_name: str,
        github_owner_name: str,
        github_api_endpoint: str,
        github_dependabot_state: str,
        pipeline_failure_webhook: str,
        timeout: tuple[int, int] = (3, 15),
    ):
        self.github_token = github_token
        self.github_base_url = github_base_url.rstrip("/")
        self.github_repo_base_url = github_repo_base_url
        self.github_repo_name = github_repo_name
        self.github_repo_owner_name = github_owner_name
        self.github_repo_full_name = (f'{self.github_repo_owner_name}/{self.github_repo_name}')  # noqa: E501
        self.github_api_endpoint = github_api_endpoint
        self.github_dependabot_state = github_dependabot_state
        self.pipeline_failure_webhook = pipeline_failure_webhook
        self.timeout = timeout

        self.github_api_url, self.github_repo_web_url = self.build_url(
            self.github_base_url,
            self.github_repo_base_url,
            self.github_repo_name,
            self.github_api_endpoint,
            self.github_dependabot_state,
            self.github_repo_owner_name
        )

    def build_url(
        self,
        github_base_url: str,
        github_repo_base_url: str,
        github_repo_name: str,
        github_api_endpoint: str,
        github_dependabot_state: str,
        github_repo_owner: str,
    ) -> str:
        separator = "&" if "?" in github_api_endpoint else "?"
        repo_api_url = (
            f"{github_base_url}/"
            f"{github_repo_base_url}"
            f"{github_repo_name}"
            f"{github_api_endpoint}"
            f"{separator}state={github_dependabot_state}"
        )
        logger.info("Github API URL created: %s", repo_api_url)

        repo_web_url = (f'https://github.com/{github_repo_owner}/{github_repo_name}')  # noqa: E501

        return repo_api_url, repo_web_url

    def _build_fingerprint(self, payload: dict) -> str:
        serialized = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    def get_github_data(self, pipeline_name: str) -> list[dict]:
        headers = {
            "Authorization": f"Bearer {self.github_token}",
            "X-GitHub-Api-Version": "2022-11-28",
            "Accept": "application/vnd.github+json",
        }

        try:
            response = requests.get(
                self.github_api_url,
                headers=headers,
                timeout=self.timeout,
            )
            response.raise_for_status()
        except RequestException as exc:
            message = ('Pipeline failure for %s for %s, "GitHub data retrieval error: %s',  # noqa: E501
                       pipeline_name,
                       self.github_repo_name,
                       exc)  # noqa: E501

            logger.debug(message)
            webhook_response = send_slack_webhook_basic(
                self.pipeline_failure_webhook,
                message,
            )
            logger.debug(
                "Slack pipeline failure alert sent with code: %s",
                webhook_response,
            )
            raise RuntimeError(message) from exc

        logger.info(
            "Data retrieved for Github %s for %s",
            pipeline_name,
            self.github_repo_name,
        )

        try:
            alert_data = response.json()

        except ValueError as exc:
            raise RuntimeError("GitHub returned invalid JSON") from exc

        if not isinstance(alert_data, list):
            raise RuntimeError("GitHub Dependabot endpoint did not return a list")  # noqa: E501

        normalized_alerts = [
            self.prepare_alert_records(alert)
            for alert in alert_data
        ]

        return normalized_alerts, self.github_repo_web_url, \
            self.github_api_url, self.github_repo_full_name

    def prepare_alert_records(self, alert: dict) -> dict:
        advisory = alert.get("security_advisory", {}) or {}
        vuln = alert.get("security_vulnerability", {}) or {}
        pkg = vuln.get("package", {}) or {}
        first_patched = vuln.get("first_patched_version", {}) or {}
        dependency = alert.get("dependency", {}) or {}

        manifest_path = alert.\
            get("manifest") or dependency.get("manifest_path")
        alert_number = alert.get("number")
        github_state = alert.get("state") or "open"
        package_name = pkg.get("name")
        ecosystem = pkg.get("ecosystem")

        fingerprint_payload = {
            "github_state": github_state,
            "package_name": package_name,
            "ecosystem": ecosystem,
            "manifest_path": manifest_path,
            "scope": dependency.get("scope"),
            "relationship": dependency.get("relationship"),
            "severity": advisory.get("severity"),
            "summary": advisory.get("summary"),
            "cve_id": advisory.get("cve_id"),
            "ghsa_id": advisory.get("ghsa_id"),
            "vulnerable_version_range": vuln.get("vulnerable_version_range"),
            "first_patched_version": first_patched.get("identifier"),
        }

        source_fingerprint = self._build_fingerprint(fingerprint_payload)

        review_group_key = "::".join(
            [
                self.github_repo_full_name,
                ecosystem or "",
                package_name or "",
                manifest_path or "",
            ]
        )

        return {
            "alert_id": f"{self.github_repo_full_name}#{alert_number}",
            "repo_owner": self.github_repo_owner_name,
            "repo_name": self.github_repo_name,
            "repo_full_name": self.github_repo_full_name,
            "repo_html_url": self.github_repo_web_url,
            "repo_api_url": self.github_api_url,
            "alert_number": alert_number,
            "github_state": github_state,
            "package_name": package_name,
            "ecosystem": ecosystem,
            "manifest_path": manifest_path,
            "scope": dependency.get("scope"),
            "relationship": dependency.get("relationship"),
            "severity": advisory.get("severity"),
            "summary": advisory.get("summary"),
            "description": advisory.get("description"),
            "cve_id": advisory.get("cve_id"),
            "ghsa_id": advisory.get("ghsa_id"),
            "vulnerable_version_range": vuln.get("vulnerable_version_range"),
            "first_patched_version": first_patched.get("identifier"),
            "alert_html_url": alert.get("html_url"),
            "created_at": alert.get("created_at"),
            "updated_at": alert.get("updated_at"),
            "dismissed_at": alert.get("dismissed_at"),
            "dismissed_reason": alert.get("dismissed_reason"),
            "fixed_at": alert.get("fixed_at"),
            "auto_dismissed_at": alert.get("auto_dismissed_at"),
            "source_fingerprint": source_fingerprint,
            "review_group_key": review_group_key,
            "raw_alert_json": alert,
        }
