# (C) Markham Lee 2023 - 2026
# https://github.com/MarkhamLee/internet-and-iot-data-platform
# Data schemas for site monitoring agent
from __future__ import annotations
from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, Field, HttpUrl


DesiredState = Literal["desired", "undesired", "unknown"]


class PageReviewResult(BaseModel):
    page_status: DesiredState = Field(
        description="Whether the page is currently in the desired state."
    )
    confidence: float = Field(ge=0.0, le=1.0)
    summary: str = Field(description="Short human-readable summary of the page state.")  # noqa: E501
    evidence: list[str] = Field(default_factory=list)
    extracted_price: Optional[str] = None
    extracted_title: Optional[str] = None
    normalized_state_key: Optional[str] = Field(
        default=None,
        description="Compact canonical state string, e.g. 'in_stock', 'out_of_stock'."  # noqa: E501
    )


class FetchResult(BaseModel):
    url: HttpUrl
    status_code: int
    final_url: HttpUrl
    fetched_at: datetime
    html: str
    text: str
    etag: Optional[str] = None
    last_modified: Optional[str] = None


class TrackedPageState(BaseModel):
    page_key: str
    url: HttpUrl
    current_status: DesiredState
    first_seen_at: datetime
    last_checked_at: datetime
    state_changed_at: datetime
    desired_state_started_at: Optional[datetime] = None
    undesired_state_started_at: Optional[datetime] = None
    last_reminder_sent_at: Optional[datetime] = None
    last_slack_message_type: Optional[str] = None
    last_review_summary: Optional[str] = None
    last_state_key: Optional[str] = None
