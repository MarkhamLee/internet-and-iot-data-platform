# (C) Markham Lee 2023 - 2026
# https://github.com/MarkhamLee/internet-and-iot-data-platform
# Entry point: resolves configuration and kicks off the Dependabot agent.
import sys
import os
from os import getenv
from agent_pipeline import DependabotAgent
# from qwen_client import QwenClient  # noqa: E402

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)
from agent_library.logging_util import console_logging  # noqa: E402
from agent_library.qwen_client import QwenClient  # noqa: E402


logger = console_logging("Dependabot review main")

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

APPROVED_MODELS = {"qwen3.5:9b", "llama3.2:3b"}


def get_required_env(name: str) -> str:
    value = getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def pg_kwargs() -> dict:
    return {
        "db_host": os.environ["POSTGRES_HOST_K3S"],
        "db_port": 5432,
        "database": os.environ["POSTGRES_DEPENDABOT_DATABASE"],
        "postgres_user": os.environ["POSTGRES_USER_DEPENDABOT"],
        "postgres_password": os.environ["DEPENDABOT_AGENT_POSTGRES"],
    }


def main() -> None:
    ollama_url = get_required_env("OLLAMA_BASE_URL")
    slack_webhook_url = get_required_env("DEPENDABOT_SLACK_WEBHOOK")

    qwen_model = getenv("QWEN_MODEL", "qwen3.5:9b")
    prompt_version = getenv("PROMPT_VERSION", "v1")
    review_limit = int(getenv("REVIEW_LIMIT", "25"))
    read_timeout = int(getenv("READ_TIMEOUT", "600"))
    reminder_interval_hours = int(getenv("REMINDER_INTERVAL_HOURS", "24"))
    agent_runs_table = getenv("AGENT_RUNS_TABLE", "agent_runs")

    qwen_client = QwenClient(
        ollama_url=ollama_url,
        model=qwen_model,
        approved_models=APPROVED_MODELS,
        timeout=(10, read_timeout),
        temperature=0,
    )

    agent = DependabotAgent(
        qwen_client=qwen_client,
        slack_webhook_url=slack_webhook_url,
        pg_kwargs=pg_kwargs(),
        review_prompt=REVIEW_PROMPT,
        prompt_version=prompt_version,
        review_limit=review_limit,
        reminder_interval_hours=reminder_interval_hours,
        agent_runs_table=agent_runs_table,
    )

    agent.run()


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        logger.exception("Dependabot review workflow failed: %s", exc)
        sys.exit(1)
