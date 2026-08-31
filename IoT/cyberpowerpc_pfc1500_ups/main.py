# Markham 2023 - 2026
# Internet & IoT Data Platform:
# https://github.com/MarkhamLee/internet-and-iot-data-platform
# Script for pulling leveraging the Network Ups Tools (NUT) application to
# to pull data from an UPS device connected to a small server running
# NUT server.
from __future__ import annotations


import subprocess as sp
import sys
from time import sleep

import platform_utils.alert_utils as alerting
import platform_utils.data_utils as data_utils
from platform_utils.platform_logger import configure_logger

from ups_config import PowerSource, UpsMonitorConfig, InfluxConfig

logger = configure_logger('cyberpowerpc_pfc1500_ups_monitoring')


# start monitoring loop
def ups_monitoring(cmd: str, ups_config, influx_config):

    ups_id = ups_config.ups_id

    while True:

        try:
            # query the UPS via bash to acquire data
            data = sp.check_output(cmd, shell=False)

        except Exception as e:
            logger.debug('Failed to read data from UPS: %s, with error: %s',
                         ups_id,
                         e)  # noqa: E501
            sleep(600)
            continue

        # parse the output of the bash command into a Python dictionary
        payload = parse_data(data)

        # write the data to InfluxDB


def ups_health_check(cmd: str):

    pass


def send_power_status_alert(message, slack_webhook):

    logger.info(message)
    alerting.send_slack_webhook_basic(slack_webhook, message)


def send_device_alert(ups_status, slack_webhook, ups_id):

    message = ('UPS device %s status is: %s, which may require direct attention',  # noqa: E501
               ups_id,
               ups_status)  # noqa: E501
    logger.info(message)
    logger.info('Sending UPS device status change Slack alert')
    alerting.send_slack_webhook_basic(slack_webhook, message)


# build UPS bash query string
def build_ups_query(ups_config) -> str:

    ups_id = ups_config.ups_id
    ups_ip = ups_config.ups_ip

    CMD = "upsc " + ups_id + "@" + ups_ip

    return CMD


# parse string from bash ups query into a python dictionary
def parse_data(data: str) -> dict:

    data = data.decode("utf-8").strip().split("\n")

    # parse data into a list of lists, each pair of values becomes
    # its own list.
    initial_list = [i.split(':') for i in data]

    # convert lists into a dictionary
    ups_dict = dict(initial_list)

    # build json payload
    payload = {
        "battery_level": float(ups_dict['battery.charge']),
        "battery_run_time": (float(ups_dict['battery.runtime']))/60,
        "battery_voltage": float(ups_dict['battery.voltage']),
        "input_voltage": float(ups_dict['input.voltage']),
        "load_percentage": float(ups_dict['ups.load']),
        "max_power": float(ups_dict['ups.realpower.nominal']),
        "ups_status": ups_dict['ups.status'],
        "device_model": ups_dict['device.model']
    }

    return payload


def main():

    try:
        ups_config = UpsMonitorConfig.from_environment()
        influx_config = InfluxConfig.from_environment()

        cmd = build_ups_query(ups_config)

    except (KeyError, ValueError):
        logger.exception(
            "Startup configuration is missing or invalid"
        )
        raise SystemExit(1)

    logger.info(
        "Starting UPS monitor for UPS ID %s located in %s",
        ups_config.ups_id,
        ups_config.ups_location
    )

    ups_monitoring(cmd, ups_config, influx_config)


if __name__ == '__main__':
    main()
