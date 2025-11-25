# Markham 2023 - 2025
# Internet & IoT Data Platform:
# https://github.com/MarkhamLee/internet-and-iot-data-platform
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

# Load Environmental Variables
AIR_ALERT_WEBHOOK = os.environ['CLIMATE_ALERT_WEBHOOK']
DEVICE_ALERT_WEBHOOK = os.environ['DEVICE_ALERT_WEBHOOK']
ERROR_SLEEP_DURATION = int(os.environ['ERROR_SLEEP_DURATION'])
IOT_PIPELINE_ALERTS = os.environ['IOT_PIPELINE_ALERTS']
DEVICE_ID = os.environ['DEVICE_ID']
SENSOR_ID = os.environ['SENSOR_ID']
INTERVAL = int(os.environ['INTERVAL'])
TOPIC = os.environ['TOPIC']
MQTT_BROKER = os.environ['MQTT_BROKER']
MQTT_USER = os.environ['MQTT_USER']
MQTT_SECRET = os.environ['MQTT_SECRET']
MQTT_PORT = int(os.environ['MQTT_PORT'])
PM2_THRESHOLD = int(os.environ['PM2_THRESHOLD'])
PM10_THRESHOLD = int(os.environ['PM10_THRESHOLD'])


def air(client: object, quality: object, topic: str, interval: int) -> str:

    while True:

        air_data = quality.get_air_quality()

        # checking for errors, actual air data is returned as a tuple
        # while read errors return an integer
        if not isinstance(air_data, tuple):
            logger.info(f'Sensor read error, going to sleep for {ERROR_SLEEP_DURATION} minutes')
            sleep(ERROR_SLEEP_DURATION)
            continue
        
        payload = process_air_quality_data(air_data, client, topic)

        logger.info(f'Sending payload {payload}')
        send_data(payload)

        sleep(interval)


def process_air_quality_data(data):

    pm2, pm10 = data

    if pm2 > PM2_THRESHOLD or pm10 > PM10_THRESHOLD:
        send_threshold_alert(pm2, pm10)

    # prepare payload 
    payload = {
        "pm2": pm2,
        "pm10": pm10
    }

    # convert payload to json for MQTT
    return json.dumps(payload)


def send_threshold_alert(pm2, pm10):

    # alerts for now, future plan is to link/hook into an air purifier
    message = (f"{SENSOR_ID} is reporting air quality above threshold, ventilate room. PM2_5 level: {pm2}, PM10 level: {pm10} ")  # noqa: E501

    com_utilities.send_slack_webhook(AIR_ALERT_WEBHOOK, message)


def send_data(payload: dict, topic, client):

    try: 
        result = client.publish(topic, payload)
        status = result[0]

    except Exception as e:
        message = (f'{DEVICE_ID} Failed to connect to MQTT broker with error: {e}')
        logger.info(message)
        com_utilities.send_slack_webhook(IOT_PIPELINE_ALERTS, message)

    # secondary check, the except only catches connectivity errors, the below
    # catches errors when the broker was available, but publishing to the topic
    # failed.
    if status != 0:
        message = (f'Air quality MQTT publish failure for {DEVICE_ID} to topic: {topic}, with status code: {status}')  # noqa: E501
        logger.debug(message)  # noqa: E501
        com_utilities.send_slack_webhook(IOT_PIPELINE_ALERTS, message)
        
         # for simplicity just use the same duration for sensor and MQTT broker errors
        sleep(ERROR_SLEEP_DURATION)  

def main():

    # instantiate air quality class
    quality = AirQuality()
    logger.info('Air quality class instantiated successfully')

    # get unique client ID
    clientID = com_utilities.getClientID()

    # get mqtt client
    client = com_utilities.mqttClient(clientID,
                                      MQTT_USER,
                                      MQTT_SECRET,
                                      MQTT_BROKER,
                                      MQTT_PORT)

    # start data monitoring
    try:
        air(client, quality, TOPIC, INTERVAL)

    finally:
        client.loop_stop()


if __name__ == '__main__':
    main()
