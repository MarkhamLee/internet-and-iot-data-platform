#!/usr/bin/env python
# Markham Lee (C) 2023
# Productivity, Home IoT, Music, Stocks & Weather Dashboard
# https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
# Primary script for hardware monitoring container for the Orange Pi 3B
# pulls CPU temps, utilization and clock speed, as well as GPU temp and RAM use

import json
import gc
import os
import sys
from time import sleep
from orangepi3b_data import OrangePi3BData


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

            # get per CPU frequencies
            cpu_freq, core = get_data.get_freq()

            # get system temperatures
            # using an experimental OS, temp sensors are having issues
            # commenting out while I work on a fix.
            # cpu_temp, gpu_temp = get_data.rockchip_3566_temps()

            '''
            payload = {
                "cpu_utilization": cpu_util,
                "ram_utilization": ram_use,
                "cpu_freq": cpu_freq,
                "cpu_temp": cpu_temp,
                "gpu_temp": gpu_temp
                }
            '''

            payload = {
                "cpu_utilization": cpu_util,
                "ram_utilization": ram_use,
                "cpu_freq": cpu_freq
            }

            payload = json.dumps(payload)
            send_message(client, TOPIC, payload)

            del payload, cpu_util, ram_use, cpu_freq, cpu_temp, gpu_temp
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

    # instantiate data and utilities class
    opi_data = OrangePi3BData()

    TOPIC = os.environ['TOPIC']

    # load environmental variables
    MQTT_BROKER = os.environ['MQTT_BROKER']
    MQTT_USER = os.environ['MQTT_USER']
    MQTT_SECRET = os.environ['MQTT_SECRET']
    MQTT_PORT = int(os.environ['MQTT_PORT'])

    # get unique client ID
    client_id = com_utils.get_client_id()

    # get mqtt client
    client, code = com_utils.mqtt_client(client_id, MQTT_USER,
                                         MQTT_SECRET, MQTT_BROKER,
                                         MQTT_PORT)

    # start monitoring
    try:
        monitor(client, opi_data, TOPIC)

    finally:
        client.loop_stop()


if __name__ == '__main__':
    main()
