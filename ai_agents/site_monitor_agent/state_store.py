# (C) Markham Lee 2023 - 2026
# https://github.com/MarkhamLee/internet-and-iot-data-platform
# Stores output of page comparisons in Postgres
from __future__ import annotations
import psycopg
from datetime import datetime
from psycopg.rows import dict_row
from typing import Any
from schemas import PageReviewResult, TrackedPageState


class StateStore:
    def __init__(self, dsn: str):
        self.dsn = dsn

    def get_current_state(self, page_key: str) -> TrackedPageState | None:
        sql = """
        select
            page_key,
            url,
            current_status,
            first_seen_at,
            last_checked_at,
            state_changed_at,
            desired_state_started_at,
            undesired_state_started_at,
            last_reminder_sent_at,
            last_slack_message_type,
            last_review_summary,
            last_state_key
        from page_watch_current
        where page_key = %s
        """

        with psycopg.connect(self.dsn,
                             autocommit=True,
                             row_factory=dict_row) as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (page_key,))
                row = cur.fetchone()
                if row is None:
                    return None

                return TrackedPageState(**row)

    def upsert_current_state(
        self,
        page_key: str,
        url: str,
        review: PageReviewResult,
        now: datetime,
        event_type: str,
        send_time: datetime | None,
        previous: TrackedPageState | None,
    ) -> None:
        desired_started_at = self._desired_started_at(
            previous=previous,
            current_status=review.page_status,
            now=now,
        )
        undesired_started_at = self._undesired_started_at(
            previous=previous,
            current_status=review.page_status,
            now=now,
        )
        state_changed_at = self._state_changed_at(
            previous=previous,
            current_status=review.page_status,
            now=now,
        )

        last_reminder_sent_at = (
            send_time
            if send_time is not None
            else previous.last_reminder_sent_at if previous else None
        )

        sql = """
        insert into page_watch_current (
            page_key,
            url,
            current_status,
            first_seen_at,
            last_checked_at,
            state_changed_at,
            desired_state_started_at,
            undesired_state_started_at,
            last_reminder_sent_at,
            last_slack_message_type,
            last_review_summary,
            last_state_key
        )
        values (
            %(page_key)s,
            %(url)s,
            %(current_status)s,
            %(first_seen_at)s,
            %(last_checked_at)s,
            %(state_changed_at)s,
            %(desired_state_started_at)s,
            %(undesired_state_started_at)s,
            %(last_reminder_sent_at)s,
            %(last_slack_message_type)s,
            %(last_review_summary)s,
            %(last_state_key)s
        )
        on conflict (page_key) do update set
            url = excluded.url,
            current_status = excluded.current_status,
            last_checked_at = excluded.last_checked_at,
            state_changed_at = excluded.state_changed_at,
            desired_state_started_at = excluded.desired_state_started_at,
            undesired_state_started_at = excluded.undesired_state_started_at,
            last_reminder_sent_at = excluded.last_reminder_sent_at,
            last_slack_message_type = excluded.last_slack_message_type,
            last_review_summary = excluded.last_review_summary,
            last_state_key = excluded.last_state_key
        """

        payload: dict[str, Any] = {
            "page_key": page_key,
            "url": url,
            "current_status": review.page_status,
            "first_seen_at": previous.first_seen_at if previous else now,
            "last_checked_at": now,
            "state_changed_at": state_changed_at,
            "desired_state_started_at": desired_started_at,
            "undesired_state_started_at": undesired_started_at,
            "last_reminder_sent_at": last_reminder_sent_at,
            "last_slack_message_type": event_type,
            "last_review_summary": review.summary,
            "last_state_key": review.normalized_state_key,
        }

        with psycopg.connect(self.dsn, autocommit=True) as conn:
            with conn.transaction():
                with conn.cursor() as cur:
                    cur.execute(sql, payload)

    def insert_event(
        self,
        page_key: str,
        url: str,
        review: PageReviewResult,
        now: datetime,
        event_type: str,
        slack_sent: bool,
    ) -> None:
        sql = """
        insert into page_watch_event (
            page_key,
            url,
            observed_at,
            event_type,
            page_status,
            confidence,
            summary,
            evidence,
            extracted_price,
            extracted_title,
            normalized_state_key,
            slack_sent
        )
        values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        with psycopg.connect(self.dsn, autocommit=True) as conn:
            with conn.transaction():
                with conn.cursor() as cur:
                    cur.execute(
                        sql,
                        (
                            page_key,
                            url,
                            now,
                            event_type,
                            review.page_status,
                            review.confidence,
                            review.summary,
                            review.evidence,
                            review.extracted_price,
                            review.extracted_title,
                            review.normalized_state_key,
                            slack_sent,
                        ),
                    )

    def save_result(
        self,
        page_key: str,
        url: str,
        review: PageReviewResult,
        now: datetime,
        event_type: str,
        slack_sent: bool,
        send_time: datetime | None,
        previous: TrackedPageState | None,
    ) -> None:
        desired_started_at = self._desired_started_at(
            previous=previous,
            current_status=review.page_status,
            now=now,
        )
        undesired_started_at = self._undesired_started_at(
            previous=previous,
            current_status=review.page_status,
            now=now,
        )
        state_changed_at = self._state_changed_at(
            previous=previous,
            current_status=review.page_status,
            now=now,
        )
        last_reminder_sent_at = (
            send_time
            if send_time is not None
            else previous.last_reminder_sent_at if previous else None
        )

        upsert_sql = """
        insert into page_watch_current (
            page_key,
            url,
            current_status,
            first_seen_at,
            last_checked_at,
            state_changed_at,
            desired_state_started_at,
            undesired_state_started_at,
            last_reminder_sent_at,
            last_slack_message_type,
            last_review_summary,
            last_state_key
        )
        values (
            %(page_key)s,
            %(url)s,
            %(current_status)s,
            %(first_seen_at)s,
            %(last_checked_at)s,
            %(state_changed_at)s,
            %(desired_state_started_at)s,
            %(undesired_state_started_at)s,
            %(last_reminder_sent_at)s,
            %(last_slack_message_type)s,
            %(last_review_summary)s,
            %(last_state_key)s
        )
        on conflict (page_key) do update set
            url = excluded.url,
            current_status = excluded.current_status,
            last_checked_at = excluded.last_checked_at,
            state_changed_at = excluded.state_changed_at,
            desired_state_started_at = excluded.desired_state_started_at,
            undesired_state_started_at = excluded.undesired_state_started_at,
            last_reminder_sent_at = excluded.last_reminder_sent_at,
            last_slack_message_type = excluded.last_slack_message_type,
            last_review_summary = excluded.last_review_summary,
            last_state_key = excluded.last_state_key
        """

        event_sql = """
        insert into page_watch_event (
            page_key,
            url,
            observed_at,
            event_type,
            page_status,
            confidence,
            summary,
            evidence,
            extracted_price,
            extracted_title,
            normalized_state_key,
            slack_sent
        )
        values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        upsert_payload: dict[str, Any] = {
            "page_key": page_key,
            "url": url,
            "current_status": review.page_status,
            "first_seen_at": previous.first_seen_at if previous else now,
            "last_checked_at": now,
            "state_changed_at": state_changed_at,
            "desired_state_started_at": desired_started_at,
            "undesired_state_started_at": undesired_started_at,
            "last_reminder_sent_at": last_reminder_sent_at,
            "last_slack_message_type": event_type,
            "last_review_summary": review.summary,
            "last_state_key": review.normalized_state_key,
        }

        event_params = (
            page_key,
            url,
            now,
            event_type,
            review.page_status,
            review.confidence,
            review.summary,
            review.evidence,
            review.extracted_price,
            review.extracted_title,
            review.normalized_state_key,
            slack_sent,
        )

        with psycopg.connect(self.dsn, autocommit=True) as conn:
            with conn.transaction():
                with conn.cursor() as cur:
                    cur.execute(upsert_sql, upsert_payload)
                    cur.execute(event_sql, event_params)

    @staticmethod
    def _desired_started_at(
        previous: TrackedPageState | None,
        current_status: str,
        now: datetime,
    ) -> datetime | None:
        if current_status != "desired":
            return None

        if previous and previous.current_status == "desired":
            return previous.desired_state_started_at or previous.state_changed_at  # noqa: E501

        return now

    @staticmethod
    def _undesired_started_at(
        previous: TrackedPageState | None,
        current_status: str,
        now: datetime,
    ) -> datetime | None:
        if current_status != "undesired":
            return None

        if previous and previous.current_status == "undesired":
            return previous.undesired_state_started_at or previous.state_changed_at  # noqa: E501

        return now

    @staticmethod
    def _state_changed_at(
        previous: TrackedPageState | None,
        current_status: str,
        now: datetime,
    ) -> datetime:
        if previous and previous.current_status == current_status:
            return previous.state_changed_at

        return now
