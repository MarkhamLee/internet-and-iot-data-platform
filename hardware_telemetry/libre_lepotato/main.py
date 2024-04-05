#!/usr/bin/env python
# Markham Lee (C) 2023
# https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
# Primary script for a container that provide hardware monitoring for a
# Libre Le Potato single board computer, tracking CPU: temps, utilization,
# clock speed and RAM use. The Data transmitted via MQTT so that in a future
# iteration MQTT messages can be used for remote management of the device in
# response to issues.
import json
import gc
import os
import sys
from time import sleep
from linux_lepotato import LibreCpuData

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from hw_library.logging_util import logger  # noqa: E402
from hw_library.communications import Communications  # noqa: E402

com_utils = Communications()


def monitor(client: object, get_data: object, TOPIC: str):

    INTERVAL = int(os.environ['INTERVAL'])
    DEVICE_ID = os.environ['DEVICE_ID']

    logger.info(f'Starting HW monitoring for {DEVICE_ID}')

    while True:

        try:

            # get CPU utilization
            cpu_util = get_data.get_cpu_data()

            # get current RAM use
            ram_use = get_data.get_ram_data()

            # get current freq and core count
            cpu_freq, core_count = get_data.get_freq()

            # get CPU temperature
            cpu_temp = get_data.libre_lepotato_temps()

            payload = {
                "cpuTemp": cpu_temp,
                "cpuFreq": cpu_freq,
                "cpuUse": cpu_util,
                "ramUse": ram_use,
                "coreCount": core_count
            }

            payload = json.dumps(payload)
            send_message(client, TOPIC, payload)

            del payload, cpu_util, ram_use, cpu_freq, cpu_temp, core_count
            gc.collect()

        except Exception as e:
            logger.debug(f'failed to read data from {DEVICE_ID} with error: {e}')  # noqa: E501

        sleep(INTERVAL)


def send_message(client: object, TOPIC: str, payload: dict):

    try:
        result = client.publish(TOPIC, payload)
        status = result[0]

        # scenarios where the broker is working as expected, but the message
        # failed to end.
        if status != 0:
            print(f'Failed to send {payload} to: {TOPIC}')
            logger.debug(f'MQTT publishing failure, return code: {status}')

    except Exception as e:
        logger.debug(f"MQTT Broker error: {e}")


def main():

    # instantiate CPU data class & utilities class
    get_data = LibreCpuData()

    TOPIC = os.environ['TOPIC']

    # load environmental variables
    MQTT_BROKER = os.environ["MQTT_BROKER"]
    MQTT_USER = os.environ['MQTT_USER']
    MQTT_SECRET = os.environ['MQTT_SECRET']
    MQTT_PORT = int(os.environ['MQTT_PORT'])

    # get unique client ID
    clientID = com_utils.get_client_id()

    # get mqtt client
    client, code = com_utils.mqtt_client(clientID, MQTT_USER,
                                         MQTT_SECRET, MQTT_BROKER,
                                         MQTT_PORT)

    # start monitoring
    try:
        monitor(client, get_data, TOPIC)

    finally:
        client.loop_stop()


if __name__ == '__main__':
    main()
