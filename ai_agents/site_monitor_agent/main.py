# (C) Markham Lee 2023 - 2026
# https://github.com/MarkhamLee/internet-and-iot-data-platform
# Entry point for the site monitor agent
from __future__ import annotations

import os
import socket
import sys
import uuid
from datetime import UTC, datetime
from os import getenv
import psycopg
from time import perf_counter
from psycopg.types.json import Jsonb
from config import load_config
from research_pipeline import run_research_cycle

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from agent_library.logging_util import console_logging  # noqa: E402
from agent_library.qwen_client import QwenClient  # noqa: E402
from agent_library.agent_utilities import write_instrumentation  # noqa: E402

logger = console_logging("site_monitor_agent")

APPROVED_MODELS = {"qwen3.5:9b", "llama3.2:3b"}
AGENT_RUNS_TABLE = "agent_runs"
AGENT_NAME = "site_monitor_agent"


def main() -> None:
    run_uuid = uuid.uuid4()
    started_at = datetime.now(tz=UTC)
    status = "success"
    errors: list[str] = []

    review_limit = int(getenv("REVIEW_LIMIT", "25"))
    read_timeout = int(getenv("READ_TIMEOUT", "600"))
    prompt_version = getenv("PROMPT_VERSION", "v1")
    git_sha = getenv("GIT_SHA", None)

    logger.info(
        "Site monitor agent starting run_uuid=%s review_limit=%s",
        run_uuid,
        review_limit,
    )

    app = load_config()

    client = QwenClient(
        ollama_url=app.ollama_url,
        model=app.qwen_model,
        approved_models=APPROVED_MODELS,
        timeout=(10, read_timeout),
        temperature=app.llm_temperature,
    )

    run_start = perf_counter()

    try:
        cycle_result = run_research_cycle(
            app=app,
            client=client,
            review_limit=review_limit,
        )
    except Exception as exc:
        logger.exception("Research cycle failed: %s", exc)
        cycle_result = {
            "items_fetched": 0,
            "llm_invoked": 0,
            "alerted": 0,
            "slack_attempted": 0,
            "slack_sent": 0,
            "failed": 1,
            "avg_llm_seconds": None,
            "duration_seconds": None,
            "errors": [str(exc)],
        }
        status = "failed"
        errors.append(str(exc))

    if cycle_result.get("errors"):
        status = "partial"
        errors.extend(cycle_result["errors"])

    completed_at = datetime.now(tz=UTC)
    total_duration = round(perf_counter() - run_start, 2)

    run_payload = {
        "run_uuid": str(run_uuid),
        "started_at": started_at,
        "completed_at": completed_at,
        "duration_seconds": total_duration,
        "agent_name": AGENT_NAME,
        "host_name": socket.gethostname(),
        "process_id": os.getpid(),
        "git_sha": git_sha,
        "target_count": cycle_result.get("items_fetched", 0),
        "items_fetched_count": cycle_result.get("items_fetched", 0),
        "succeeded_target_count": (
            cycle_result.get("llm_invoked", 0)
            - cycle_result.get("failed", 0)
        ),
        "failed_target_count": cycle_result.get("failed", 0),
        "llm_invoked_target_count": cycle_result.get("llm_invoked", 0),
        "slack_attempted_target_count": cycle_result.get("slack_attempted", 0),
        "slack_sent_target_count": cycle_result.get("slack_sent", 0),
        "status": status,
        "error_count": len(errors),
        "warning_count": 0,
        # jsonb fields
        "errors": Jsonb(errors) if errors else None,
        "metadata": Jsonb(
            {
                "prompt_version": prompt_version,
                "model_name": app.qwen_model,
                "avg_llm_seconds": cycle_result.get("avg_llm_seconds"),
            }
        ),
    }

    try:
        with psycopg.connect(app.postgres_dsn, autocommit=True) as conn:
            write_instrumentation(
                conn=conn,
                table=app.agent_runs_table,
                payload=run_payload,
            )
        logger.info(
            "Run instrumentation written run_uuid=%s status=%s duration=%ss "
            "llm_invoked=%s slack_sent=%s errors=%s",
            run_uuid,
            status,
            total_duration,
            cycle_result.get("llm_invoked", 0),
            cycle_result.get("slack_sent", 0),
            len(errors),
        )
    except Exception as exc:
        logger.warning(
            "Run instrumentation FAILED run_uuid=%s: %s",
            run_uuid,
            exc,
        )

    logger.info("Site monitor agent complete run_uuid=%s", run_uuid)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        logger.exception("Site monitor agent failed: %s", exc)
        sys.exit(1)
