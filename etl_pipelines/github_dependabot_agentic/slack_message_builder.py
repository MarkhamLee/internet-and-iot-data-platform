# (C) Markham Lee 2023 - 2026
# Internet and IoT Data Platform
# https://github.com/MarkhamLee/internet-and-iot-data-platform
from schemas import DependabotRiskAssessment

RISK_EMOJI = {"low": "🟢", "medium": "🟡", "high": "🔴"}
REC_EMOJI = {
    "apply_immediately": "⚡ Apply Immediately",
    "apply_with_testing": "🧪 Apply with Testing",
    "defer": "⏳ Defer",
    "skip": "⛔ Skip"
}
SEV_COLOR = {"critical": "#FF0000", "high": "#FF6600", "medium": "#FFCC00", "low": "#36A64F"}

def build_report_blocks(a: DependabotRiskAssessment, repo: str, cve_id: str) -> list:
    return [
        {"type": "header", "text": {"type": "plain_text",
            "text": f"🔒 {a.severity.upper()}: {a.package} ({repo})"}},
        {"type": "section", "fields": [
            {"type": "mrkdwn", "text": f"*Package:* `{a.package}` ({a.ecosystem})"},
            {"type": "mrkdwn", "text": f"*CVE:* {cve_id or 'N/A'}"},
            {"type": "mrkdwn", "text": f"*Upgrade:* `{a.current_version}` → `{a.suggested_version}`"},
            {"type": "mrkdwn", "text": f"*Breaking Risk:* {RISK_EMOJI[a.breaking_change_risk]} {a.breaking_change_risk}"},
        ]},
        {"type": "section", "text": {"type": "mrkdwn",
            "text": f"*CVE Summary:*\n{a.cve_summary}"}},
        {"type": "section", "text": {"type": "mrkdwn",
            "text": f"*How it's used in the codebase:*\n{a.usage_in_codebase}"}},
        {"type": "section", "text": {"type": "mrkdwn",
            "text": f"*Breaking change rationale:*\n{a.breaking_change_rationale}"}},
        {"type": "section", "text": {"type": "mrkdwn",
            "text": f"*Recommendation:* {REC_EMOJI[a.recommendation]}"}},
        {"type": "rich_text", "elements": [{
            "type": "rich_text_preformatted",
            "elements": [{"type": "text", "text": a.suggested_pr_description}]
        }]},
    ]

def build_reminder_blocks(a: DependabotRiskAssessment, reminder_count: int) -> list:
    return [
        {"type": "section", "text": {"type": "mrkdwn",
            "text": f"⏰ *Reminder #{reminder_count}* — `{a.package}` upgrade still pending.\n"
                    f"Recommendation: {REC_EMOJI[a.recommendation]}"}}
    ]