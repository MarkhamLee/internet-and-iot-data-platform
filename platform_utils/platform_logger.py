# (C) Markham Lee 2023 - 2026
# https://github.com/MarkhamLee/internet-and-iot-data-platform

from __future__ import annotations

import logging
import sys
import threading
import time


DEFAULT_FORMAT = (
    "%(asctime)sZ %(levelname)-8s "
    "logger=%(name)s pid=%(process)d "
    "source=%(filename)s:%(lineno)d %(message)s"
)

_CONFIG_LOCK = threading.RLock()


def configure_logger(
    name: str,
    *,
    logger_level: int = logging.DEBUG,
    console_level: int = logging.INFO,
) -> logging.Logger:
    """Configure one idempotent stdout-only logger.

    The logger owns exactly one stdout handler. Propagation is disabled so a
    root handler cannot emit the same record a second time.
    """
    logger = logging.getLogger(name)

    with _CONFIG_LOCK:
        logger.setLevel(logger_level)
        logger.disabled = False
        logger.propagate = False

        for existing_handler in logger.handlers[:]:
            logger.removeHandler(existing_handler)
            existing_handler.close()

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(console_level)

        formatter = logging.Formatter(
            DEFAULT_FORMAT,
            datefmt="%Y-%m-%dT%H:%M:%S",
        )
        formatter.converter = time.gmtime

        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger
