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
    import IotCommunications  # noqa: E402

# instantiate hardware monitoring class
monitor_utilities = IotCommunications()

UPS_ID = os.environ['UPS_ID']


# start monitoring loop
def ups_monitoring(CMD: str, TOPIC: str, client: object):

    INTERVAL = int(os.environ['UPS_INTERVAL'])

    logger.info(f'Starting monitoring for {UPS_ID}')
    excessive_load_count = 0
    load_threshold = 900/INTERVAL

    while True:

        try:

            # query the UPS via bash to acquire data
            data = sp.check_output(CMD, shell=True)
            data = data.decode("utf-8").strip().split("\n")

            # parse data into a list of lists, each pair of values becomes
            # its own lists.
            initial_list = [i.split(':') for i in data]

            test_dict = dict(initial_list)

            # payload for MQTT message
            payload = {
                "battery_level": float(test_dict['battery.charge']),
                "battery_run_time":
                    (float(test_dict['battery.runtime']))/60,
                "battery_voltage": float(test_dict['battery.voltage']),
                "input_voltage": float(test_dict['input.voltage']),
                "load_percentage": float(test_dict['ups.load']),
                "max_power": float(test_dict['ups.realpower.nominal']),
                "ups_status": test_dict['ups.status'],
                "device_model": test_dict['device.model']
            }

            # check load status, send alert if it's to high
            # TODO: add a series of alerts based on the values above
            # Note: running on battery already generates alerts via the
            # Firewall.
            if float(test_dict['ups.load']) > 50:
                excessive_load_count += 1

            if excessive_load_count > load_threshold:
                SLACK_WEBHOOK = os.environ['SLACK_HW_ALERTS']
                message = (f'Power load has exceeded 50% on {UPS_ID} for more than 15 minutes')  # noqa: E501
                logger.info(message)
                monitor_utilities.send_slack_webhook(SLACK_WEBHOOK, message)
                excessive_load_count = 0  # reset the timer

            # build json payload
            payload = json.dumps(payload)

            result = client.publish(TOPIC, payload)
            status = result[0]

            if status != 0:
                logger.debug(f'MQTT publishing failure for monitoring UPS: {UPS_ID}, return code: {status}')  # noqa: E501

            del data, initial_list, test_dict, payload, result, status
            gc.collect()

        except Exception as e:
            logger.debug(f'Failed to read data from UPS: {UPS_ID} with error: {e}')  # noqa: E501
            # TODO: add Slack alert for when UPS goes down, low priority for
            # now as the firewall will detect this and send out a Slack alert.
            # Will need to add in the future once I add more UPS devices.
            sleep(600)

        sleep(INTERVAL)


def build_ups_query():

    UPS_IP = os.environ['UPS_IP']
    CMD = "upsc " + UPS_ID + "@" + UPS_IP

    return CMD


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

    # start monitoring
    try:
        ups_monitoring(CMD, TOPIC, client)

    finally:
        client.loop_stop()


if __name__ == '__main__':
    main()
