from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field, HttpUrl

DesiredState = Literal["desired", "undesired", "unknown"]
QueueStatus = Literal["pending",
                      "in_progress",
                      "completed",
                      "failed",
                      "cancelled"]
RunStatus = Literal["running", "completed", "completed_with_errors", "failed"]


class TrackedPageState(BaseModel):
    page_key: str
    url: HttpUrl
    current_status: DesiredState
    first_seen_at: datetime
    last_checked_at: datetime
    state_changed_at: datetime
    desired_state_started_at: datetime | None = None
    undesired_state_started_at: datetime | None = None
    last_reminder_sent_at: datetime | None = None
    last_slack_message_type: str | None = None
    last_review_summary: str | None = None
    last_state_key: str | None = None
    last_http_etag: str | None = None
    last_http_last_modified: str | None = None
    last_content_hash: str | None = None
    last_llm_reviewed_hash: str | None = None
    research_needed: bool = False
    research_requested_at: datetime | None = None
    pending_reconfirmation: bool = False
    pending_content_hash: str | None = None
    pending_final_url: str | None = None
    pending_http_etag: str | None = None
    pending_http_last_modified: str | None = None
    last_research_completed_at: datetime | None = None
    last_research_queue_id: int | None = None


class ResearchQueueItem(BaseModel):
    id: int
    page_key: str
    url: str
    requested_at: datetime
    available_at: datetime
    claimed_at: datetime | None = None
    completed_at: datetime | None = None
    status: QueueStatus
    request_reason: str
    priority: int = 100
    content_hash: str | None = None
    final_url: str | None = None
    http_etag: str | None = None
    http_last_modified: str | None = None
    pending_reconfirmation: bool = False
    attempt_count: int = 0
    max_attempts: int = 5
    last_error: str | None = None
    errors: list[dict[str, Any]] = Field(default_factory=list)
    payload: dict[str, Any] = Field(default_factory=dict)
    result_reviewed_at: datetime | None = None
    result_page_status: str | None = None
    result_event_type: str | None = None


class PageReviewResult(BaseModel):
    page_status: DesiredState
    confidence: float
    summary: str
    evidence: list[str] = Field(default_factory=list)
    extracted_price: str | None = None
    extracted_title: str | None = None
    normalized_state_key: str | None = None


class CollectionPipelineResult(BaseModel):
    page_key: str
    status: str
    queued_for_research: bool = False
    reminder_sent: bool = False
    request_reason: str | None = None
    content_hash: str | None = None
    queue_id: int | None = None
