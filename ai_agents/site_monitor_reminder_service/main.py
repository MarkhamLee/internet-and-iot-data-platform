# (C) Markham Lee 2023 - 2026
# https://github.com/MarkhamLee/internet-and-iot-data-platform
# Entrypoint for the site monitor reminder service
from __future__ import annotations

import os
import sys
from datetime import UTC, datetime

from platform_utils.platform_logger import configure_logger
from reminder_pipeline import run_reminder_cycle

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from site_monitor_data_ingestion.config import load_config  # noqa: E402

logger = configure_logger("site_monitor_reminder_logs")

path = os.environ.get("MONITORING_TARGETS_PATH", "monitoring_targets.yml")


def main() -> None:
    app = load_config(path)

    started_at = datetime.now(UTC)
    logger.info(
        "Starting site monitor reminder service target_count=%s",
        len(app.targets),
    )
    run_reminder_cycle(app=app, started_at=started_at)


if __name__ == "__main__":
    main()
