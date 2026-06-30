# (C) Markham Lee 2023 - 2026
# Internet and IoT Data Platform
# https://github.com/MarkhamLee/internet-and-iot-data-platform
from schemas import StoredRiskAssessment


RISK_EMOJI = {
    "low": "🟢",
    "medium": "🟡",
    "high": "🔴",
    "critical": "🔴",
}

REC_EMOJI = {
    "apply_immediately": "⚡ Apply Immediately",
    "apply_with_testing": "🧪 Apply with Testing",
    "defer": "⏳ Defer",
    "skip": "⛔ Skip",
}


def build_report_blocks(
    a: StoredRiskAssessment
) -> list:
    severity = (a.severity or "").upper() or "UNKNOWN"
    risk_label = RISK_EMOJI.\
        get(a.breaking_change_risk, "⚪") + f" {a.breaking_change_risk}"
    rec_label = REC_EMOJI.get(a.recommendation, f"ℹ️ {a.recommendation}")
    current_version = a.current_version or "unknown"
    suggested_version = a.suggested_version or "unknown"

    return [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"🔒 {severity}: {a.package} ({a.repo_full_name})",
            },
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*Package:* `{a.package}` ({a.ecosystem})",
                },
                {
                    "type": "mrkdwn",
                    "text": f"*CVE:* {a.cve_id or 'N/A'}",
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Upgrade:* `{current_version}` → `{suggested_version}`",  # noqa: E501
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Breaking Risk:* {risk_label}",
                },
            ],
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*CVE Summary:*\n{a.cve_summary}",
            },
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*How it's used in the codebase:*\n{a.usage_in_codebase}",  # noqa: E501
            },
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Breaking change rationale:*\n{a.breaking_change_rationale}",  # noqa: E501
            },
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Recommendation:* {rec_label}",
            },
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                # Use a code fence instead of rich_text_preformatted
                "text": f"*Suggested PR description:*\n```{a.suggested_pr_description}```",  # noqa: E501
            },
        },
    ]


def build_reminder_blocks(
    a: StoredRiskAssessment,
    reminder_count: int,
) -> list:
    rec_label = REC_EMOJI.get(a.recommendation, f"ℹ️ {a.recommendation}")
    risk_label = RISK_EMOJI.get(a.breaking_change_risk, "⚪") + f" {a.breaking_change_risk}"  # noqa: E501
    severity = (a.severity or "").upper() or "UNKNOWN"
    current_version = a.current_version or "unknown"
    suggested_version = a.suggested_version or "unknown"
    manifest = a.manifest_path or "unknown"

    return [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"⏰ Reminder #{reminder_count} — {severity}: {a.package} ({a.repo_full_name})",  # noqa: E501
            },
        },
        {
            "type": "section",
            "fields": [
                {"type": "mrkdwn", "text": f"*Summary:* `{a.cve_summary}`"},
                {"type": "mrkdwn", "text": f"*Package:* `{a.package}` ({a.ecosystem})"},  # noqa: E501
                {"type": "mrkdwn", "text": f"*File:* `{manifest}`"},
                {"type": "mrkdwn", "text": f"*Upgrade:* `{current_version}` → `{suggested_version}`"},  # noqa:E501
                {"type": "mrkdwn", "text": f"*Breaking Risk:* {risk_label}"},
            ],
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Risk Summary:*\n{a.risk_summary}",
            },
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Recommendation:* {rec_label}",
            },
        },
    ]


def build_slack_payload(blocks: list, fallback_text: str) -> dict:
    return {
        "text": fallback_text,
        "blocks": blocks,
    }
