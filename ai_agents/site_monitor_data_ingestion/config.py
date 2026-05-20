# (C) Markham Lee 2023 - 2026
# https://github.com/MarkhamLee/internet-and-iot-data-platform
# Loading vars, config, etc., for the data ingestion
# component of the site monitoring agent
from __future__ import annotations

import os
import yaml
from pathlib import Path
from pydantic import BaseModel, Field, HttpUrl
from typing import Any


class WatchTarget(BaseModel):
    page_key: str
    url: HttpUrl
    enabled: bool = True
    desired_state_description: str
    undesired_state_description: str
    css_selectors: list[str] = Field(default_factory=list)
    include_text_patterns: list[str] = Field(default_factory=list)
    reminder_interval_minutes: int = 60
    send_missed_it_message: bool = True
    custom_prompt: str | None = None
    slack_channel: str | None = None


class WatchFileConfig(BaseModel):
    targets: list[WatchTarget]


class AppConfig(BaseModel):
    postgres_dsn: str
    slack_webhook_url: str
    log_level: str = "INFO"
    force_research_after_hours: int | None = None
    targets: list[WatchTarget]


def load_watch_file(path: str | Path = "monitoring_targets.yml")\
      -> WatchFileConfig:
    with open(path, "r", encoding="utf-8") as file_handle:
        raw: dict[str, Any] = yaml.safe_load(file_handle) or {}
    return WatchFileConfig(**raw)


def load_config(path: str | Path = "monitoring_targets.yml") -> AppConfig:
    watch_cfg = load_watch_file(path)
    force_research_after_hours_raw = os.\
        environ.get("FORCE_RESEARCH_AFTER_HOURS")

    return AppConfig(
        postgres_dsn=os.environ["POSTGRES_SITE_MONITOR_DSN"],
        slack_webhook_url=os.environ["SITE_MONITOR_SLACK_WEBHOOK"],
        log_level=os.environ.get("LOG_LEVEL", "INFO"),
        force_research_after_hours=(
            int(force_research_after_hours_raw)
            if force_research_after_hours_raw
            else None
        ),
        targets=watch_cfg.targets,
    )
