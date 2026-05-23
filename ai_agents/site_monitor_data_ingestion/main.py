from __future__ import annotations

import os
import sys
from datetime import UTC, datetime

from config import load_config
from ingestion_pipeline import IngestionDependencies, run_ingestion_cycle
from ingestion_instrumentation_store import IngestionInstrumentationStore
from research_queue_store import ResearchQueueStore
from state_store import StateStore

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from agent_library.logging_util import console_logging  # noqa: E402
from agent_library.agent_utilities import validate_webhook  # noqa: E402

logger = console_logging("site_monitor_data_ingestion_logs")


def main() -> None:
    app = load_config()

    webhook_status = validate_webhook(app.slack_webhook_url)
    if not webhook_status:
        logger.warning("Slack webhook is either non-functional or unreachable, security alerts will not be sent")  # noqa: E501

    deps = IngestionDependencies(
        state_store=StateStore(app.postgres_dsn),
        queue_store=ResearchQueueStore(app.postgres_dsn),
        instrumentation_store=IngestionInstrumentationStore(app.postgres_dsn),
        logger=logger,
    )

    started_at = datetime.now(UTC)
    logger.info(
        "Starting site monitor data ingestion count=%s force_research_after_hours=%s",  # noqa: E501
        len(app.targets),
        app.force_research_after_hours,
    )
    run_ingestion_cycle(app=app, deps=deps, started_at=started_at)


if __name__ == "__main__":
    main()
