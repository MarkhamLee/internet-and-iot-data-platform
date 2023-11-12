# Markham Lee (C) 2023
# Productivity, Weather, Personal, et al dashboard:
# https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
# Python script for receiving energy data from a TP Link
# Kasa TP25P4 smart plug. Note: this data could just as easily be written
# directly to InfluxDB via its REST API, using MQTT because I may
# (at some point) want to send instructions back to the device, communications,
# monitor if a device is connected, etc.

import asyncio
import os
import sys
import json
import logging
from kasa import SmartPlug
from kasa_utilities import DeviceUtilities

# setup logging
logging.basicConfig(filename='hardwareData.log', level=logging.ERROR,
                    format='%(asctime)s %(levelname)s %(name)s %(threadName)s\
                        : %(message)s')


async def get_plug_data(client: object, topic: str,
                        device_ip: str, interval: int):

    # TODO: add exception handling
    dev = SmartPlug(device_ip)

    while True:

        # poll device for update
        await dev.update()

        # split out data

        payload = {
            "power_usage": dev.emeter_realtime.power,
            "voltage": dev.emeter_realtime.voltage,
            "current": dev.emeter_realtime.current,
            "device_id": dev.device_id
        }

        payload = json.dumps(payload)
        result = client.publish(topic, payload)
        status = result[0]

        if status != 0:

            print(f'Failed to send {payload} to: {topic}')
            logging.error(f'data failed to publish to MQTT topic, status code:\
                          {status}')

        # wait 30 seconds
        await asyncio.sleep(interval)  # Sleep some time between updates


def main():

    # instantiate utilities class
    deviceUtilities = DeviceUtilities()

    # parse command line arguments
    args = sys.argv[1:]

    INTERVAL = int(args[0])
    DEVICE_IP = str(args[1])
    TOPIC = str(args[2])

    # Load Environmental Variables
    MQTT_BROKER = os.environ['MQTT_BROKER']
    MQTT_USER = os.environ['MQTT_USER']
    MQTT_SECRET = os.environ['MQTT_SECRET']
    MQTT_PORT = int(os.environ['MQTT_PORT'])

    # get unique client ID
    clientID = deviceUtilities.getClientID()

    # get mqtt client
    client, code = deviceUtilities.mqttClient(clientID, MQTT_USER,
                                              MQTT_SECRET, MQTT_BROKER,
                                              MQTT_PORT)

    # start device monitoring
    try:
        asyncio.run(get_plug_data(client, TOPIC, DEVICE_IP, INTERVAL))

    finally:
        client.loop_stop()


if __name__ == "__main__":
    main()
