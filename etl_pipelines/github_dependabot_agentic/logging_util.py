# (C) Markham Lee 2023-2026
# Internet & IoT Data Platform
# https://github.com/MarkhamLee/internet-and-iot-data-platform
import logging
from logging.handlers import RotatingFileHandler
from sys import stdout


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
