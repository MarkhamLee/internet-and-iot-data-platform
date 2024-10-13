# Markham Lee (C) 2023 - 2024
# Productivity, Weather, Personal, et al dashboard:
# https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
# This script retrieves air quality data from a Nova PM SDS011 Air Quality
# sensor connected via USB and then sends the data off to an MQTT broker
import json
import gc
import os
import sys
from time import sleep
from air_quality import AirQuality

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from iot_libraries.logging_util import logger  # noqa: E402
from iot_libraries.communications_utilities\
    import IoTCommunications  # noqa: E402

com_utilities = IoTCommunications()

DEVICE_ID = os.environ['DEVICE_ID']
SENSOR_ID = os.environ['SENSOR_ID']

# load threshold alert webhook
AIR_ALERT_WEBHOOK = os.environ['CLIMATE_ALERT_WEBHOOK']

# load device failure alert webhook
DEVICE_FAILURE_WEBHOOK = os.environ['DEVICE_ALERT_WEBHOOK']


def air(client: object, quality: object, topic: str, interval: int) -> str:

    error_n = 1
    PM2_THRESHOLD = int(os.environ['PM2_THRESHOLD'])
    PM10_THRESHOLD = int(os.environ['PM10_THRESHOLD'])

    while True:

        pm2, pm10 = quality.get_air_quality()

        if pm2 > PM2_THRESHOLD or pm10 > PM10_THRESHOLD:

            send_threshold_alert(pm2, pm10)

        payload = {
            "pm2": pm2,
            "pm10": pm10
        }

        payload = json.dumps(payload)
        result = client.publish(topic, payload)
        status = result[0]

        sleep_duration = interval

        if status != 0:
            message = (f'Air quality MQTT publish failure on {DEVICE_ID}, status code: {status}')  # noqa: E501
            logger.debug(message)  # noqa: E501
            com_utilities.send_slack_webhook(DEVICE_FAILURE_WEBHOOK, message)
            sleep_duration = error_n * interval
            error_n = (2 * error_n)

        error_n = 1  # reset error sleep interval

        # given that this is a RAM constrained device, let's delete
        # everything and do some garbage collection, watching things
        # on htop the RAM usage was creeping upwards...
        del payload, result, status, pm2, pm10
        gc.collect()

        sleep(sleep_duration)


def send_threshold_alert(pm2, pm10):

    # alerts for now, future plan is to link/hook into an air purifier
    message = (f"{SENSOR_ID} reporting air quality above threshold, ventilate room. PM2_5 level: {pm2}, PM10 level: {pm10} ")  # noqa: E501

    com_utilities.send_slack_webhook(AIR_ALERT_WEBHOOK, message)


def main():

    # instantiate air quality class

    try:
        quality = AirQuality()
        logger.info('Air quality class instantiated successfully')

    except Exception as e:
        message = (f'Air Quality Class failed to instantiate, with error {e}, going to sleep....')  # noqa: E501
        logger.debug(message)
        com_utilities.send_slack_webhook(DEVICE_FAILURE_WEBHOOK, message)
        sleep(1800)

    # Load parameters
    INTERVAL = int(os.environ['INTERVAL'])
    TOPIC = os.environ['TOPIC']

    # Load Environmental Variables
    MQTT_BROKER = os.environ['MQTT_BROKER']
    MQTT_USER = os.environ['MQTT_USER']
    MQTT_SECRET = os.environ['MQTT_SECRET']
    MQTT_PORT = int(os.environ['MQTT_PORT'])

    # get unique client ID
    clientID = com_utilities.getClientID()

    # get mqtt client
    client, code = com_utilities.mqttClient(clientID, MQTT_USER, MQTT_SECRET,
                                            MQTT_BROKER, MQTT_PORT)

    # start data monitoring
    try:
        air(client, quality, TOPIC, INTERVAL)

    finally:
        client.loop_stop()


if __name__ == '__main__':
    main()
