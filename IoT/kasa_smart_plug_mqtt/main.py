# Markham Lee 2023 - 2024
# Finance, Productivity, IoT, & Weather dashboard
# https://github.com/MarkhamLee/finance-productivity-iot-informational-weather-dashboard
# Python script for receiving energy data from a TP Link Kasa TP254
# smart plug and transmitting the data via MQTT
import asyncio
import gc
import json
import os
import sys
from kasa import SmartPlug

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from iot_libraries.logging_util import logger  # noqa: E402
from iot_libraries.communications_utilities\
    import IoTCommunications  # noqa: E402

com_utilities = IoTCommunications()

DEVICE_FAILURE_CHANNEL = os.environ['DEVICE_FAILURE_CHANNEL']
SENSOR_ID = os.environ['SENSOR_ID']


async def get_plug_data(client: object, topic: str,
                        device_ip: str, interval: int):

    device_error_count = 0
    mqtt_error_count = 0

    try:
        plug = SmartPlug(device_ip)
        logger.info(f'Connected to Kasa smart plug at: {device_ip}')

    except Exception as e:
        message = (f"Kasa device: {SENSOR_ID} unavailable with error {e}, going to sleep....")  # noqa: E501
        com_utilities.send_slack_alert(message, DEVICE_FAILURE_CHANNEL)
        # go to sleep for 30 minutes, give device time to be setup
        # and deployed, Kubernetes will just redeploy the container
        # if we exit, so we sleep instead
        asyncio.sleep(1800)

    while True:

        # poll device for update
        try:
            await plug.update()

        except Exception as e:
            message = (f'Kasa plug {SENSOR_ID} connectivity failure with error: {e}')  # noqa: E501
            logger.debug(message)
            device_error_count += 1
            if device_error_count > 36:
                com_utilities.send_slack_alert(message, DEVICE_FAILURE_CHANNEL)
                device_error_count = 0  # reset error count
                asyncio.sleep(1200)  # sleep for 20 minutes
                continue

        # split out data
        payload = {
            "power_usage": plug.emeter_realtime.power,
            "voltage": plug.emeter_realtime.voltage,
            "current": plug.emeter_realtime.current,
            "device_id": plug.device_id
        }

        logger.info(f'Payload ready: {payload}')

        payload = json.dumps(payload)
        result = client.publish(topic, payload)
        status = result[0]

        if status != 0:
            mqtt_error_count += 1
            message = (f'MQTT connection error, failed to publish data for: {SENSOR_ID} to MQTT topic: {topic}, with code: {status}')  # noqa: E501
            logger.debug(message)

            if mqtt_error_count > 36:
                com_utilities.send_slack_alert(message, DEVICE_FAILURE_CHANNEL)
                mqtt_error_count = 0  # reset count interval
                # sleep for 30 minutes, 10 consecutive failures suggests
                # broader network and/or MQTT broker issues.
                asyncio.sleep(1800)

        # clean up RAM, container metrics show RAM usage creeping up daily
        del payload, result, status
        gc.collect()

        # wait 5 seconds
        await asyncio.sleep(interval)  # Sleep some time between updates


def main():

    # Load operating parameters
    INTERVAL = int(os.environ['INTERVAL'])
    DEVICE_IP = os.environ['DEVICE_IP']
    TOPIC = os.environ['TOPIC']

    # Load connection variables
    MQTT_BROKER = os.environ['MQTT_BROKER']
    MQTT_USER = os.environ['MQTT_USER']
    MQTT_SECRET = os.environ['MQTT_SECRET']
    MQTT_PORT = int(os.environ['MQTT_PORT'])

    # get unique client ID
    clientID = com_utilities.getClientID()

    # get mqtt client
    client, code = com_utilities.mqttClient(clientID, MQTT_USER,
                                            MQTT_SECRET, MQTT_BROKER,
                                            MQTT_PORT)

    # start device monitoring
    try:
        asyncio.run(get_plug_data(client, TOPIC, DEVICE_IP, INTERVAL))

    finally:
        client.loop_stop()


if __name__ == "__main__":
    main()
