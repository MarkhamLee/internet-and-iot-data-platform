# (C) Markham Lee 2023 - 2026
# https://github.com/MarkhamLee/internet-and-iot-data-platform

from __future__ import annotations

import logging
import sys
from sys import stdout
from pathlib import Path
from logging.handlers import RotatingFileHandler

DEFAULT_FORMAT = (
    "%(asctime)s %(levelname)-8s %(name)s "
    "[%(filename)s:%(lineno)d] %(message)s"
)


def configure_logger(
    name: str,
    *,
    logger_level: int = logging.DEBUG,
    console_level: int | None = logging.INFO,
    file_level: int | None = logging.DEBUG,
    log_dir: str | Path = "logs",
) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logger_level)
    logger.propagate = False

    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        DEFAULT_FORMAT,
        datefmt="%Y-%m-%dT%H:%M:%S%z",
    )

    if console_level is not None:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(console_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    if file_level is not None:
        path = Path(log_dir)
        path.mkdir(parents=True, exist_ok=True)

        file_handler = RotatingFileHandler(
            path / f"{name.replace('.', '_')}.log",
            maxBytes=2_000_000,
            backupCount=5,
            encoding="utf-8",
        )
        file_handler.setLevel(file_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def console_logging(name: str):

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    handler = logging.StreamHandler(stdout)
    handler.setLevel(logging.DEBUG)
    formatter = logging.\
        Formatter('%(asctime)s - %(levelname)s - %(filename)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.propagate = False

    return logger
