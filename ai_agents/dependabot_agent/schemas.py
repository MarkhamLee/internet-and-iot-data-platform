# (C) Markham Lee 2023 - 2026
# https://github.com/MarkhamLee/internet-and-iot-data-platform
# defining schemas to better manage data quality
from datetime import datetime
from typing import Any, List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


Priority = Literal["critical", "high", "medium", "low"]
Confidence = Literal["high", "medium", "low"]
ReviewReason = Literal[
    "new_alert",
    "alert_changed",
    "stale_research",
    "manual_recheck",
]


class AlertRecord(BaseModel):
    model_config = ConfigDict(extra="ignore")

    alert_id: str
    repo_owner: str
    repo_name: str
    repo_full_name: str
    repo_html_url: Optional[str] = None
    repo_api_url: Optional[str] = None
    alert_number: int
    github_state: str
    package_name: str
    ecosystem: str
    manifest_path: Optional[str] = None
    scope: Optional[str] = None
    relationship: Optional[str] = None
    severity: Optional[str] = None
    summary: Optional[str] = None
    description: Optional[str] = None
    cve_id: Optional[str] = None
    ghsa_id: Optional[str] = None
    vulnerable_version_range: Optional[str] = None
    first_patched_version: Optional[str] = None
    alert_html_url: Optional[str] = None
    source_fingerprint: str
    review_group_key: str
    needs_review: bool = True
    review_reason: Optional[ReviewReason] = None

    first_seen_at: Optional[datetime] = None
    last_seen_open_at: Optional[datetime] = None
    last_state_change_at: Optional[datetime] = None
    last_synced_at: Optional[datetime] = None
    last_researched_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None

    latest_research_json: Optional[dict[str, Any]] = None
    slack_channel_id: Optional[str] = None
    slack_message_ts: Optional[str] = None
    reminder_count: int = 0
    raw_alert_json: dict[str, Any] = Field(default_factory=dict)

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class AlertReviewResult(BaseModel):
    alert_id: str
    alert_number: int
    priority: Priority
    risk_summary: str
    recommended_action: str
    reasoning: str
    confidence: Confidence


class AlertReviewResponse(BaseModel):
    results: List[AlertReviewResult] = Field(default_factory=list)


class AlertReviewWrite(BaseModel):
    alert_id: str
    repo_full_name: str
    review_group_key: str
    review_reason: ReviewReason
    model_name: str
    prompt_version: str
    recommendation: str
    priority: Priority
    confidence: Confidence
    risksummary: str
    reasoning: str
    research_json: dict[str, Any] = Field(default_factory=dict)
    assessment_json: dict[str, Any] = Field(default_factory=dict)


class SimpleQuestionResponse(BaseModel):
    answer: str
