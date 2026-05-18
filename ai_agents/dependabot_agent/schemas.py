# (C) Markham Lee 2023 - 2026
# https://github.com/MarkhamLee/internet-and-iot-data-platform
from __future__ import annotations
from datetime import datetime
from typing import Literal
from pydantic import BaseModel


class AlertRecord(BaseModel):
    alert_id: str
    alert_number: int
    repo_owner: str | None = None
    repo_name: str | None = None
    repo_full_name: str
    repo_html_url: str | None = None
    repo_api_url: str | None = None
    github_state: str | None = None
    package_name: str
    ecosystem: str
    manifest_path: str | None = None
    scope: str | None = None
    relationship: str | None = None
    severity: str | None = None
    summary: str | None = None
    description: str | None = None
    cve_id: str | None = None
    ghsa_id: str | None = None
    vulnerable_version_range: str | None = None
    first_patched_version: str | None = None
    alert_html_url: str | None = None
    source_fingerprint: str | None = None
    review_group_key: str | None = None
    needs_review: bool = True
    review_reason: str | None = None
    first_seen_at: datetime | None = None
    last_seen_open_at: datetime | None = None
    last_state_change_at: datetime | None = None
    last_synced_at: datetime | None = None
    last_researched_at: datetime | None = None
    latest_research_json: dict | None = None
    slack_channel_id: str | None = None
    slack_message_ts: str | None = None
    slack_notified_at: datetime | None = None
    reminder_count: int = 0
    resolved_at: datetime | None = None
    raw_alert_json: dict | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class DependabotRiskAssessment(BaseModel):
    alert_id: str
    package: str
    ecosystem: str
    severity: Literal["critical", "high", "medium", "low"]
    current_version: str | None = None
    suggested_version: str | None = None
    cve_summary: str
    usage_in_codebase: str
    breaking_change_risk: Literal["low", "medium", "high", "critical"]
    breaking_change_rationale: str
    recommendation: Literal[
        "apply_immediately", "apply_with_testing", "defer", "skip"
    ]
    suggested_pr_description: str
    priority: Literal["critical", "high", "medium", "low"]
    confidence: Literal["high", "medium", "low"]
    risk_summary: str
    reasoning: str


class AlertReviewResponse(BaseModel):
    results: list[DependabotRiskAssessment]


class AlertReviewWrite(BaseModel):
    alert_id: str
    repo_full_name: str
    review_group_key: str | None = None
    review_reason: str
    model_name: str
    prompt_version: str
    recommendation: str
    priority: str
    confidence: str
    risksummary: str
    reasoning: str
    current_version: str | None = None
    suggested_version: str | None = None
    cve_summary: str | None = None
    usage_in_codebase: str | None = None
    breaking_change_risk: str | None = None
    breaking_change_rationale: str | None = None
    suggested_pr_description: str | None = None
    research_json: dict
    assessment_json: dict


class AlertGroup(BaseModel):
    repo_full_name: str
    package_name: str
    ecosystem: str
    severity: str | None
    summary: str | None
    description: str | None
    cve_id: str | None
    ghsa_id: str | None
    vulnerable_version_range: str | None
    first_patched_version: str | None
    review_group_key: str | None
    review_reason: str | None
    # Per-manifest members of the group
    manifest_paths: list[str]
    alert_ids: list[str]
    alert_numbers: list[int]
