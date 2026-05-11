# (C) Markham Lee 2023 - 2026
# https://github.com/MarkhamLee/internet-and-iot-data-platform
# defining schemas to better manage data quality
from datetime import datetime
from langgraph.graph.message import add_messages
from typing import List, Literal, Optional, Annotated, TypedDict
from pydantic import BaseModel, Field


class DependencyInfo(BaseModel):
    package_name: Optional[str] = None
    ecosystem: Optional[str] = None
    manifest_path: Optional[str] = None
    scope: Optional[str] = None
    relationship: Optional[str] = None


class NormalizedAlert(BaseModel):
    alert_number: int
    state: str
    dependency: DependencyInfo
    severity: Optional[str] = None
    summary: Optional[str] = None
    description: Optional[str] = None
    cve_id: Optional[str] = None
    ghsa_id: Optional[str] = None
    vulnerable_version_range: Optional[str] = None
    first_patched_version: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    html_url: Optional[str] = None


class ReviewResult(BaseModel):
    alert_number: int
    priority: Literal["critical", "high", "medium", "low"]
    risk_summary: str
    recommended_action: str
    reasoning: str
    confidence: Literal["high", "medium", "low"]


class ReviewResponse(BaseModel):
    results: List[ReviewResult] = Field(default_factory=list)


class SimpleQuestionResponse(BaseModel):
    answer: str


class DependabotRiskAssessment(BaseModel):
    package: str
    ecosystem: str
    current_version: str
    suggested_version: str
    severity: Literal["critical", "high", "medium", "low"]
    cve_summary: str
    breaking_change_risk: Literal["low", "medium", "high"]
    breaking_change_rationale: str
    usage_in_codebase: str
    recommendation: Literal["apply_immediately", "apply_with_testing", "defer", "skip"]
    suggested_pr_description: str

class AlertAgentState(TypedDict):
    messages: Annotated[list, add_messages]
    alert_id: str
    repo: str
    alert_data: dict                          # raw GitHub API response
    code_context: str                         # relevant code from repo
    registry_data: dict                       # PyPI/npm research results
    assessment: DependabotRiskAssessment | None
    last_researched_at: datetime | None
    slack_message_ts: str | None
    skip_research: bool