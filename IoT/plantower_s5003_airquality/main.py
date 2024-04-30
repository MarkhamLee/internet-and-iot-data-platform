# Markham Lee (C) 2023 - 2024
# Finance, Productivity, IoT Dashboard
# https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
# Python script for pulling data from a PMS5003 air quality sensor
# connected by USB, and then pushing the data to console.
# Influenced by R. Smith's script for the same sensor:
# https://github.com/rsmith-nl/ft232-pms5003/tree/main
# WIP - this iteration is to test pushing the containner to a device
# and then running it for several days to see if the measurements are
# consistent
import json
import gc
import os
import sys
from time import sleep
from plantower_utils import PlantowerS5003Utils


parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from iot_libraries.logging_util import logger  # noqa: E402
from iot_libraries.communications_utilities\
    import IoTCommunications  # noqa: E402

com_utilities = IoTCommunications()
DEVICE_FAILURE_CHANNEL = os.environ['DEVICE_FAILURE_CHANNEL']

DEVICE_ID = os.environ['DEVICE_ID']
SENSOR_ID = os.environ['PLANTOWER_SENSOR_ID']


def get_sensor_data(client: object, topic: str, interval: int, quality):

    PM2_THRESHOLD = int(os.environ['PM2_THRESHOLD'])
    PM10_THRESHOLD = int(os.environ['PM10_THRESHOLD'])

    while True:

        try:

            data = quality.get_air_data(interval)

            # data quality checks
            if len(data) != 32:
                continue

            if not data.startswith(b"BM"):
                continue

            # parse data
            pm1, pm25, pm10 = quality.parse_plantower_data(data)

            # check to see if pollutant levels above a threshold, send alert
            # IDEA: look into coordinating multiple air quality sensors and/or
            # air purifiers. E.g., if air quality drops due to cooking, have
            # the others check more often or turn up the purifiers.
            if pm25 > PM2_THRESHOLD or pm10 > PM10_THRESHOLD:
                send_threshold_alert(pm25, pm10)

            # create payload
            payload = {
                "pm1": pm1,
                "pm25": pm25,
                "pm10": pm10
            }

            payload = json.dumps(payload)
            send_message(client, payload, topic)

            del payload
            gc.collect()

        except Exception as e:
            message = (f"Failed to read from device with error: {e}")
            logger.debug(message)
            com_utilities.send_slack_alert(message, DEVICE_FAILURE_CHANNEL)

        sleep(interval)


def send_message(client: object, payload: dict, topic: str):

    try:
        result = client.publish(topic, payload)
        status = result[0]

    except Exception as error:
        logger.debug(f'MQTT connection error: {error}\
                            with status: {status}')

    # memory clean-up
    del payload, result, status
    gc.collect()


# TODO: move this to common library for all air quality sensors
def send_threshold_alert(pm2, pm10):

    # load threshold alert webhook
    AIR_ALERT_WEBHOOK = os.environ['CLIMATE_ALERT_WEBHOOK']

    # alerts for now, future plan is to link/hook into an air purifier
    message = (f"{SENSOR_ID} reporting air quality above threshold, ventilate room. PM2_5 level: {pm2}, PM10 level: {pm10} ")  # noqa: E501

    com_utilities.send_slack_webhook(AIR_ALERT_WEBHOOK, message)


def main():

    try:
        quality = PlantowerS5003Utils()
        logger.info(f'Plantower S5003 connected with ID: {SENSOR_ID}')

    except Exception as e:
        message = (f'Plantower Air Quality class failed to instantiate with error {e}, going to sleep....')  # noqa: E501
        logger.debug(message)
        com_utilities.send_slack_alert(message, DEVICE_FAILURE_CHANNEL)
        sleep(1800)

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
        get_sensor_data(client, TOPIC, INTERVAL, quality)

    finally:
        client.loop_stop()


if __name__ == '__main__':
    main()
