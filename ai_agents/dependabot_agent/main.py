# (C) Markham Lee 2023 - 2026
# https://github.com/MarkhamLee/internet-and-iot-data-platform
# main orchestrator for reviewing open Dependabot alerts with Qwen
import sys
import os
import uuid
from os import getenv
from datetime import datetime, timezone
from schemas import AlertGroup, AlertReviewResponse, AlertReviewWrite
from time import perf_counter
from logging_util import console_logging
from postgres_review_repository import PostgresReviewRepository
from qwen_client import QwenClient
from slack_message_builder import (
    build_report_blocks,
    build_reminder_blocks,
    build_slack_payload,
)


parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)
from agent_library.agent_utilities import (  # noqa: E402
    send_slack_webhook_block,
    write_instrumentation,
)


logger = console_logging("Dependabot review orchestrator")


REVIEW_PROMPT = """
You are reviewing a group of GitHub Dependabot alerts for the same vulnerable
package across one or more manifest files in a repository.

Your task:
- Review the alert group in the payload.
- For EACH manifest_path in the payload, return one result containing:
  - The alert_id that corresponds to that manifest_path
  (provided in the payload).
  - The manifest_path itself.
  - Identify the currently installed (vulnerable) version and suggested safe
    upgrade version based on vulnerable_version_range and
    first_patched_version.
  - Assign a remediation priority: critical, high, medium, or low.
  - Write a short cve_summary explaining the vulnerability in plain language.
  - Describe how the package is likely used based on its manifest path, scope,
    ecosystem, and relationship.
  - Assess breaking_change_risk (low, medium, high, critical) and explain your
    rationale in breaking_change_rationale.
  - Recommend one of: apply_immediately, apply_with_testing, defer, skip.
  - Write a suggested_pr_description suitable for a pull request description.
  - Write a short risk_summary in plain language.
  - Explain your reasoning briefly.
  - Set confidence to high, medium, or low.

Guidance:
- The vulnerability details (CVE, severity, version range) are the same for all
  manifest paths — only the usage context and breaking change risk may differ
  between paths.
- Prioritize runtime production dependencies over development-only dependencies
  when risk is otherwise similar.
- Prefer practical engineering judgment over generic security wording.
- Return exactly one result per manifest_path — no more, no fewer.
""".strip()


POSTGRES_DATABASE = os.environ['POSTGRES_DEPENDABOT_DATABASE']
POSTGRES_SECRET = os.environ['DEPENDABOT_AGENT_POSTGRES']
POSTGRES_USER_NAME = os.environ['POSTGRES_USER_DEPENDABOT']
POSTGRES_HOST = os.environ['POSTGRES_HOST_K3S']
POSTGRES_PORT = 5432
APPROVED_MODELS = {"qwen3.5:9b", "llama3.2:3b"}
REMINDER_INTERVAL_HOURS = int(getenv("REMINDER_INTERVAL_HOURS", "24"))
AGENT_RUNS_TABLE = "agent_runs"


def get_required_env(name: str) -> str:
    value = getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


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


def pg_kwargs() -> dict:
    return {
        "db_host": POSTGRES_HOST,
        "db_port": POSTGRES_PORT,
        "database": POSTGRES_DATABASE,
        "postgres_user": POSTGRES_USER_NAME,
        "postgres_password": POSTGRES_SECRET,
    }


