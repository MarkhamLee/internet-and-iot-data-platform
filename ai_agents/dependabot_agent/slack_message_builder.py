# (C) Markham Lee 2023 - 2026
# Internet and IoT Data Platform
# https://github.com/MarkhamLee/internet-and-iot-data-platform
from schemas import DependabotRiskAssessment


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


def build_report_blocks(a: DependabotRiskAssessment,
                        repo: str,
                        cve_id: str) -> list:
    risk_label = RISK_EMOJI.get(a.breaking_change_risk, "⚪") + f" {a.breaking_change_risk}"  # noqa: E501
    rec_label = REC_EMOJI.get(a.recommendation, f"ℹ️ {a.recommendation}")

    return [
        {"type": "header", "text": {"type": "plain_text",
                                    "text": f"🔒 {a.severity.upper()}: {a.package} ({repo})"}},  # noqa: E501
        {"type": "section", "fields": [
            {"type": "mrkdwn", "text": f"*Package:* `{a.package}` ({a.ecosystem})"},  # noqa: E501
            {"type": "mrkdwn", "text": f"*CVE:* {cve_id or 'N/A'}"},
            {"type": "mrkdwn", "text": f"*Upgrade:* `{a.current_version}` → `{a.suggested_version}`"},  # noqa: E501
            {"type": "mrkdwn", "text": f"*Breaking Risk:* {risk_label}"},
        ]},
        {"type": "section", "text": {"type": "mrkdwn",
                                     "text": f"*CVE Summary:*\n{a.cve_summary}"}},  # noqa: E501
        {"type": "section", "text": {"type": "mrkdwn",
                                     "text": f"*How it's used in the codebase:*\n{a.usage_in_codebase}"}},  # noqa: E501
        {"type": "section", "text": {"type": "mrkdwn",
                                     "text": f"*Breaking change rationale:*\n{a.breaking_change_rationale}"}},  # noqa: E501
        {"type": "section", "text": {"type": "mrkdwn",
                                     "text": f"*Recommendation:* {rec_label}"}},  # noqa: E501
        {"type": "rich_text", "elements": [{
            "type": "rich_text_preformatted",
            "elements": [{"type": "text", "text": a.suggested_pr_description}]
        }]},
    ]


def build_reminder_blocks(a: DependabotRiskAssessment,
                          reminder_count: int) -> list:
    rec_label = REC_EMOJI.get(a.recommendation, f"ℹ️ {a.recommendation}")

    return [
        {"type": "section", "text": {"type": "mrkdwn",
                                     "text": f"⏰ *Reminder #{reminder_count}* — `{a.package}` upgrade still pending.\n"  # noqa: E501
                                             f"Recommendation: {rec_label}"}},
    ]


def build_slack_payload(blocks: list, fallback_text: str) -> dict:
    return {"text": fallback_text, "blocks": blocks}
