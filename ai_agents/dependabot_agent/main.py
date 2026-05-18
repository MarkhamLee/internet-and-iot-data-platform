# (C) Markham Lee 2023 - 2026
# https://github.com/MarkhamLee/internet-and-iot-data-platform
# main orchestrator for reviewing open Dependabot alerts with Qwen
import sys
import os
from os import getenv
from datetime import datetime, timezone
from schemas import AlertReviewResponse, AlertReviewWrite
from time import perf_counter
from logging_util import console_logging
from postgres_review_repository import PostgresReviewRepository
from qwen_client import QwenClient
from slack_message_builder import build_report_blocks, \
    build_reminder_blocks, build_slack_payload

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)
from agent_library.\
    agent_utilities import send_slack_webhook_block  # noqa: E402

logger = console_logging("Dependabot review orchestrator")

REVIEW_PROMPT = """
You are reviewing a single GitHub Dependabot alert for a software repository.

Your task:
- Review the alert in the payload.
- Identify the currently installed (vulnerable) version and the suggested safe
  upgrade version based on the vulnerable_version_range and
  first_patched_version.
- Assign a remediation priority: critical, high, medium, or low.
- Write a short cve_summary explaining the vulnerability in plain language.
- Describe how the package is likely used in the codebase based on its name,
  ecosystem, manifest path, scope, and relationship.
- Assess breaking_change_risk (low, medium, high, critical) and explain your
  rationale in breaking_change_rationale.
- Recommend one of: apply_immediately, apply_with_testing, defer, skip.
- Write a suggested_pr_description suitable for a pull request description.
- Write a short risk_summary in plain language.
- Explain your reasoning briefly.
- Set confidence to high, medium, or low.

Guidance:
- Consider package ecosystem, severity, manifest path, scope, relationship,
  and whether the package appears runtime-related.
- Prioritize runtime production dependencies over development-only dependencies
  when risk is otherwise similar.
- Prefer practical engineering judgment over generic security wording.
- Return exactly one result for the alert_id in the payload.
""".strip()

POSTGRES_DATABASE = os.environ['POSTGRES_DEPENDABOT_DATABASE']
POSTGRES_SECRET = os.environ['DEPENDABOT_AGENT_POSTGRES']
POSTGRES_USER_NAME = os.environ['POSTGRES_USER_DEPENDABOT']
POSTGRES_HOST = os.environ['POSTGRES_HOST_K3S']
POSTGRES_PORT = 5432
APPROVED_MODELS = {"qwen3.5:9b", "llama3.2:3b"}
REMINDER_INTERVAL_HOURS = int(getenv("REMINDER_INTERVAL_HOURS", "24"))


def get_required_env(name: str) -> str:
    value = getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def build_review_payload(alert: dict) -> dict:
    return {
        "task": "review_single_dependabot_alert",
        "alert": {
            "alert_id": alert["alert_id"],
            "alert_number": alert["alert_number"],
            "repo_full_name": alert["repo_full_name"],
            "package_name": alert["package_name"],
            "ecosystem": alert["ecosystem"],
            "manifest_path": alert.get("manifest_path"),
            "scope": alert.get("scope"),
            "relationship": alert.get("relationship"),
            "severity": alert.get("severity"),
            "summary": alert.get("summary"),
            "description": alert.get("description"),
            "cve_id": alert.get("cve_id"),
            "ghsa_id": alert.get("ghsa_id"),
            "vulnerable_version_range": alert.get("vulnerable_version_range"),
            "first_patched_version": alert.get("first_patched_version"),
            "alert_html_url": alert.get("alert_html_url"),
            "review_reason": alert.get("review_reason"),
        },
    }


