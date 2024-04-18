# Markham Lee 2023 - 2024
# Finance, Productivity, IoT, & Weather dashboard
# https://github.com/MarkhamLee/finance-productivity-iot-informational-weather-dashboard
# Template for quickly standing up a script to read data from a sensor or
# IoT device and transmitting that data via MQTT.
# Add device imports
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


def get_sensor_data(client: object, topic: str, interval: int):

    # add code for connecting/instantiating/initializing the sensor
    logger.info('Connected to <sensor name>')

    while True:

        # replace with
        try:
            value1 = 1
            value2 = 2

        except Exception as error:
            logger.debug(f'Device read error {error}')
            continue

        payload = {
            "value1": value1,
            "value2": value2
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

    # load environmental variables
    TOPIC = os.environ['TOPIC']
    INTERVAL = int(os.environ['INTERVAL'])
    MQTT_BROKER = os.environ['MQTT_BROKER']
    MQTT_USER = os.environ['MQTT_USER']
    MQTT_SECRET = os.environ['MQTT_SECRET']
    MQTT_PORT = int(os.environ['MQTT_PORT'])

    # get unique client ID
    CLIENT_ID = com_utilities.getClientID()

    # get mqtt client
    client, code = com_utilities.mqttClient(CLIENT_ID, MQTT_USER,
                                            MQTT_SECRET, MQTT_BROKER,
                                            MQTT_PORT)

    # start data monitoring
    try:
        get_sensor_data(client, TOPIC, INTERVAL)

    finally:
        client.loop_stop()


if __name__ == '__main__':
    main()
