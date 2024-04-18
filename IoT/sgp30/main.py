# Markham Lee 2023 - 2024
# Finance, Productivity, IoT, & Weather dashboard
# https://github.com/MarkhamLee/finance-productivity-iot-informational-weather-dashboard
# Pulls data from an SPG30 air quality sensor and transmits the data via MQTT
import json
import gc
import os
import sys
from sgp30 import SGP30
from time import sleep


parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from iot_libraries.logging_util import logger  # noqa: E402
from iot_libraries.communications_utilities\
    import IoTCommunications  # noqa: E402

com_utilities = IoTCommunications()
SENSOR_ID = os.environ['SENSOR_ID']


def get_sensor_data(client: object, topic: str, interval: int):

    failure_count = int(os.environ['FAILURE_THRESHOLD'])
    DEVICE_FAILURE_CHANNEL = os.environ['DEVICE_FAILURE_CHANNEL']
    NODE_DEVICE_ID = os.environ['DEVICE_ID']

    air_quality = SGP30()
    logger.info('Connected to SGP30')

    error_count = 0

    while True:

        # replace with
        try:
            air_data = air_quality.get_air_quality()
            total_co2 = air_data.equivalent_co2
            total_voc = air_data.total_voc

            payload = {
                "co2_Levels": total_co2,
                "total_volatile_compounds": total_voc
            }

            payload = json.dumps(payload)
            send_message(client, payload, topic)
            del total_co2, total_voc, air_data, payload
            gc.collect()
            error_count = 0

        except Exception as e:
            error_count += 1
            logger.debug(f'Device read error: {e}, consecutive read error count: {error_count}')  # noqa: E501
            if error_count == failure_count:
                message = (f'Potential device failure on: {NODE_DEVICE_ID}, device connected but non responsive over {failure_count} consecutive attempts')  # noqa: E501
                logger.debug(message)
                com_utilities.send_slack_alert(message, DEVICE_FAILURE_CHANNEL)
                error_count = 0

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