def main() -> None:
    ollama_url = get_required_env("OLLAMA_BASE_URL")
    slack_webhook_url = get_required_env("DEPENDABOT_SLACK_WEBHOOK")
    qwen_model = "qwen3.5:9b"

    repo_full_name = getenv("REPO_FULL_NAME")
    prompt_version = getenv("PROMPT_VERSION", "v1")
    review_limit = int(getenv("REVIEW_LIMIT", "25"))

    qwen_client = QwenClient(
        ollama_url=ollama_url,
        model=qwen_model,
        approved_models=APPROVED_MODELS,
        timeout=(10, 180),
        temperature=0,
    )

    # Phase 1: Fetch alerts needing review
    with PostgresReviewRepository(
        db_host=POSTGRES_HOST,
        db_port=POSTGRES_PORT,
        database=POSTGRES_DATABASE,
        postgres_user=POSTGRES_USER_NAME,
        postgres_password=POSTGRES_SECRET,
    ) as repository:
        alerts = repository.fetch_alerts_needing_review(
            repo_full_name=repo_full_name,
            limit=review_limit,
        )

    if not alerts:
        logger.info("No alerts require review")
    else:
        logger.info("Reviewing %s alerts one at a time", len(alerts))

        reviewed_count = 0
        start = perf_counter()

        for alert in alerts:
            logger.info("Reviewing alert_id=%s", alert.alert_id)

            payload = build_review_payload(alert.model_dump(mode="python"))
            response = qwen_client.generate_structured_response(
                prompt=REVIEW_PROMPT,
                payload=payload,
                response_model=AlertReviewResponse,
            )

            logger.info("Qwen response received for alert_id=%s",
                        alert.alert_id)

            if len(response.results) != 1:
                raise RuntimeError(
                    f"Expected exactly one review result for alert_id={alert.alert_id}, "  # noqa: E501
                    f"got {len(response.results)}"
                )

            review = response.results[0]
            if review.alert_id != alert.alert_id:
                raise RuntimeError(
                    f"Review alert_id mismatch. expected={alert.alert_id}, "
                    f"got={review.alert_id}"
                )

            review_write = AlertReviewWrite(
                alert_id=alert.alert_id,
                repo_full_name=alert.repo_full_name,
                review_group_key=alert.review_group_key,
                review_reason=alert.review_reason or "manual_recheck",
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
                breaking_change_rationale=review.breaking_change_rationale,
                suggested_pr_description=review.suggested_pr_description,
                research_json=alert.model_dump(mode="json"),
                assessment_json=review.model_dump(mode="json"),
            )

            # Phase 2: Write review result
            with PostgresReviewRepository(
                db_host=POSTGRES_HOST,
                db_port=POSTGRES_PORT,
                database=POSTGRES_DATABASE,
                postgres_user=POSTGRES_USER_NAME,
                postgres_password=POSTGRES_SECRET,
            ) as repository:
                repository.save_review_result(
                    review=review_write,
                    latest_research_json={
                        "model_name": qwen_client.model,
                        "prompt_version": prompt_version,
                        "review": review.model_dump(mode="json"),
                    },
                )

            reviewed_count += 1
            logger.info("Completed review for alert_id=%s", alert.alert_id)

            # Optional: break here during debugging to process just one alert
            # break

        duration = round(perf_counter() - start, 2)
        logger.info(
            "Dependabot review workflow completed successfully; "
            "reviewed %s alerts in %s seconds",
            reviewed_count,
            duration,
        )

    # Phase 3: Slack notifications (new alerts + reminders)
    with PostgresReviewRepository(
        db_host=POSTGRES_HOST,
        db_port=POSTGRES_PORT,
        database=POSTGRES_DATABASE,
        postgres_user=POSTGRES_USER_NAME,
        postgres_password=POSTGRES_SECRET,
    ) as repository:
        alerts_to_notify = repository.fetch_alerts_needing_slack_notification(
            reminder_interval_hours=REMINDER_INTERVAL_HOURS,
        )

    if not alerts_to_notify:
        logger.info("No Slack notifications to send")
        return

    logger.info("Sending Slack notifications for %s alerts",
                len(alerts_to_notify))

    now = datetime.now(tz=timezone.utc)

    for alert in alerts_to_notify:
        is_reminder = alert.slack_notified_at is not None
        assessment = repository.fetch_latest_assessment(alert.alert_id)

        if assessment is None:
            logger.warning(
                "No assessment found for alert_id=%s, skipping Slack notification",  # noqa: E501
                alert.alert_id,
            )
            continue

        if is_reminder:
            reminder_count = (alert.reminder_count or 0) + 1
            blocks = build_reminder_blocks(assessment,
                                           reminder_count=reminder_count)
            fallback = f"Reminder #{reminder_count}: {alert.package_name} upgrade still pending ({alert.repo_full_name})"  # noqa: E501
        else:
            blocks = build_report_blocks(
                assessment,
                repo=alert.repo_full_name,
                cve_id=alert.cve_id,
            )
            fallback = f"New Dependabot alert: {alert.package_name} [{alert.severity}] in {alert.repo_full_name}"  # noqa: E501

        payload = build_slack_payload(blocks, fallback_text=fallback)
        status_code = send_slack_webhook_block(slack_webhook_url, payload)

        if status_code == 200:
            with PostgresReviewRepository(
                db_host=POSTGRES_HOST,
                db_port=POSTGRES_PORT,
                database=POSTGRES_DATABASE,
                postgres_user=POSTGRES_USER_NAME,
                postgres_password=POSTGRES_SECRET,
            ) as repository:
                repository.mark_alert_slack_notified(
                    alert_id=alert.alert_id,
                    is_reminder=is_reminder,
                    notified_at=now,
                )
        else:
            logger.warning(
                "Slack notification failed for alert_id=%s with status %s",
                alert.alert_id,
                status_code,
            )


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        logger.exception("Dependabot review workflow failed: %s", exc)
        sys.exit(1)
