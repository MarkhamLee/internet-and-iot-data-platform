# Markham Lee 2023 - 2024
# Finance, Productivity, IoT, & Weather dashboard
# https://github.com/MarkhamLee/finance-productivity-iot-informational-weather-dashboard
# Script for reading data from a BME280 barometric pressure, humidity and
# temperature sensor and then transmitting the data via MQTT.
import smbus2
import bme280
import gc
import json
import os
import sys
from time import sleep

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from iot_libraries.logging_util import logger  # noqa: E402
from iot_libraries.communications_utilities\
    import IoTCommunications  # noqa: E402

com_utilities = IoTCommunications()
DEVICE_FAILURE_CHANNEL = os.environ['DEVICE_FAILURE_CHANNEL']


DEVICE_ID = os.environ['DEVICE_ID']
SENSOR_ID = os.environ['SENSOR_ID']


def get_bme280_data(client, topic, interval):

    logger.info("Data logging started...")
    # error_n = 1

    while True:

        # define key variables
        port = 1
        address = 0x77
        bus = smbus2.SMBus(port)

        calibration_params = bme280.load_calibration_params(bus, address)

        # read data
        data = bme280.sample(bus, address, calibration_params)

        # build payload
        payload = {
            "temperature": data.temperature,
            "barometric_pressure": data.pressure,
            "humidity": data.humidity
        }

        payload = json.dumps(payload)
        result = client.publish(topic, payload)
        status = result[0]

        sleep_duration = interval

        if status != 0:
            message = (f'{SENSOR_ID} MQTT publish failure on {DEVICE_ID}, status code: {status}')  # noqa: E501
            logger.debug(message)  # noqa: E501
            com_utilities.send_slack_alert(message, DEVICE_FAILURE_CHANNEL)
            sleep_duration = 3600

        del data, payload
        gc.collect()

        sleep(sleep_duration)


def main():

    # load environmental variables
    TOPIC = os.environ['OFFICE_TEMP_BME280_TEST']
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
        get_bme280_data(client, TOPIC, INTERVAL)

    finally:
        client.loop_stop()


if __name__ == '__main__':
    main()
