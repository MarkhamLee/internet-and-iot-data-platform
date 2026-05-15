# (C) Markham Lee 2023 - 2026
# https://github.com/MarkhamLee/internet-and-iot-data-platform
# Config script for site monitor. Will need to make a tweak for
# deploying on K3s so that the config is loaded from a config map
# vs a .yaml file.
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
    ollama_url: str
    qwen_model: str
    approved_models: list[str]
    log_level: str = "INFO"
    targets: list[WatchTarget]


def load_watch_file(path: str | Path = "monitoring_targets.yml")\
     -> WatchFileConfig:
    with open(path, "r", encoding="utf-8") as f:
        raw: dict[str, Any] = yaml.safe_load(f) or {}
    return WatchFileConfig(**raw)


def load_config(path: str | Path = "monitoring_targets.yml") -> AppConfig:
    watch_cfg = load_watch_file(path)

    approved_models_raw = os.environ.get("APPROVED_MODELS", "")
    approved_models = [m.strip() for m in approved_models_raw.split(",") if m.strip()]  # noqa: E501

    return AppConfig(
        postgres_dsn=os.environ["POSTGRES_SITE_MONITOR_DSN"],
        slack_webhook_url=os.environ["SITE_MONITOR_SLACK_WEBHOOK"],
        ollama_url=os.environ["OLLAMA_BASE_URL"],
        qwen_model=os.environ["QWEN_MODEL"],
        approved_models=approved_models,
        log_level=os.environ.get("LOG_LEVEL", "INFO"),
        targets=watch_cfg.targets,
    )
