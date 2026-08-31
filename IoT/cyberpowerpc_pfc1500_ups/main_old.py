# Markham 2023 - 2026
# Internet & IoT Data Platform:
# https://github.com/MarkhamLee/internet-and-iot-data-platform
# Script for pulling leveraging the Network Ups Tools (NUT) application to
# to pull data from an UPS device connected to a small server running
# NUT server.
import gc
import json
import os
from time import sleep
import subprocess as sp

import platform_utils.alert_utils as alerting
import platform_utils.data_utils as data_utils
from platform_utils.platform_logger import configure_logger
import iot_libraries.iot_com_utilities as iot_com


logger = configure_logger('cyberpowerpc_pfc1500_ups_monitoring')


# load environmental variables
# Note:  UPS IP is the IP of the mini server connected
# to the UPS, not the IP of the UP itself
# Since the server might support several UPS devices, we differentiate
# between them with the metric port
INFLUX_MEASUREMENT = os.environ['UPS_INFLUX_MEASUREMENT']
MQTT_BROKER = os.environ["MQTT_BROKER"]
MQTT_USER = os.environ['MQTT_USER']
MQTT_SECRET = os.environ['MQTT_SECRET']
MQTT_PORT = int(os.environ['MQTT_PORT'])
INTERVAL = int(os.environ['UPS_INTERVAL'])
SLACK_WEBHOOK = os.environ['SLACK_HW_ALERTS']
TAG_KEY = os.environ['TAG_KEY']
TAG_VALUE = os.environ['TAG_VALUE']
TOPIC = os.environ['UPS_TOPIC']
UPS_ID = os.environ['UPS_ID']
UPS_IP = os.environ['UPS_IP']

# base payload
BASE_PAYLOAD = {
    "measurement": INFLUX_MEASUREMENT,
    "tags": {
                TAG_KEY: TAG_VALUE,
        }
    }

# set threshold variables
excessive_load_count = 0
load_threshold = 900/INTERVAL
issue_count = 0
issue_threshold = 600/INTERVAL
ac_status = 1
power_alert_threshold = 5 * (60/INTERVAL)

# ensures we get an alert the first time it happens
power_alert_count = power_alert_threshold


# start monitoring loop
def ups_monitoring(CMD: str, TOPIC: str, client: object):

    logger.info('Starting monitoring for %s',
                UPS_ID)

    while True:

        try:
            # query the UPS via bash to acquire data
            data = sp.check_output(CMD, shell=True)

        except Exception as e:
            logger.debug('Failed to read data from UPS: %s, with error: %s',
                         UPS_ID,
                         e)  # noqa: E501
            sleep(600)
            continue

        # parse the output of the bash command into a Python dictionary
        payload = parse_data(data)

        # check load status, send alert if it's too high

        if float(payload['load_percentage']) > 50:
            excessive_load_count += 1

        else:
            excessive_load_count = 0  # reset counter

        if excessive_load_count > load_threshold:
            message = (f'Power load has exceeded 50% on {UPS_ID} for more than 15 minutes',  # noqa: E501
                       UPS_ID)  # noqa: E501
            logger.info(message)
            alerting.send_slack_webhook_basic(SLACK_WEBHOOK, message)
            excessive_load_count = 0  # reset the timer

        ups_status = payload['ups_status']

        # send an alert if the device is running off the battery
        # AKA using mains AC power.
        if ups_status == ' OB DISCHRG':
            power_alert_count += 1
            logger.info('UPS %s has switched to battery power',
                        UPS_ID)
            ac_status = 0

        if ups_status == ' OL CHRG' and ac_status == 0:
            # reset threshold
            ac_status = 1
            power_alert_count = power_alert_threshold
            back_on_ac_message = ('UPS %s is back on AC/Mains Power, battery is recharging',  # noqa: E501
                                  UPS_ID)  # noqa: E501
            logger.info(back_on_ac_message)
            send_power_status_alert(back_on_ac_message)

        if power_alert_count > power_alert_threshold:
            lost_power_message = ('UPS %s has lost mains power and is running off of the battery',  # noqa: E501
                                  UPS_ID)  # noqa: E501
            logger.info(lost_power_message)
            logger.info('Sending loss of AC mains alert')
            send_power_status_alert(lost_power_message)
            power_alert_count = 0

        if ups_status != ' OL' and ups_status != ' OB DISCHRG':
            issue_count += 1

            if issue_count > issue_threshold:
                logger.info('UPS device: %s status change alert to: %s, sending Slack alert...',  # noqa: E501
                            UPS_ID,
                            ups_status)  # noqa: E501
                send_device_alert(ups_status)
                issue_count = 0

        # build json payload
        payload = json.dumps(payload)

        result = client.publish(TOPIC, payload)
        result_code = result[0]

        if result[0] != 0:  # checking status code
            logger.debug('MQTT publishing failure for monitoring UPS: %s, return code: %s',  # noqa: E501
                         UPS_ID,
                         result_code)  # noqa: E501

        del data, payload, result
        gc.collect()

        sleep(INTERVAL)


