from __future__ import annotations

from datetime import datetime

from schemas import PageReviewResult
from state_store import StateStore
from research_queue_store import ResearchQueueStore


class ResearchCompletionStore:
    def __init__(self, dsn: str):
        self.state_store = StateStore(dsn)
        self.queue_store = ResearchQueueStore(dsn)

    def complete_review(
        self,
        *,
        queue_id: int,
        page_key: str,
        url: str,
        review: PageReviewResult,
        observed_at: datetime,
        event_type: str,
        slack_sent: bool,
        send_time: datetime | None,
        http_etag: str | None,
        http_last_modified: str | None,
        content_hash: str | None,
        llm_invoked: bool,
        pipeline_name: str = "site_monitor_research",
        pending_reconfirmation: bool | None = None,
    ) -> None:
        previous = self.state_store.get_current_state(page_key)
        self.state_store.save_research_result(
            queue_id=queue_id,
            page_key=page_key,
            url=url,
            review=review,
            observed_at=observed_at,
            event_type=event_type,
            slack_sent=slack_sent,
            send_time=send_time,
            previous=previous,
            http_etag=http_etag,
            http_last_modified=http_last_modified,
            content_hash=content_hash,
            llm_invoked=llm_invoked,
            pipeline_name=pipeline_name,
            pending_reconfirmation=pending_reconfirmation,
        )
        self.queue_store.mark_completed(
            queue_id=queue_id,
            reviewed_at=observed_at,
            page_status=review.page_status,
            event_type=event_type,
        )
