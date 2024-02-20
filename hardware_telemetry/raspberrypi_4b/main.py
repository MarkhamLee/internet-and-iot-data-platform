#!/usr/bin/env python
# Markham Lee (C) 2023
# https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
# Primary script for a container that provide hardware monitoring for a
# Raspberry Pi 4B, tracking CPU: temps, utilization and clock speed, GPU temps
# and RAM use. The Data transmitted via MQTT so that in a future iteration MQTT
# messages can be used for remote management of the device in response to
# issues.

import os
import json
import time
import gc
import logging
from sys import stdout
from rpi4b_data import Rpi4bData

# set up/configure logging with stdout so it can be picked up by K8s
logger = logging.getLogger('Raspberry_Pi_4B_Telemetry')
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
        cpuUtil = getData.getCPUData()

        # get current RAM use
        ramUse = getData.getRamData()

        # get current freq and core count
        cpuFreq, coreCount = getData.getFreq()

        # get CPU temperature
        cpuTemp = getData.get_rpi4b_temps()

        payload = {
            "cpuTemp": cpuTemp,
            "cpuFreq": cpuFreq,
            "cpuUse": cpuUtil,
            "ramUse": ramUse
        }

        payload = json.dumps(payload)

        result = client.publish(topic, payload)
        status = result[0]

        if status != 0:

            print(f'Failed to send {payload} to: {topic}')
            logger.debug(f'MQTT publishing failure for hardware monitoring on: {DEVICE_ID}, return code: {status}')  # noqa: E501

        del payload, cpuUtil, ramUse, cpuFreq, cpuTemp, status, result
        gc.collect()


def main():

    # instantiate utilities class
    get_data = Rpi4bData()

    # operating parameters
    TOPIC = os.environ['TOPIC']

    # load environmental variables
    MQTT_BROKER = os.environ["MQTT_BROKER"]
    MQTT_USER = os.environ['MQTT_USER']
    MQTT_SECRET = os.environ['MQTT_SECRET']
    MQTT_PORT = int(os.environ['MQTT_PORT'])

    # get unique client ID
    clientID = get_data.getClientID()

    # get mqtt client
    client, code = get_data.mqttClient(clientID, MQTT_USER, MQTT_SECRET,
                                       MQTT_BROKER, MQTT_PORT)

    # start monitoring
    try:
        monitor(client, get_data, TOPIC)

    finally:
        client.loop_stop()


if __name__ == '__main__':
    main()