def check_ups_status(payload: dict):

    ups_status = payload['ups_status']

    # send an alert if the device is running off the battery
    # AKA using mains AC power.
    if ups_status == ' OB DISCHRG':
        power_alert_count += 1
        logger.info('UPS %s has switched to battery power',
                    UPS_ID)
        ac_status = 0

    if ups_status == ' OL CHRG' and ac_status == 0:
        # reset threshold
        ac_status = 1
        power_alert_count = power_alert_threshold
        back_on_ac_message = ('UPS %s is back on AC/Mains Power, battery is recharging',  # noqa: E501
                              UPS_ID)  # noqa: E501
        logger.info(back_on_ac_message)
        send_power_status_alert(back_on_ac_message)

    if power_alert_count > power_alert_threshold:
        lost_power_message = ('UPS %s has lost mains power and is running off of the battery',  # noqa: E501
                              UPS_ID)  # noqa: E501
        logger.info(lost_power_message)
        logger.info('Sending loss of AC mains alert')
        send_power_status_alert(lost_power_message)
        power_alert_count = 0

    if ups_status != ' OL' and ups_status != ' OB DISCHRG':
        issue_count += 1

    if issue_count > issue_threshold:
        logger.info('UPS device: %s status change alert to: %s, sending Slack alert...',  # noqa: E501
                    UPS_ID,
                    ups_status)  # noqa: E501
        send_device_alert(ups_status)
        issue_count = 0




def send_power_status_alert(message):

    logger.info(message)
    alerting.send_slack_webhook_basic(SLACK_WEBHOOK, message)


def send_device_alert(ups_status):

    message = ('UPS device %s status is: %s, which may require direct attention',  # noqa: E501
               UPS_ID,
               ups_status)  # noqa: E501
    logger.info(message)
    logger.info('Sending UPS device status change Slack alert')
    alerting.send_slack_webhook_basic(SLACK_WEBHOOK, message)


# build UPS bash query string
def build_ups_query() -> str:

    CMD = "upsc " + UPS_ID + "@" + UPS_IP

    return CMD


# parse string from bash ups query into a python dictionary
def parse_data(data: str) -> dict:

    data = data.decode("utf-8").strip().split("\n")

    # parse data into a list of lists, each pair of values becomes
    # its own list.
    initial_list = [i.split(':') for i in data]

    # convert lists into a dictionary
    ups_dict = dict(initial_list)

    # build payload for MQTT message
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

    logger.info('Monitoring utilities class instantiated')

    CMD = build_ups_query()

    # get unique client ID
    clientID = iot_com.get_client_id()

    # get mqtt client
    client = iot_com.mqtt_client(clientID,
                                 MQTT_USER,
                                 MQTT_SECRET,
                                 MQTT_BROKER,
                                 MQTT_PORT)

    message = (f'{UPS_ID} monitoring is online')
    logger.info(message)
    alerting.send_slack_webhook_basic(SLACK_WEBHOOK, message)

    # start monitoring
    try:
        ups_monitoring(CMD, TOPIC, client)

    finally:
        client.loop_stop()


if __name__ == '__main__':
    main()
