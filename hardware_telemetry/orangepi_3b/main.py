#!/usr/bin/env python
# Markham Lee (C) 2023
# Productivity, Home IoT, Music, Stocks & Weather Dashboard
# https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
# Primary script for hardware monitoring container for the Orange Pi 3B
# pulls CPU temps, utilization and clock speed, as well as GPU temp and RAM use

import json
import time
import gc
import os
import logging
from sys import stdout
from orangepi3b_data import OrangePi3BData

# set up/configure logging with stdout so it can be picked up by K8s
logger = logging.getLogger('Orange_Pi_3B_Telemetry')
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler(stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s - %(message)s')  # noqa: E501
handler.setFormatter(formatter)
logger.addHandler(handler)


def monitor(client: object, getData: object, topic: str):

    DEVICE_ID = os.environ['DEVICE_ID']

    while True:

        time.sleep(1)

        # get CPU utilization
        cpu_util = getData.getCPUData()

        # get current RAM use
        ram_use = getData.getRamData()

        # get per CPU frequencies
        cpu_freq, core = getData.getFreq()

        # get system temperatures
        cpu_temp, gpu_temp = getData.rockchip_3566_temps()

        payload = {
           "cpu_utilization": cpu_util,
           "ram_utilization": ram_use,
           "cpu_freq": cpu_freq,
           "cpu_temp": cpu_temp,
           "gpu_temp": gpu_temp
        }

        payload = json.dumps(payload)

        result = client.publish(topic, payload)
        status = result[0]
        if status != 0:

            print(f'Failed to send {payload} to: {topic}')
            logger.debug(f'MQTT publishing failure for hardware monitoring on: {DEVICE_ID}, return code: {status}')  # noqa: E501

        del payload, cpu_util, ram_use, cpu_freq, cpu_temp, gpu_temp, \
            status, result
        gc.collect()


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
    clientID = opi_data.getClientID()

    # get mqtt client
    client, code = opi_data.mqttClient(clientID, MQTT_USER,
                                       MQTT_SECRET, MQTT_BROKER,
                                       MQTT_PORT)

    # start monitoring
    try:
        monitor(client, opi_data, TOPIC)

    finally:
        client.loop_stop()


if __name__ == '__main__':
    main()
