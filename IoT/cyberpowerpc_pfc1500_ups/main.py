# Markham Lee (C) 2024
# Finance, Productivity, IoT & General Data Platform
# https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
# Script for pulling leveraging the Network Ups Tools (NUT) application to
# to pull data from an UPS device connected to a small server running the
# NUT server. Running this requires the NUT client to installed on the
# machine running it
import gc
import json
import os
import sys
from time import sleep
import subprocess as sp


parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from iot_libraries.logging_util import logger  # noqa: E402
from iot_libraries.communications_utilities\
    import IoTCommunications  # noqa: E402

# instantiate hardware monitoring class
monitor_utilities = IoTCommunications()

SLACK_WEBHOOK = os.environ['SLACK_HW_ALERTS']
UPS_ID = os.environ['UPS_ID']


# start monitoring loop
def ups_monitoring(CMD: str, TOPIC: str, client: object):

    INTERVAL = int(os.environ['UPS_INTERVAL'])

    logger.info(f'Starting monitoring for {UPS_ID}')
    excessive_load_count = 0
    load_threshold = 900/INTERVAL
    issue_count = 0
    issue_threshold = 600/INTERVAL

    # ensures we get an alert every five minutes if the mains power is lost
    power_alert_threshold = 5 * (60/INTERVAL)

    # ensures we get an alert the first time it happens
    power_alert_count = power_alert_threshold

    while True:

        try:
            # query the UPS via bash to acquire data
            data = sp.check_output(CMD, shell=True)

        except Exception as e:
            logger.debug(f'Failed to read data from UPS: {UPS_ID} with error: {e}')  # noqa: E501
            # TODO: add Slack alert for when UPS goes down, low priority for
            # now as the firewall will detect this and send out a Slack alert.
            # Will need to add in the future once I add more UPS devices.
            sleep(600)
            continue

        # parse the output of the bash command into a Python dictionary
        payload = parse_data(data)

        # check load status, send alert if it's too high
        # TODO: add a series of alerts based on the values above
        # Note: running on battery already generates alerts via the
        # Firewall.

        if float(payload['load_percentage']) > 50:
            excessive_load_count += 1

        else:
            excessive_load_count = 0  # reset counter

        if excessive_load_count > load_threshold:
            message = (f'Power load has exceeded 50% on {UPS_ID} for more than 15 minutes')  # noqa: E501
            logger.info(message)
            monitor_utilities.send_slack_webhook(SLACK_WEBHOOK, message)
            excessive_load_count = 0  # reset the timer

        ups_status = payload['ups_status']

        # send an alert if the device is running off the battery
        # AKA using mains AC power.
        if ups_status == ' OB DISCHRG':
            power_alert_count += 1
            logger.info(f'UPS {UPS_ID} has switched to battery power')
        else:
            # proper reset the issue as resolved
            power_alert_count = power_alert_threshold
            back_on_ac_message = (f'UPS {UPS_ID} is back on AC/Mains Power')
            logger.info(back_on_ac_message)
            send_power_status_alert(back_on_ac_message)

        if power_alert_count > power_alert_threshold:
            lost_power_message = (f'UPS {UPS_ID} has lost mains power and is running off of the battery')  # noqa: E501
            logger.info(lost_power_message)
            logger.info('Sending loss of AC mains alert')
            send_power_status_alert(lost_power_message)
            power_alert_count = 0

        if ups_status != ' OL' and ups_status != ' OB DISCHRG':
            issue_count += 1

            if issue_count > issue_threshold:
                logger.info(f'UPS device: {UPS_ID} status change alert to: {ups_status}, sending Slack alert...')  # noqa: E501
                send_device_alert(ups_status)
                issue_count = 0

        # build json payload
        payload = json.dumps(payload)

        result = client.publish(TOPIC, payload)

        if result[0] != 0:  # checking status code
            logger.debug(f'MQTT publishing failure for monitoring UPS: {UPS_ID}, return code: {result[0]}')  # noqa: E501

        del data, payload, result
        gc.collect()

        sleep(INTERVAL)


def send_power_status_alert(message):

    logger.info(message)
    monitor_utilities.send_slack_webhook(SLACK_WEBHOOK, message)


def send_device_alert(ups_status):

    message = (f'UPS device status change to: {ups_status}, which may require direct attention')  # noqa: E501
    logger.info(message)
    logger.info('Sending UPS device status change Slack alert')
    monitor_utilities.send_slack_webhook(SLACK_WEBHOOK, message)


# build UPS bash query string
def build_ups_query() -> str:

    UPS_IP = os.environ['UPS_IP']
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

    # operating parameters
    TOPIC = os.environ['UPS_TOPIC']

    # load environmental variables
    MQTT_BROKER = os.environ["MQTT_BROKER"]
    MQTT_USER = os.environ['MQTT_USER']
    MQTT_SECRET = os.environ['MQTT_SECRET']
    MQTT_PORT = int(os.environ['MQTT_PORT'])

    CMD = build_ups_query()

    # get unique client ID
    clientID = monitor_utilities.getClientID()

    # get mqtt client
    client, code = monitor_utilities.mqttClient(clientID,
                                                MQTT_USER, MQTT_SECRET,
                                                MQTT_BROKER, MQTT_PORT)

    message = (f'{UPS_ID} monitoring is online')
    logger.info(message)
    monitor_utilities.send_slack_webhook(SLACK_WEBHOOK, message)

    # start monitoring
    try:
        ups_monitoring(CMD, TOPIC, client)

    finally:
        client.loop_stop()


if __name__ == '__main__':
    main()
