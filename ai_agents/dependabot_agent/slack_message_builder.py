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
    a: StoredRiskAssessment,
    repo: str,
    cve_id: str,
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
                "text": f"🔒 {severity}: {a.package} ({repo})",
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
                    "text": f"*CVE:* {cve_id or 'N/A'}",
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

    return [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": (
                    f"⏰ *Reminder #{reminder_count}* — `{a.package}` upgrade still pending.\n"  # noqa: E501
                    f"Recommendation: {rec_label}"
                ),
            },
        },
    ]


def build_slack_payload(blocks: list, fallback_text: str) -> dict:
    return {
        "text": fallback_text,
        "blocks": blocks,
    }
