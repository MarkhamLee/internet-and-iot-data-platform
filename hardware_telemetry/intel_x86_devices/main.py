#!/usr/bin/env python
# Markham Lee (C) 2023
# Productivity, Home IoT, Music, Stocks & Weather Dashboard
# https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
# Primary script for a hardware monitoring container for a generic Linux x86
# Device, pulls CPU temps, utilization and clock speed, as well as GPU temp
# and RAM use

import json
import time
import gc
import os
import logging
from sys import stdout
from intel_x86 import Intelx86

# set up/configure logging with stdout so it can be picked up by K8s
logger = logging.getLogger('intel_x86_telemetry_logger')
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler(stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s - %(message)s')  # noqa: E501
handler.setFormatter(formatter)
logger.addHandler(handler)


def monitor(client: object, getData: object, topic: str):

    while True:

        time.sleep(1)

        # get CPU utilization
        cpu_util = getData.getCPUData()

        # get current RAM use
        ram_use = getData.getRamData()

        # get avg clock speed for all cores
        cpu_freq, core = getData.getFreq()

        # get CPU temperature
        cpu_temp = getData.coreTemp()

        payload = {
           "cpu_utilization": cpu_util,
           "ram_utilization": ram_use,
           "cpu_freq": cpu_freq,
           "cpu_temp": cpu_temp
        }

        payload = json.dumps(payload)

        result = client.publish(topic, payload)
        status = result[0]
        if status != 0:

            print(f'Failed to send {payload} to: {topic}')
            logger.debug(f'MQTT publishing failure, return code: {status}')

        del payload, cpu_util, ram_use, cpu_freq, cpu_temp, \
            status, result
        gc.collect()


def main():

    # instantiate data and utilities class
    intel_x86_data = Intelx86()

    # get MQTT topic
    TOPIC = os.environ['TOPIC']

    # load environmental variables
    MQTT_BROKER = os.environ['MQTT_BROKER']
    MQTT_USER = os.environ['MQTT_USER']
    MQTT_SECRET = os.environ['MQTT_SECRET']
    MQTT_PORT = int(os.environ['MQTT_PORT'])

    # get unique client ID
    clientID = intel_x86_data.getClientID()

    # get mqtt client
    client, code = intel_x86_data.mqttClient(clientID, MQTT_USER,
                                             MQTT_SECRET, MQTT_BROKER,
                                             MQTT_PORT)

    # start monitoring
    try:
        monitor(client, intel_x86_data, TOPIC)

    finally:
        client.loop_stop()


if __name__ == '__main__':
    main()
