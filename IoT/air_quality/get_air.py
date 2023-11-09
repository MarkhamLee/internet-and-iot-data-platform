# Markham Lee (C) 2023
# Productivity, Weather, Personal, et al dashboard:
# https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
# This script retrieves air quality data from a Nova PM SDS011
# Air Quality sensor connected via USB and then sends the data off
# to a MQTT broker

import json
import time
import gc
import sys
import os
import logging
from airquality import AirQuality


def air(client: object, quality: object, topic: str, interval: int) -> str:

    while True:

        # TODO: add exception handling + alerting if a sensor fails

        # get air quality data
        pm2, pm10 = quality.getAirQuality()

        # round off air quality numbers
        pm2 = round(pm2, 2)
        pm10 = round(pm10, 2)

        payload = {
            "pm2": pm2,
            "pm10": pm10
        }

        payload = json.dumps(payload)
        result = client.publish(topic, payload)
        status = result[0]

        if status == 0:
            print(f'Data {payload} was published to: {topic}')

        else:
            print(f'Failed to send {payload} to: {topic}')
            logging.debug(f'data failed to publish to MQTT topic, status code:\
                          {status}')

        # given that this is a RAM constrained device, let's delete
        # everything and do some garbage collection, watching things
        # on htop the RAM usage was creeping upwards...
        del payload, result, status, pm2, pm10
        gc.collect()

        time.sleep(interval)


def main():

    # instantiate air quality class
    quality = AirQuality()

    # parse command line arguments
    args = sys.argv[1:]

    INTERVAL = int(args[0])
    TOPIC = str(args[1])

    # Load Environmental Variables
    MQTT_BROKER = os.environ['MQTT_BROKER']
    MQTT_USER = os.environ['MQTT_USER']
    MQTT_SECRET = os.environ['MQTT_SECRET']
    MQTT_PORT = int(os.environ['MQTT_PORT'])

    # get unique client ID
    clientID = quality.getClientID()

    # get mqtt client
    client, code = quality.mqttClient(clientID, MQTT_USER, MQTT_SECRET,
                                      MQTT_BROKER, MQTT_PORT)

    # start data monitoring
    try:
        air(client, quality, TOPIC, INTERVAL)

    finally:
        client.loop_stop()


if __name__ == '__main__':
    main()
