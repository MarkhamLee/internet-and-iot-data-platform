# (C) Markham Lee 2023 - 2026
# https://github.com/MarkhamLee/internet-and-iot-data-platform
# Schemas for the site monitor agent pipeline
from __future__ import annotations
from datetime import datetime
from typing import Literal
from pydantic import BaseModel, StrictBool, model_validator

PageStatus = Literal["desired", "undesired", "unknown"]
Confidence = Literal["high", "medium", "low"]
RecommendedAction = Literal["alert", "monitor", "no_action"]


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
    max_attempts: int = 5
    last_error: str | None = None
    errors: list[dict] | None = None
    payload: dict
    result_reviewed_at: datetime | None = None
    result_page_status: str | None = None
    result_event_type: str | None = None


class AssessmentFields(BaseModel):
    desired_state_found: StrictBool
    confidence: Confidence
    summary: str
    reasoning: str
    recommended_action: RecommendedAction
    result_page_status: PageStatus
    result_event_type: str | None = None

    @model_validator(mode="after")
    def consistent_state(self):
        if self.desired_state_found != (self.result_page_status == "desired"):
            raise ValueError("desired_state_found must be true exactly when status is desired")  # noqa: E501
        return self


class PageAnalysisResponse(AssessmentFields):
    """Validated model output; unknown means insufficient evidence,
    not negative evidence."""


class PageAnalysisWrite(AssessmentFields):
    queue_id: int
    page_key: str
    url: str
    model_name: str
    alert_sent: bool = False


class ResearchCompletion(BaseModel):
    """Committed state transition and
    application-owned notification decision."""
    previous_status: PageStatus
    current_status: PageStatus
    state_changed: bool
    should_alert: bool
    event_type: Literal[
        "desired_state_confirmed", "became_desired", "became_undesired",
        "state_unknown", "state_unchanged", "state_confirmed_undesired",
    ]
    suppression_reason: str | None = None


def decide_initial_alert(
    previous_status: PageStatus, current_status: PageStatus, *,
    send_missed_it_message: bool,
) -> ResearchCompletion:
    """
    Pure policy; the caller must supply the state
    locked inside completion.
    """

    if previous_status not in {"desired", "undesired", "unknown"}:
        raise ValueError("Invalid previous page status")
    if current_status not in {"desired", "undesired", "unknown"}:
        raise ValueError("Invalid current page status")
    if type(send_missed_it_message) is not bool:
        raise ValueError("send_missed_it_message must be a bool")
    changed = previous_status != current_status
    if not changed:
        alert, event, reason = False, "state_unchanged", "same_state"
    elif current_status == "desired":
        alert = True
        event = "desired_state_confirmed" if previous_status ==\
            "unknown" else "became_desired"
        reason = None
    elif current_status == "unknown":
        alert, event, reason = False, "state_unknown", "insufficient_evidence"
    elif previous_status == "desired":
        alert, event = send_missed_it_message, "became_undesired"
        reason = None if alert else "missed_it_disabled"
    else:
        alert, event, reason = False, "state_confirmed_undesired", "desired_state_not_found"  # noqa: E501
    return ResearchCompletion(
        previous_status=previous_status, current_status=current_status,
        state_changed=changed, should_alert=alert, event_type=event,
        suppression_reason=reason,
    )