def main() -> None:
    run_id = uuid.uuid4()
    started_at = datetime.now(tz=timezone.utc)
    status = "success"
    errors: list[str] = []

    ollama_url = get_required_env("OLLAMA_BASE_URL")
    slack_webhook_url = get_required_env("DEPENDABOT_SLACK_WEBHOOK")
    qwen_model = "qwen3.5:9b"

    prompt_version = getenv("PROMPT_VERSION", "v1")
    review_limit = int(getenv("REVIEW_LIMIT", "25"))
    read_timeout = int(getenv("READ_TIMEOUT", "600"))

    qwen_client = QwenClient(
        ollama_url=ollama_url,
        model=qwen_model,
        approved_models=APPROVED_MODELS,
        timeout=(10, read_timeout),
        temperature=0,
    )

    alerts_reviewed = 0
    failed_groups = 0
    slack_sent = 0
    slack_failed = 0
    llm_durations: list[float] = []
    repos: list[str] = []
    groups_fetched = 0
    alerts_fetched = 0

    # Phase 1: Fetch alert groups needing review
    with PostgresReviewRepository(**pg_kwargs()) as repository:
        groups = repository.fetch_alert_groups_needing_review(
            limit=review_limit,
        )

    groups_fetched = len(groups)

    if not groups:
        logger.info("No alert groups require review")
    else:
        alerts_fetched = sum(len(g.alert_ids) for g in groups)
        repos = sorted({g.repo_full_name for g in groups})
        logger.info(
            "Reviewing %s alert groups covering %s alerts across repos: %s",
            groups_fetched,
            alerts_fetched,
            ", ".join(repos),
        )

        start = perf_counter()

        for group in groups:
            try:
                logger.info(
                    "Reviewing group package=%s ecosystem=%s manifest_count=%s",  # noqa: E501
                    group.package_name,
                    group.ecosystem,
                    len(group.manifest_paths),
                )

                payload = build_group_payload(group)

                llm_start = perf_counter()
                response = qwen_client.generate_structured_response(
                    prompt=REVIEW_PROMPT,
                    payload=payload,
                    response_model=AlertReviewResponse,
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
                        model_name=qwen_client.model,
                        prompt_version=prompt_version,
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
                        breaking_change_rationale=review.breaking_change_rationale,  # noqa: E501
                        suggested_pr_description=review.suggested_pr_description,  # noqa: E501
                        research_json=group.model_dump(mode="json"),
                        assessment_json=review.model_dump(mode="json"),
                    )

                    # Phase 2: Write each review result
                    with PostgresReviewRepository(**pg_kwargs()) as repository:
                        repository.save_review_result(
                            review=review_write,
                            latest_research_json={
                                "model_name": qwen_client.model,
                                "prompt_version": prompt_version,
                                "review": review.model_dump(mode="json"),
                            },
                        )

                    alerts_reviewed += 1
                    logger.info(
                        "Completed review for alert_id=%s manifest_path=%s",
                        alert_id,
                        review.manifest_path,
                    )

            except Exception as exc:
                failed_groups += 1
                status = "partial"
                error = (
                    f"review group package={group.package_name} "
                    f"ecosystem={group.ecosystem}: {exc}"
                )
                errors.append(error)
                logger.exception("Failed to %s", error)
                continue

        duration = round(perf_counter() - start, 2)
        logger.info(
            "Review phase complete; reviewed=%s failed_groups=%s duration=%ss",
            alerts_reviewed,
            failed_groups,
            duration,
        )

    # Phase 3: Slack notifications (new alerts + reminders)
    with PostgresReviewRepository(**pg_kwargs()) as repository:
        alerts_to_notify = repository.fetch_alerts_needing_slack_notification(
            reminder_interval_hours=REMINDER_INTERVAL_HOURS,
        )

    if not alerts_to_notify:
        logger.info("No Slack notifications to send")
    else:
        logger.info(
            "Sending Slack notifications for %s alerts", len(alerts_to_notify)
        )

        now = datetime.now(tz=timezone.utc)

        for alert in alerts_to_notify:
            try:
                is_reminder = alert.slack_notified_at is not None

                with PostgresReviewRepository(**pg_kwargs()) as repository:
                    assessment = repository.fetch_latest_assessment(
                        alert.alert_id
                    )

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
                        f"Reminder #{reminder_count}: {alert.package_name} "
                        f"upgrade still pending ({alert.repo_full_name})"
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
                status_code = send_slack_webhook_block(slack_webhook_url,
                                                       payload)

                if status_code == 200:
                    slack_sent += 1
                    with PostgresReviewRepository(**pg_kwargs()) as repository:
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
                    status = "partial"
                    logger.warning(
                        "Slack notification failed for alert_id=%s status=%s",
                        alert.alert_id,
                        status_code,
                    )

            except Exception as exc:
                slack_failed += 1
                status = "partial"
                error = f"slack notification alert_id={alert.alert_id}: {exc}"
                errors.append(error)
                logger.exception("Unexpected error sending %s", error)
                continue

    # Phase 4: Write run instrumentation
    completed_at = datetime.now(tz=timezone.utc)
    avg_llm = (
        round(sum(llm_durations) / len(llm_durations), 2)
        if llm_durations else None
    )
    total_duration = round((completed_at - started_at).total_seconds(), 2)

    run_payload = {
        "run_id": run_id,
        "started_at": started_at,
        "completed_at": completed_at,
        "duration_seconds": total_duration,
        "repos": repos,
        "repo_count": len(repos),
        "groups_fetched": groups_fetched,
        "alerts_fetched": alerts_fetched,
        "alerts_reviewed": alerts_reviewed,
        "failed_groups": failed_groups,
        "slack_sent": slack_sent,
        "slack_failed": slack_failed,
        "avg_llm_seconds": avg_llm,
        "model_name": qwen_model,
        "prompt_version": prompt_version,
        "status": status,
        "error_message": errors if errors else None,
    }

    try:
        with PostgresReviewRepository(**pg_kwargs()) as repository:
            write_instrumentation(
                conn=repository.conn,
                table=AGENT_RUNS_TABLE,
                payload=run_payload,
            )
        logger.info(
            "Run complete run_id=%s status=%s duration=%ss errors=%s",
            run_id,
            status,
            total_duration,
            len(errors),
        )
    except Exception as exc:
        logger.exception("Failed to write run instrumentation: %s", exc)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        logger.exception("Dependabot review workflow failed: %s", exc)
        sys.exit(1)
