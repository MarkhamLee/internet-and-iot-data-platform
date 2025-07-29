# Markham Lee 2023 - 2024
# Finance, Productivity, IoT, & Weather dashboard
# https://github.com/MarkhamLee/finance-productivity-iot-informational-weather-dashboard
# This script pulls data from a DHT22 temperature sensor and the publishes it
# to an MQTT topic.
import adafruit_dht
import board
import json
import gc
import os
import sys
from time import sleep


parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from iot_libraries.logging_util import logger  # noqa: E402
from iot_libraries.communications_utilities\
    import IoTCommunications  # noqa: E402

com_utilities = IoTCommunications()

# load environmental variables
TOPIC = os.environ['TOPIC']
INTERVAL = int(os.environ['INTERVAL'])
MQTT_BROKER = os.environ['MQTT_BROKER']
MQTT_USER = os.environ['MQTT_USER']
MQTT_SECRET = os.environ['MQTT_SECRET']
MQTT_PORT = int(os.environ['MQTT_PORT'])


def get_temps(client: object, topic: str, interval: int):

    # The use pulseio parameter is suggested parameter for a Raspberry Pi
    # may not need to use it with other types of SBCs

    # The sensor fails to read about 1/3 of the time but that can be managed
    # via exception handling and the next attempt is nearly always successful.
    # This appears to be an issue of the sensor + the driver, as this rarely
    # happens on a Raspberry Pi Pico Microcontroller (in my experience). Still,
    # given that you you can immediately retry reading the data it doesn't
    # really cause any issues as far as the sensor providing steady/consistent
    # data.

    temp_device = adafruit_dht.DHT22(board.D4, use_pulseio=False)
    logger.info('Connected to DHT22')

    while True:

        # get temperature and humidity data
        try:
            temp = temp_device.temperature
            humidity = temp_device.humidity

        except RuntimeError as error:  # noqa: F841
            logger.debug(f'Device runtime error {error}')
            continue

        except Exception as error:
            logger.debug(f'Device read error {error}')
            continue

        if temp is not None:

            payload = {
                    "temp": temp,
                    "humidity": humidity
                }

            payload = json.dumps(payload)
            send_message(client, payload, topic)
            del temp, humidity, payload
            gc.collect()

        sleep(interval)


def send_message(client: object, payload: dict, topic: str):

    try:
        result = client.publish(topic, payload)
        status = result[0]

    except Exception as error:
        logger.debug(f'MQTT connection error: {error}\
                            with status: {status}')

    # given that this is a RAM constrained device,
    # let's delete everything and do some garbage collection

    del payload, result, status
    gc.collect()


def main():

    # get unique client ID
    CLIENT_ID = com_utilities.getClientID()

    # get mqtt client
    client = com_utilities.mqttClient(CLIENT_ID,
                                      MQTT_USER,
                                      MQTT_SECRET,
                                      MQTT_BROKER,
                                      MQTT_PORT)

    # start data monitoring
    try:
        get_temps(client, TOPIC, INTERVAL)

    finally:
        client.loop_stop()


if __name__ == '__main__':
    main()
