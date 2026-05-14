from __future__ import annotations

from datetime import datetime, timedelta


def should_invoke_llm(
    previous,
    content_hash: str,
    now: datetime,
    force_review_after_hours: int | None = None,
) -> tuple[bool, str]:
    if previous is None:
        return True, "first_observation"

    if previous.current_status == "unknown":
        return True, "previous_unknown"

    if previous.last_llm_reviewed_hash != content_hash:
        return True, "content_changed"

    if force_review_after_hours is not None:
        last_review_at = getattr(previous, "last_checked_at", None)
        if last_review_at and now - last_review_at >=\
                timedelta(hours=force_review_after_hours):
            return True, "forced_refresh"

    return False, "content_unchanged"


def determine_event_type(
    previous,
    current,
    now: datetime,
    reminder_interval_minutes: int,
) -> tuple[str, bool]:
    if previous is None:
        return ("became_desired", True) if current.\
            page_status == "desired" else ("no_change", False)

    if previous.current_status != current.page_status:
        if previous.current_status == "undesired" and current.\
                 page_status == "desired":
            return "became_desired", True
        if previous.current_status == "desired" and current.\
                page_status == "undesired":
            return "missed_it", True
        if previous.current_status == "unknown" and current.\
                page_status == "desired":
            return "became_desired", True
        if previous.current_status == "unknown" and current.\
                page_status == "undesired":
            return "became_undesired", True
        return "state_changed", True

    if current.page_status == "desired":
        if (
            previous.last_reminder_sent_at is None
            or now - previous.
                last_reminder_sent_at >= timedelta
                (minutes=reminder_interval_minutes)
        ):
            return "desired_reminder", True

    return "no_change", False
