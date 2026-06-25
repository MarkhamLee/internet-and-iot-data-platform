# (C) Markham Lee 2023 - 2026
# https://github.com/MarkhamLee/internet-and-iot-data-platform
# Core agent logic for the Dependabot review pipeline.
# Handles LLM review, Slack notifications, and run instrumentation.
# Instantiated and called by main.py.
import uuid
from datetime import datetime, timezone
from time import perf_counter
from schemas import AlertGroup, AlertReviewResponse, AlertReviewWrite
from postgres_review_repository import PostgresReviewRepository
from qwen_client import QwenClient
from slack_message_builder import (
    build_report_blocks,
    build_reminder_blocks,
    build_slack_payload,
)
from agent_library.agent_utilities import (
    send_slack_webhook_block,
    write_instrumentation,
)
from agent_library.logging_util import console_logging

logger = console_logging("Dependabot agent")

AGENT_RUNS_TABLE = "agent_runs"


def build_group_payload(group: AlertGroup) -> dict:
    return {
        "task": "review_dependabot_alert_group",
        "group": {
            "repo_full_name": group.repo_full_name,
            "package_name": group.package_name,
            "ecosystem": group.ecosystem,
            "severity": group.severity,
            "summary": group.summary,
            "description": group.description,
            "cve_id": group.cve_id,
            "ghsa_id": group.ghsa_id,
            "vulnerable_version_range": group.vulnerable_version_range,
            "first_patched_version": group.first_patched_version,
            "review_reason": group.review_reason,
            "manifests": [
                {"alert_id": alert_id, "manifest_path": path}
                for alert_id, path in zip(group.alert_ids,
                                          group.manifest_paths)
            ],
        },
    }


