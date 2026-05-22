# (C) Markham Lee 2023 - 2026
# https://github.com/MarkhamLee/internet-and-iot-data-platform
# Schemas for the site monitor agent pipeline
from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class ResearchQueueItem(BaseModel):
    id: int
    page_key: str
    url: str
    requested_at: datetime
    available_at: datetime | None = None
    claimed_at: datetime | None = None
    completed_at: datetime | None = None
    status: str
    request_reason: str
    priority: int = 0
    content_hash: str
    final_url: str | None = None
    http_etag: str | None = None
    http_last_modified: str | None = None
    pending_reconfirmation: bool = False
    attempt_count: int = 0
    max_attempts: int = 3
    last_error: str | None = None
    errors: dict | None = None
    payload: dict
    result_reviewed_at: datetime | None = None
    result_page_status: str | None = None
    result_event_type: str | None = None


class PageAnalysisResponse(BaseModel):
    """Structured LLM output model."""
    desired_state_found: bool
    confidence: Literal["high", "medium", "low"]
    summary: str
    reasoning: str
    recommended_action: Literal["alert", "monitor", "no_action"]
    result_page_status: str
    result_event_type: str | None = None


class PageAnalysisWrite(BaseModel):
    """Write model for persisting LLM results back to the queue."""
    queue_id: int
    page_key: str
    url: str
    desired_state_found: bool
    confidence: str
    summary: str
    reasoning: str
    recommended_action: str
    result_page_status: str
    result_event_type: str | None
    model_name: str
    alert_sent: bool = False