class DependabotAgent:
    def __init__(
        self,
        *,
        qwen_client: QwenClient,
        slack_webhook_url: str,
        pg_kwargs: dict,
        review_prompt: str,
        prompt_version: str,
        review_limit: int,
        reminder_interval_hours: int,
    ):
        self.qwen_client = qwen_client
        self.slack_webhook_url = slack_webhook_url
        self.pg_kwargs = pg_kwargs
        self.review_prompt = review_prompt
        self.prompt_version = prompt_version
        self.review_limit = review_limit
        self.reminder_interval_hours = reminder_interval_hours

    def _repo(self) -> PostgresReviewRepository:
        """Open a fresh repository connection."""
        return PostgresReviewRepository(**self.pg_kwargs)

    # ------------------------------------------------------------------
    # Phase 1: LLM review
    # ------------------------------------------------------------------

    def run_review_phase(self) -> dict:
        """Fetch alert groups needing review, call the LLM, persist results."""
        alerts_reviewed = 0
        failed_groups = 0
        llm_durations: list[float] = []
        repos: list[str] = []
        groups_fetched = 0
        alerts_fetched = 0
        errors: list[str] = []

        with self._repo() as repository:
            groups = repository.fetch_alert_groups_needing_review(
                limit=self.review_limit,
            )

        groups_fetched = len(groups)

        if not groups:
            logger.info("No alert groups require review")
            return {
                "groups_fetched": 0,
                "alerts_fetched": 0,
                "alerts_reviewed": 0,
                "failed_groups": 0,
                "repos": [],
                "llm_durations": [],
                "errors": [],
            }

        alerts_fetched = sum(len(g.alert_ids) for g in groups)
        repos = sorted({g.repo_full_name for g in groups})
        logger.info(
            "Reviewing %s alert groups covering %s alerts across repos: %s",
            groups_fetched,
            alerts_fetched,
            ", ".join(repos),
        )

        for group in groups:
            try:
                logger.info(
                    "Reviewing group repo=%s package=%s ecosystem=%s manifest_count=%s",  # noqa: E501
                    group.repo_full_name,
                    group.package_name,
                    group.ecosystem,
                    len(group.manifest_paths),
                )

                payload = build_group_payload(group)

                llm_start = perf_counter()
                response: AlertReviewResponse = (
                    self.qwen_client.generate_structured_response(
                        prompt=self.review_prompt,
                        payload=payload,
                        response_model=AlertReviewResponse,
                    )
                )
                llm_durations.append(perf_counter() - llm_start)

                logger.info(
                    "Qwen response received package=%s result_count=%s",
                    group.package_name,
                    len(response.results),
                )

                if len(response.results) != len(group.manifest_paths):
                    raise RuntimeError(
                        f"Result count mismatch for package={group.package_name}. "  # noqa: E501
                        f"expected={len(group.manifest_paths)} got={len(response.results)}"  # noqa: E501
                    )

                for review in response.results:
                    alert_id = group.alert_id_for_path(review.manifest_path)

                    if alert_id is None:
                        raise RuntimeError(
                            f"Unrecognised manifest_path={review.manifest_path} "  # noqa: E501
                            f"in response for package={group.package_name}"
                        )

                    if review.alert_id != alert_id:
                        logger.debug(
                            "Qwen response dump for mismatch package=%s: %s",
                            group.package_name,
                            response.model_dump(mode="json"),
                        )
                        raise RuntimeError(
                            f"Review alert_id mismatch for manifest_path={review.manifest_path}. "  # noqa: E501
                            f"expected={alert_id} got={review.alert_id}"
                        )

                    review_write = AlertReviewWrite(
                        alert_id=alert_id,
                        repo_full_name=group.repo_full_name,
                        review_group_key=group.review_group_key,
                        review_reason=group.review_reason or "manual_recheck",
                        model_name=self.qwen_client.model,
                        prompt_version=self.prompt_version,
                        recommendation=review.recommendation,
                        priority=review.priority,
                        confidence=review.confidence,
                        risksummary=review.risk_summary,
                        reasoning=review.reasoning,
                        current_version=review.current_version,
                        suggested_version=review.suggested_version,
                        cve_summary=review.cve_summary,
                        usage_in_codebase=review.usage_in_codebase,
                        breaking_change_risk=review.breaking_change_risk,
                        breaking_change_rationale=review.
                        breaking_change_rationale,
                        suggested_pr_description=review.
                        suggested_pr_description,
                        research_json=group.model_dump(mode="json"),
                        assessment_json=review.model_dump(mode="json"),
                    )

                    with self._repo() as repository:
                        repository.save_review_result(
                            review=review_write,
                            latest_research_json={
                                "model_name": self.qwen_client.model,
                                "prompt_version": self.prompt_version,
                                "review": review.model_dump(mode="json"),
                            },
                        )

                    alerts_reviewed += 1
                    logger.info(
                        "Completed review alert_id=%s repo=%s manifest_path=%s",  # noqa: E501
                        alert_id,
                        group.repo_full_name,
                        review.manifest_path,
                    )

            except Exception as exc:
                failed_groups += 1
                error = (
                    f"review group repo={group.repo_full_name} "
                    f"package={group.package_name} ecosystem={group.ecosystem}: {exc}"  # noqa: E501
                )
                errors.append(error)
                logger.exception("Failed to %s", error)
                continue

        return {
            "groups_fetched": groups_fetched,
            "alerts_fetched": alerts_fetched,
            "alerts_reviewed": alerts_reviewed,
            "failed_groups": failed_groups,
            "repos": repos,
            "llm_durations": llm_durations,
            "errors": errors,
        }

    # ------------------------------------------------------------------
    # Phase 2: Slack notifications
    # ------------------------------------------------------------------

    def run_notification_phase(self) -> dict:
        """Send Slack messages for new alerts and
        rich reminders for pending ones."""

        slack_sent = 0
        slack_failed = 0
        errors: list[str] = []

        with self._repo() as repository:
            alerts_to_notify = repository.fetch_alerts_needing_slack_notification(  # noqa: E501
                reminder_interval_hours=self.reminder_interval_hours,)

        if not alerts_to_notify:
            logger.info("No Slack notifications to send")
            return {"slack_sent": 0, "slack_failed": 0, "errors": []}

        logger.info(
            "Sending Slack notifications for %s alerts", len(alerts_to_notify)
        )

        now = datetime.now(tz=timezone.utc)

        for alert in alerts_to_notify:
            try:
                is_reminder = alert.slack_notified_at is not None

                with self._repo() as repository:
                    assessment = repository.\
                        fetch_latest_assessment(alert.alert_id)

                if assessment is None:
                    logger.warning(
                        "No assessment found for alert_id=%s, skipping",
                        alert.alert_id,
                    )
                    continue

                if is_reminder:
                    reminder_count = (alert.reminder_count or 0) + 1
                    blocks = build_reminder_blocks(
                        assessment, reminder_count=reminder_count
                    )
                    fallback = (
                        f"Reminder #{reminder_count} — {alert.package_name} "
                        f"({alert.ecosystem}) upgrade still pending\n"
                        f"Repo: {alert.repo_full_name} | "
                        f"File: {alert.manifest_path}\n"
                        f"Recommendation: {assessment.recommendation} | "
                        f"Risk: {assessment.risk_summary}"
                    )
                else:
                    blocks = build_report_blocks(
                        assessment,
                        repo=alert.repo_full_name,
                        cve_id=alert.cve_id,
                    )
                    fallback = (
                        f"New Dependabot alert: {alert.package_name} "
                        f"[{alert.severity}] in {alert.repo_full_name}"
                    )

                payload = build_slack_payload(blocks, fallback_text=fallback)
                status_code = send_slack_webhook_block(
                    self.slack_webhook_url, payload
                )

                if status_code == 200:
                    slack_sent += 1
                    with self._repo() as repository:
                        repository.mark_alert_slack_notified(
                            alert_id=alert.alert_id,
                            is_reminder=is_reminder,
                            notified_at=now,
                        )
                else:
                    slack_failed += 1
                    error = (
                        f"slack notification alert_id={alert.alert_id} "
                        f"status={status_code}"
                    )
                    errors.append(error)
                    logger.warning(
                        "Slack notification failed alert_id=%s status=%s",
                        alert.alert_id,
                        status_code,
                    )

            except Exception as exc:
                slack_failed += 1
                error = f"slack notification alert_id={alert.alert_id}: {exc}"
                errors.append(error)
                logger.exception("Unexpected error sending %s", error)
                continue

        return {"slack_sent": slack_sent,
                "slack_failed": slack_failed,
                "errors": errors}

    # ------------------------------------------------------------------
    # Phase 3: Instrumentation
    # ------------------------------------------------------------------

    def write_run_instrumentation(
        self,
        *,
        run_id: uuid.UUID,
        started_at: datetime,
        review_stats: dict,
        notification_stats: dict,
    ) -> None:
        """Persist a run summary row to the agent_runs table."""
        completed_at = datetime.now(tz=timezone.utc)
        all_errors = review_stats["errors"] + notification_stats["errors"]
        status = "success" if not all_errors else "partial"

        llm_durations = review_stats["llm_durations"]
        avg_llm = (
            round(sum(llm_durations) / len(llm_durations), 2)
            if llm_durations
            else None
        )

        run_payload = {
            "run_id": run_id,
            "started_at": started_at,
            "completed_at": completed_at,
            "duration_seconds": round(
                (completed_at - started_at).total_seconds(), 2
            ),
            "repos": review_stats["repos"],
            "repo_count": len(review_stats["repos"]),
            "groups_fetched": review_stats["groups_fetched"],
            "alerts_fetched": review_stats["alerts_fetched"],
            "alerts_reviewed": review_stats["alerts_reviewed"],
            "failed_groups": review_stats["failed_groups"],
            "slack_sent": notification_stats["slack_sent"],
            "slack_failed": notification_stats["slack_failed"],
            "avg_llm_seconds": avg_llm,
            "model_name": self.qwen_client.model,
            "prompt_version": self.prompt_version,
            "status": status,
            "error_message": all_errors if all_errors else None,
        }

        with self._repo() as repository:
            write_instrumentation(
                conn=repository.conn,
                table=AGENT_RUNS_TABLE,
                payload=run_payload,
            )

        logger.info(
            "Run complete run_id=%s status=%s duration=%ss errors=%s",
            run_id,
            status,
            run_payload["duration_seconds"],
            len(all_errors),
        )

    # ------------------------------------------------------------------
    # Entrypoint
    # ------------------------------------------------------------------

    def run(self) -> None:
        run_id = uuid.uuid4()
        started_at = datetime.now(tz=timezone.utc)

        start = perf_counter()
        review_stats = self.run_review_phase()
        logger.info(
            "Review phase complete reviewed=%s failed_groups=%s duration=%ss",
            review_stats["alerts_reviewed"],
            review_stats["failed_groups"],
            round(perf_counter() - start, 2),
        )

        notification_stats = self.run_notification_phase()

        try:
            self.write_run_instrumentation(
                run_id=run_id,
                started_at=started_at,
                review_stats=review_stats,
                notification_stats=notification_stats,
            )
        except Exception as exc:
            logger.exception("Failed to write run instrumentation: %s", exc)
